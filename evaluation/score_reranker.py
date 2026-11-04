"""Compare all four frozen methods on one fully judged expanded dev pool."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics

from evaluation.metrics import score_ranking
from evaluation.run_metrics import METRICS, load_inputs, read_json, read_jsonl, sha, unique, pair, write_json
from evaluation.run_reranker import METHOD, verify


METHODS = ('bm25', 'dense', 'hybrid', METHOD)


def score_results(questions, qrels, rankings):
    grades = defaultdict(dict)
    grouped = defaultdict(list)
    for (qid, cid), judgment in qrels.items():
        grades[qid][cid] = judgment['grade']
    for row in rankings:
        if row['method'] not in METHODS or row['question_id'] not in questions:
            raise ValueError('Unknown method/question')
        grouped[row['question_id'], row['method']].append(row)
    if grouped.keys() != {(qid, method) for qid in questions for method in METHODS}:
        raise ValueError('Incomplete question/method coverage')
    details = []
    for (qid, method), rows in sorted(grouped.items()):
        rows.sort(key=lambda r: r['rank'])
        if [r['rank'] for r in rows] != list(range(1, 11)):
            raise ValueError('Expected exactly ten unique ranks')
        scores = score_ranking([row['chunk_id'] for row in rows], grades[qid])
        if questions[qid]['answerable'] and not scores['relevant_in_pool']:
            raise ValueError('Answerable question has no positive judgments')
        details.append({'question_id': qid, 'method': method, 'answerable': questions[qid]['answerable'],
                        'top_1_grade': grades[qid][rows[0]['chunk_id']], **scores})
    summary = {
        'cutoff': 10, 'questions': len(questions), 'judged_pairs': len(qrels),
        'grade_counts': {str(grade): count for grade, count in sorted(Counter(r['grade'] for r in qrels.values()).items())},
        'answerable_questions_in_macro_averages': sum(q['answerable'] for q in questions.values()),
        'top_10_judgment_coverage': 1.0, 'heldout_queries_executed': 0, 'methods': {},
        'interpretation': 'All four methods rescored on the expanded AI-reviewed development pool. Pooled recall is not exhaustive corpus recall. No held-out or answer-quality result.',
    }
    for method in METHODS:
        included = [d for d in details if d['method'] == method and d['answerable']]
        excluded = [d for d in details if d['method'] == method and not d['answerable']]
        if not included:
            raise ValueError('No answerable questions')
        summary['methods'][method] = {
            **{name: statistics.mean(d[name] for d in included) for name in METRICS},
            'direct_evidence_at_1_count': sum(d['top_1_grade'] == 2 for d in included),
            'direct_evidence_at_10_count': sum(d['direct_mrr_at_k'] > 0 for d in included),
            'unanswerable_queries_returning_candidates': sum(d['returned_at_k'] > 0 for d in excluded),
        }
    return summary, details


def load_review(dataset, reranker, judgments):
    baseline, comparison = dataset/'runs/bm25-v1', dataset/'runs/comparison-v1'
    questions, old_pool, old_qrels, _ = load_inputs(dataset, comparison, dataset/'judgments-v1', baseline)
    verify(dataset, baseline, comparison, reranker)
    pool = unique(read_jsonl(reranker/'pool.jsonl'), pair, 'expanded pool pair')
    qrels = unique(read_jsonl(judgments/'qrels.jsonl'), pair, 'expanded judgment')
    if pool.keys() != qrels.keys():
        raise ValueError('Expanded judgments must cover the entire expanded pool')
    for identity, old in old_qrels.items():
        if qrels.get(identity) != old:
            raise ValueError('Existing reviewed decision was changed')
    chunks = {row['chunk_id']: row for row in read_jsonl(baseline/'chunks.jsonl')}
    for identity, candidate in pool.items():
        qid, cid = identity
        if qid not in questions or cid not in chunks:
            raise ValueError('Unknown source/question in expanded pool')
        source, judgment = chunks[cid], qrels[identity]
        if candidate['text'] != source['text'] or judgment['text_sha256'] != hashlib.sha256(source['text'].encode('utf-8')).hexdigest():
            raise ValueError('Expanded passage text/hash differs')
        for field in ('document_id', 'start_line', 'end_line'):
            if judgment[field] != source[field] or candidate[field] != source[field]:
                raise ValueError('Expanded passage source identity differs')
        grade = judgment['grade']
        if type(grade) is not int or grade not in (0, 1, 2):
            raise ValueError('Invalid expanded grade')
        if judgment['review_status'] != 'ai_reviewed' or not judgment['reviewer'].strip() or not judgment['rationale'].strip():
            raise ValueError('Missing expanded AI review metadata')
        excerpt = judgment['support_excerpt']
        if grade and (not isinstance(excerpt, str) or not excerpt.strip() or excerpt not in source['text']):
            raise ValueError('Missing expanded supporting excerpt')
        if not grade and excerpt is not None:
            raise ValueError('Irrelevant expanded judgment has a positive excerpt')
        if not questions[qid]['answerable'] and grade:
            raise ValueError('Positive evidence contradicts an unanswerable label')
    rankings = read_jsonl(reranker/'rankings.jsonl')
    if {pair(row) for row in rankings} != pool.keys():
        raise ValueError('Expanded pool differs from top-10 union')
    for identity, candidate in pool.items():
        actual = sorted((row['method'], row['rank']) for row in rankings if pair(row) == identity)
        declared = sorted((row['method'], row['rank']) for row in candidate['retrieved_by'])
        if actual != declared:
            raise ValueError('Expanded pool provenance differs')
    return questions, qrels, rankings, len(pool)-len(old_pool)


def render_report(summary, details, run_metadata, added):
    lines = ['# Local reranker: AI-reviewed development comparison', '',
             f'All four methods are rescored on the same expanded pool of {summary["judged_pairs"]} question/passage pairs ({added} newly judged). Original rankings and existing judgments are unchanged. All top-10 results have explicit judgments.', '',
             '| Method | nDCG@10 | MRR@10 >=1 | Direct MRR@10 | P@10 | Pooled recall@10 | Direct top-1 |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for method, scores in summary['methods'].items():
        values = ' | '.join(f'{scores[name]:.3f}' for name in METRICS)
        lines.append(f'| {method} | {values} | {scores["direct_evidence_at_1_count"]}/16 |')
    lines += ['', '## Method and interpretation', '',
        '- The frozen MiniLM cross-encoder scores the fused top 50 candidates from BM25 top 50 plus dense top 50, equal-weight RRF constant 60. The top 10 reranker logits are returned. No query rewrite, answer generation, model training or alternative model trial was used.',
        '- The configuration was frozen before scoring. The 16 prospective held-out questions remain unexecuted; results here concern the original 20 development questions only. All macro averages use the 16 answerable questions.',
        '- nDCG ideal rankings and pooled-recall denominators now include new positives introduced by the fourth method. Therefore these numbers must not be compared directly with the older three-method report. That report remains a historical snapshot.',
        '- Grade 1 is supporting context, grade 2 direct evidence for at least one answer component. MRR >=1 and grade-2-only MRR are separate. nDCG uses gain 2^grade-1 and log2(rank+1) discounts. Precision divides by 10. Pooled recall counts only positives in this four-method top-10 union.',
        '- Judgments are from the same AI that authored questions and saw earlier summaries, without independent human validation. Overlapping chunks can repeat evidence. A direct hit does not establish full multi-part answer coverage, reliable citations or good generated answers.',
        '- Four unanswerable questions have zero positives and undefined nDCG/recall; they are excluded from macro averages. Returning candidates is not a measured abstention failure.',
        f'- Local CPU reranking median: {run_metadata["median_rerank_ms"]:.1f} ms per 50-candidate query. One timed pass per question; excludes first-stage retrieval and model loading. Model loading: {run_metadata["model_load_ms"]:.1f} ms. These timings are descriptive, not a controlled speed comparison with earlier runs.',
        f'- Pair context is limited to 512 tokens. {run_metadata["truncated_pairs"]}/{run_metadata["scored_pairs"]} scored pairs had passage-tail truncation; queries were preserved. Maximum original pair length: {run_metadata["max_pair_tokens_before_truncation"]}. Returned source passages retain their full text. Raw logits are not confidence probabilities.', '',
        '## Per-question scores', '',
        '| Question | Method | nDCG@10 | Direct MRR@10 | Top-1 grade |',
        '|---|---|---:|---:|---:|',
    ]
    for row in details:
        ndcg = 'n/a' if row['ndcg_at_k'] is None else f'{row["ndcg_at_k"]:.3f}'
        lines.append(f'| {row["question_id"]} | {row["method"]} | {ndcg} | {row["direct_mrr_at_k"]:.3f} | {row["top_1_grade"]} |')
    lines += ['', '## Reproduce', '',
        'Replay candidates and logits without a model: `python -m evaluation.run_reranker --verify`.',
        'Recompute metrics: `python -m evaluation.score_reranker --output evaluation/pilot/runs/my-reranker-metrics`.',
        'Use a new output directory. See evaluation/RERANKER.md for the frozen model download, inference command, review protocol and limits.', '']
    return '\n'.join(lines)


def run(dataset, reranker, judgments, output):
    dataset, reranker, judgments, output = map(Path, (dataset, reranker, judgments, output))
    output = output.resolve()
    if any(path.resolve().is_relative_to(output) for path in (dataset, reranker, judgments)):
        raise ValueError('Output cannot replace an input directory or its ancestor')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a new empty metric output directory')
    questions, qrels, rankings, added = load_review(dataset, reranker, judgments)
    summary, details = score_results(questions, qrels, rankings)
    metadata = read_json(reranker/'run.json')
    summary['newly_judged_pairs'] = added
    summary['median_rerank_ms'] = metadata['median_rerank_ms']
    inputs = {'reranker_run': reranker/'run.json', 'rankings': reranker/'rankings.jsonl',
              'pool': reranker/'pool.jsonl', 'judgments': judgments/'qrels.jsonl',
              'review_protocol': judgments/'README.md', 'original_judgments': dataset/'judgments-v1/qrels.jsonl'}
    manifest = {'input_sha256': {name: sha(path) for name, path in inputs.items()},
                'implementation_sha256': {name: sha(Path(__file__).with_name(name)) for name in ('score_reranker.py', 'metrics.py')},
                'model_calls': 0, 'heldout_queries_executed': 0, 'review_status': 'ai_reviewed'}
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'summary.json', summary)
    write_json(output/'per_question.json', details)
    write_json(output/'run.json', manifest)
    (output/'REPORT.md').write_text(render_report(summary, details, metadata, added), encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=Path('evaluation/pilot'))
    parser.add_argument('--reranker', type=Path, default=Path('evaluation/pilot/runs/reranker-v1'))
    parser.add_argument('--judgments', type=Path, default=Path('evaluation/pilot/reranker-judgments-v1'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.dataset, args.reranker, args.judgments, args.output), indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Reranker metrics failed: {exc}\n')
