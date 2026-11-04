"""Score the fixed final comparison after every pooled passage has been judged."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

from evaluation.run_holdout import verify, METHODS
from evaluation.run_metrics import METRICS, read_json, read_jsonl, unique, pair, sha, write_json
from evaluation.score_reranker import score_results


def load_review(root, run_dir, review_dir):
    verify(root, run_dir)
    questions = unique(read_jsonl(root/'heldout-v1/questions.jsonl'), lambda row: row['question_id'], 'heldout question')
    pool = unique(read_jsonl(run_dir/'pool.jsonl'), pair, 'heldout pool')
    qrels = unique(read_jsonl(review_dir/'qrels.jsonl'), pair, 'heldout judgment')
    if not pool or pool.keys() != qrels.keys():
        raise ValueError('Final judgments must cover exactly the entire pool')
    for identity, passage in pool.items():
        judgment = qrels[identity]
        if judgment['text_sha256'] != hashlib.sha256(passage['text'].encode('utf-8')).hexdigest():
            raise ValueError('Final judgment passage hash differs')
        if any(judgment[field] != passage[field] for field in ('document_id', 'start_line', 'end_line')):
            raise ValueError('Final judgment source identity differs')
        grade = judgment['grade']
        if type(grade) is not int or grade not in (0, 1, 2):
            raise ValueError('Invalid final relevance grade')
        if judgment['review_status'] != 'ai_reviewed' or not judgment['rationale'].strip() or not judgment['reviewer'].strip():
            raise ValueError('Missing final AI review metadata')
        excerpt = judgment['support_excerpt']
        if grade and (not isinstance(excerpt, str) or not excerpt.strip() or excerpt not in passage['text']):
            raise ValueError('Positive final judgment needs a verbatim supporting excerpt')
        if not grade and excerpt is not None:
            raise ValueError('Grade-zero judgment cannot have positive evidence')
        if grade and not questions[identity[0]]['answerable']:
            raise ValueError('Positive judgment conflicts with unanswerable label')
    return questions, qrels, read_jsonl(run_dir/'rankings.jsonl')


def summarize(questions, qrels, rankings):
    scored, details = score_results(questions, qrels, rankings)
    return {
        'split': 'test', 'phase': 'final-heldout-v1', 'questions': len(questions),
        'answerable_questions_in_macro_averages': sum(q['answerable'] for q in questions.values()),
        'unanswerable_questions_excluded_from_macro_averages': sum(not q['answerable'] for q in questions.values()),
        'judged_pairs': len(qrels), 'grade_counts': scored['grade_counts'],
        'top_10_judgment_coverage': 1.0, 'methods': scored['methods'],
        'quality_results_used_for_tuning': False,
        'interpretation': 'Fixed prospective same-corpus holdout with AI-authored questions and AI-reviewed pooled judgments. Not independent human gold, full-corpus recall, answer accuracy or unseen-domain generalization.',
    }, details


def render_report(summary, details, metadata):
    count = summary['answerable_questions_in_macro_averages']
    lines = ['# Final held-out retrieval check', '',
        f'The fixed comparison executed all {summary["questions"]} reserved questions after locking implementation, model configuration and input hashes. Quality metrics were calculated only after explicit AI review of all {summary["judged_pairs"]} pooled question/passage pairs. No configuration was selected or tuned using these results.', '',
        f'Macro averages below cover {count} answerable questions. The {summary["unanswerable_questions_excluded_from_macro_averages"]} unanswerable questions have undefined nDCG/recall and are reported separately.', '',
        '| Method | nDCG@10 | MRR@10 >=1 | Direct MRR@10 | P@10 | Pooled recall@10 | Direct first |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for method in METHODS:
        scores = summary['methods'][method]
        values = ' | '.join(f'{scores[name]:.3f}' for name in METRICS)
        lines.append(f'| {method} | {values} | {scores["direct_evidence_at_1_count"]}/{count} |')
    lines += ['', '## Limits and interpretation', '',
        '- This was a prospective holdout for the final configuration. Its questions were created after earlier development findings, on the same previously inspected corpus. Families differ from development questions, but documents and some source passages are shared. Neither independent authorship nor absence of model pretraining contamination is established.',
        '- Codex authored the questions, inspected source documents and performed the passage review, without independent human validation. Candidate review displays omit method, rank and score; this is not an independent or fully blinded evaluation.',
        '- Grade 0 is irrelevant, grade 1 useful supporting context, grade 2 direct evidence for at least one requested component. Direct evidence at rank 1 does not prove complete multi-part answers. nDCG gains are 2^grade-1 with log2(rank+1) discounts. MRR >=1 and grade-2-only MRR are separate.',
        '- Ideal nDCG rankings and recall denominators use this four-method top-10 union. Pooled recall is not exhaustive corpus recall. Chunks overlap and can repeat facts. All returned top-10 passages are judged; no unjudged passage is treated as irrelevant.',
        '- All methods return candidates for the four missing-detail questions. This retrieval check does not generate answers, test citation support or measure abstention behavior.',
        f'- The reranker scored {metadata["scored_pairs"]} pairs. {metadata["truncated_pairs"]} pairs exceeded 512 tokens (maximum {metadata["max_pair_tokens_before_truncation"]}); only passage tails were truncated for scoring, and queries were preserved. Returned passages retain full text.',
        '- Timings below are descriptive CPU measurements, one timed pass per question, with development-only warmup. Query encoding is included in dense timings. Model loading, disk output and review are excluded. No paid API was called.', '',
        '## Timing', '', '| Method | Median query ms |', '|---|---:|']
    for name, field in [('bm25', 'bm25_ms'), ('dense', 'dense_ms'), ('hybrid', 'hybrid_ms'), ('reranked_hybrid', 'reranked_total_ms')]:
        lines.append(f'| {name} | {statistics.median(t[field] for t in metadata["timings"]):.2f} |')
    lines += ['', '## Per-question results', '',
              '| Question | Method | nDCG@10 | Direct MRR@10 | Top-1 grade |',
              '|---|---|---:|---:|---:|']
    for row in details:
        value = 'n/a' if row['ndcg_at_k'] is None else f'{row["ndcg_at_k"]:.3f}'
        lines.append(f'| {row["question_id"]} | {row["method"]} | {value} | {row["direct_mrr_at_k"]:.3f} | {row["top_1_grade"]} |')
    lines += ['', '## Reproduce without model calls', '',
        '`python -m evaluation.run_holdout --verify` replays all rankings from the saved query vectors and reranker logits.',
        '`python -m evaluation.score_holdout --output evaluation/pilot/runs/my-final-metrics` recalculates this report. Use a fresh directory. See evaluation/FINAL_CHECK.md for protocol and inference details.', '',
        'Further choices based on these results make this set development data for those choices. Preserve this run and use a new set for a later final check.', '']
    return '\n'.join(lines)


def run(root, run_dir, review_dir, output):
    root, run_dir, review_dir, output = map(Path, (root, run_dir, review_dir, output))
    output = output.resolve()
    if any(path.resolve().is_relative_to(output) for path in (root, run_dir, review_dir)):
        raise ValueError('Output cannot replace an input directory or its ancestor')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a new empty final-metrics directory')
    questions, qrels, rankings = load_review(root, run_dir, review_dir)
    summary, details = summarize(questions, qrels, rankings)
    inputs = {'run': run_dir/'run.json', 'rankings': run_dir/'rankings.jsonl', 'pool': run_dir/'pool.jsonl',
              'judgments': review_dir/'qrels.jsonl', 'review_protocol': review_dir/'README.md',
              'execution_lock': root.parent/'heldout_execution.json'}
    manifest = {'input_sha256': {name: sha(path) for name, path in inputs.items()},
                'implementation_sha256': {name: sha(Path(__file__).with_name(name)) for name in ('score_holdout.py', 'metrics.py', 'score_reranker.py')},
                'review_status': 'ai_reviewed', 'split': 'test', 'model_calls': 0,
                'quality_results_used_for_tuning': False}
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'summary.json', summary); write_json(output/'per_question.json', details)
    write_json(output/'run.json', manifest)
    (output/'REPORT.md').write_text(render_report(summary, details, read_json(run_dir/'run.json')), encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=Path('evaluation/pilot'))
    parser.add_argument('--run-dir', type=Path, default=Path('evaluation/pilot/runs/heldout-final-v1'))
    parser.add_argument('--review', type=Path, default=Path('evaluation/pilot/heldout-judgments-v1'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.dataset, args.run_dir, args.review, args.output), indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'Final scoring failed: {exc}\n')
