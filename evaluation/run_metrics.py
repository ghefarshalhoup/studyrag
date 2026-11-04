"""Score frozen rankings against AI-reviewed pooled passage judgments.

Run: python -m evaluation.run_metrics --output evaluation/pilot/runs/my-metrics
Uses the standard library only; does not load embeddings or generate answers.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics

from evaluation.metrics import score_ranking


METHODS = ('bm25', 'dense', 'hybrid')
METRICS = ('ndcg_at_k', 'mrr_at_k', 'direct_mrr_at_k',
           'precision_at_k', 'pooled_recall_at_k')
K = 10


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines()
            if line.strip()]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def unique(rows, key, label):
    indexed = {}
    for row in rows:
        identity = key(row)
        if identity in indexed:
            raise ValueError(f'Duplicate {label}: {identity}')
        indexed[identity] = row
    return indexed


def pair(row):
    return row['question_id'], row['chunk_id']


def load_inputs(dataset, comparison, judgments, baseline):
    """Fail closed on stale text, partial judgments or incomplete run coverage."""
    questions = unique(read_jsonl(dataset/'questions.jsonl'), lambda q: q['question_id'], 'question')
    chunks = unique(read_jsonl(baseline/'chunks.jsonl'), lambda c: c['chunk_id'], 'chunk')
    pool = unique(read_jsonl(comparison/'pool.jsonl'), pair, 'pool pair')
    qrels = unique(read_jsonl(judgments/'qrels.jsonl'), pair, 'judgment')
    rankings = read_jsonl(comparison/'rankings.jsonl')
    metadata = read_json(comparison/'run.json')
    baseline_metadata = read_json(baseline/'run.json')
    for key, path in {
        'questions_sha256': dataset/'questions.jsonl',
        'manifest_sha256': dataset/'corpus_manifest.json',
        'baseline_chunks_sha256': baseline/'chunks.jsonl',
        'baseline_run_sha256': baseline/'run.json',
    }.items():
        if sha(path) != metadata[key]:
            raise ValueError(f'Frozen input hash mismatch: {key}')
    if baseline_metadata['questions_sha256'] != sha(dataset/'questions.jsonl'):
        raise ValueError('Baseline question hash mismatch')
    manifest = read_json(dataset/'corpus_manifest.json')
    for document in manifest['documents']:
        source = (dataset/document['path']).resolve()
        if not source.is_relative_to(dataset.resolve()):
            raise ValueError('Corpus path escapes dataset')
        if sha(source) != document['sha256']:
            raise ValueError(f'Corpus hash mismatch: {document["document_id"]}')
    if not questions or not pool or pool.keys() != qrels.keys():
        raise ValueError('Judgments must cover exactly the complete non-empty pool')
    if any(q['split'] != 'dev' or type(q['answerable']) is not bool for q in questions.values()):
        raise ValueError('This report requires explicitly answerable/unanswerable development questions')
    for identity, candidate in pool.items():
        qid, cid = identity
        if qid not in questions or cid not in chunks:
            raise ValueError(f'Unknown question or chunk: {identity}')
        chunk = chunks[cid]
        judgment = qrels[identity]
        for field in ('document_id', 'start_line', 'end_line'):
            if candidate[field] != chunk[field] or judgment[field] != chunk[field]:
                raise ValueError(f'Source identity mismatch: {identity}/{field}')
        digest = hashlib.sha256(candidate['text'].encode('utf-8')).hexdigest()
        if candidate['text'] != chunk['text'] or judgment['text_sha256'] != digest:
            raise ValueError(f'Passage text/hash mismatch: {identity}')
        grade = judgment['grade']
        if type(grade) is not int or grade not in (0, 1, 2):
            raise ValueError(f'Invalid grade: {identity}')
        if judgment['review_status'] != 'ai_reviewed' or not judgment['reviewer'].strip() or not judgment['rationale'].strip():
            raise ValueError(f'Missing AI review metadata: {identity}')
        excerpt = judgment['support_excerpt']
        if grade and (not isinstance(excerpt, str) or not excerpt.strip() or excerpt not in candidate['text']):
            raise ValueError(f'Missing or invalid supporting excerpt: {identity}')
        if not grade and excerpt is not None:
            raise ValueError(f'Irrelevant passage cannot have a supporting excerpt: {identity}')
        if not questions[qid]['answerable'] and grade:
            raise ValueError(f'Positive judgment contradicts unanswerable label: {identity}')
    grouped = defaultdict(list)
    for row in rankings:
        if pair(row) not in pool or row['method'] not in METHODS:
            raise ValueError('Unknown method or unjudged ranking result')
        if type(row['rank']) is not int or row['rank'] < 1:
            raise ValueError('Invalid rank')
        if type(row['score']) not in (float, int) or not math.isfinite(row['score']):
            raise ValueError('Invalid retrieval score')
        candidate = pool[pair(row)]
        if any(row[field] != candidate[field] for field in ('document_id', 'start_line', 'end_line')):
            raise ValueError('Ranking source identity differs from pool')
        grouped[row['question_id'], row['method']].append(row)
    expected = {(qid, method) for qid in questions for method in METHODS}
    if grouped.keys() != expected:
        raise ValueError('Incomplete question/method ranking coverage')
    for key, rows in grouped.items():
        rows.sort(key=lambda r: r['rank'])
        if [r['rank'] for r in rows] != list(range(1, K+1)):
            raise ValueError(f'Expected exactly ranks 1..{K}: {key}')
        if len({r['chunk_id'] for r in rows}) != K:
            raise ValueError(f'Duplicate result in ranking: {key}')
    if {pair(row) for row in rankings} != pool.keys():
        raise ValueError('Pool differs from union of ranked results')
    # Keep method provenance consistent with the frozen top-10 union.
    for identity, candidate in pool.items():
        actual = sorted((r['method'], r['rank']) for r in rankings if pair(r) == identity)
        declared = sorted((r['method'], r['rank']) for r in candidate['retrieved_by'])
        if actual != declared:
            raise ValueError(f'Pool retrieval provenance mismatch: {identity}')
    return questions, pool, qrels, grouped


def evaluate(questions, qrels, grouped):
    by_question = defaultdict(dict)
    for (qid, cid), judgment in qrels.items():
        by_question[qid][cid] = judgment['grade']
    details = []
    for qid, question in questions.items():
        for method in METHODS:
            ranking = grouped[qid, method]
            scores = score_ranking([r['chunk_id'] for r in ranking], by_question[qid], K)
            details.append({'question_id': qid, 'method': method,
                            'answerable': question['answerable'], **scores,
                            'top_1_grade': by_question[qid][ranking[0]['chunk_id']]})
    answerable_ids = [qid for qid, q in questions.items() if q['answerable']]
    missing = [qid for qid in answerable_ids if not any(by_question[qid].values())]
    if not answerable_ids or missing:
        raise ValueError(f'Cannot average nDCG/recall without positive judgments for every answerable question: {missing}')
    summary = {
        'cutoff': K, 'questions': len(questions),
        'answerable_questions_in_macro_averages': len(answerable_ids),
        'unanswerable_questions_excluded_from_macro_averages': len(questions)-len(answerable_ids),
        'judged_pairs': len(qrels),
        'grade_counts': {str(grade): count for grade, count in
                         sorted(Counter(r['grade'] for r in qrels.values()).items())},
        'top_10_judgment_coverage': 1.0,
        'interpretation': 'AI-reviewed pooled development ranking metrics; not human gold, exhaustive corpus recall, answer quality or held-out performance.',
        'methods': {},
    }
    for method in METHODS:
        included = [d for d in details if d['method'] == method and d['answerable']]
        excluded = [d for d in details if d['method'] == method and not d['answerable']]
        summary['methods'][method] = {
            **{name: statistics.mean(d[name] for d in included) for name in METRICS},
            'direct_evidence_at_1_count': sum(d['top_1_grade'] == 2 for d in included),
            'direct_evidence_at_10_count': sum(d['direct_mrr_at_k'] > 0 for d in included),
            'unanswerable_queries_returning_candidates': sum(d['returned_at_k'] > 0 for d in excluded),
            'unanswerable_candidates_with_positive_grade': sum(d['precision_at_k']*K for d in excluded),
        }
    return summary, details


def render_report(summary, details):
    lines = [
        '# AI-reviewed pooled development ranking metrics', '',
        'These scores use the saved BM25, dense and hybrid top-10 rankings. Retrieval was not rerun or tuned during this review. No answer generation or paid API was used.', '',
        f'{summary["judged_pairs"]} unique question/passage pairs were judged. All top-10 results are covered. Macro averages below include only the {summary["answerable_questions_in_macro_averages"]} answerable development questions.', '',
        '| Method | nDCG@10 | MRR@10 (grade >=1) | Direct MRR@10 (grade 2) | P@10 | Pooled recall@10 | Direct evidence at 1 |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for method, scores in summary['methods'].items():
        values = ' | '.join(f'{scores[name]:.3f}' for name in METRICS)
        lines.append(f'| {method} | {values} | {scores["direct_evidence_at_1_count"]}/{summary["answerable_questions_in_macro_averages"]} |')
    lines += ['', '## Definitions and limits', '',
        '- Grade 0: irrelevant; grade 1: useful supporting context; grade 2: direct evidence for at least one requested answer component. A grade-2 hit does not establish a complete multi-part answer.',
        '- nDCG@10 uses gain 2^grade - 1, discount log2(rank + 1), and an ideal ranking drawn from the judged pool for that question.',
        '- MRR@10 uses the first grade >=1 result. Direct MRR@10 requires grade 2, making the difference between background and direct answers visible.',
        '- Precision@10 uses a denominator of 10. Pooled recall@10 divides retrieved positives by positives in the union of these three methods\' top 10, not by all relevant passages in the corpus. New methods must have their new results judged before comparison.',
        '- Four questions labeled unanswerable have no positive judgments. Their nDCG and recall are undefined and they are excluded from all macro averages. All three methods still returned ten candidates for each. This experiment does not test answer abstention.',
        '- Chunks overlap and are not independent evidence units. Multiple chunks can support the same fact; passage recall and nDCG are sensitive to this duplication. The earlier source-span coverage diagnostics remain available separately.',
        '- Codex drafted the questions, previously inspected run summaries, and performed this review. These judgments have no independent human validation. Candidate displays omitted methods, ranks and scores, but this was not a blinded or independent evaluation.',
        '- All 20 questions are development data from one small English Python corpus; no held-out generalization or statistical superiority is claimed. These are retrieval metrics, not generated-answer or citation accuracy.', '',
        '## Per-question ranking quality', '',
        '| Question | Method | nDCG@10 | MRR@10 | Direct MRR@10 | Pooled recall@10 | Top-1 grade |',
        '|---|---|---:|---:|---:|---:|---:|',
    ]
    for row in details:
        def fmt(value):
            return 'n/a' if value is None else f'{value:.3f}'
        values = ' | '.join(fmt(row[name]) for name in ('ndcg_at_k', 'mrr_at_k', 'direct_mrr_at_k', 'pooled_recall_at_k'))
        lines.append(f'| {row["question_id"]} | {row["method"]} | {values} | {row["top_1_grade"]} |')
    return '\n'.join(lines) + '\n'


def run(dataset, comparison, judgments, baseline, output):
    dataset, comparison, judgments, baseline, output = map(Path, (dataset, comparison, judgments, baseline, output))
    output = output.resolve()
    protected = (dataset, comparison, judgments, baseline)
    if any(path.resolve().is_relative_to(output) for path in protected):
        raise ValueError('Output cannot be an input directory or its ancestor')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory is not empty; use a new directory')
    questions, pool, qrels, grouped = load_inputs(dataset, comparison, judgments, baseline)
    summary, details = evaluate(questions, qrels, grouped)
    inputs = {
        'questions': dataset/'questions.jsonl',
        'manifest': dataset/'corpus_manifest.json',
        'chunks': baseline/'chunks.jsonl',
        'pool': comparison/'pool.jsonl',
        'rankings': comparison/'rankings.jsonl',
        'comparison_run': comparison/'run.json',
        'qrels': judgments/'qrels.jsonl',
        'review_protocol': judgments/'README.md',
    }
    metadata = {
        'metrics_version': 'pooled-graded-v1',
        'review_status': 'ai_reviewed', 'cutoff': K,
        'gain': '2**grade - 1', 'discount': 'log2(rank + 1)',
        'mrr_relevance_threshold': 1, 'direct_mrr_relevance_threshold': 2,
        'macro_population': 'answerable development questions only',
        'recall_denominator': 'positive judged chunks in top-10 union of bm25/dense/hybrid',
        'overlapping_chunks_deduplicated': False,
        'input_sha256': {name: sha(path) for name, path in inputs.items()},
        'implementation_sha256': {name: sha(Path(__file__).with_name(name))
                                  for name in ('metrics.py', 'run_metrics.py')},
        'model_calls': 0,
    }
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'summary.json', summary)
    write_json(output/'per_question.json', details)
    write_json(output/'run.json', metadata)
    (output/'REPORT.md').write_text(render_report(summary, details), encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=Path('evaluation/pilot'))
    parser.add_argument('--baseline', type=Path, default=Path('evaluation/pilot/runs/bm25-v1'))
    parser.add_argument('--comparison', type=Path, default=Path('evaluation/pilot/runs/comparison-v1'))
    parser.add_argument('--judgments', type=Path, default=Path('evaluation/pilot/judgments-v1'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.dataset, args.comparison, args.judgments, args.baseline, args.output), indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Metrics failed: {exc}\n')
