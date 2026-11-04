"""Analytical metric examples and rejection of incomplete/stale review artifacts."""
import json
import math
from pathlib import Path
import shutil

import pytest

from evaluation.metrics import score_ranking
from evaluation.run_metrics import evaluate, load_inputs, read_jsonl, run


PILOT = Path(__file__).resolve().parents[1] / 'evaluation/pilot'


def test_graded_gain_discount_and_supporting_vs_direct_reciprocal_rank():
    scores = score_ranking(['context', 'irrelevant', 'answer'],
                           {'context': 1, 'irrelevant': 0, 'answer': 2, 'unretrieved': 1}, k=3)
    # Actual DCG = 1/1 + 0/log2(3) + 3/2.
    # Ideal DCG = 3/1 + 1/log2(3) + 1/2, including an unretrieved positive.
    assert scores['ndcg_at_k'] == pytest.approx(2.5 / (3 + 1/math.log2(3) + .5))
    assert scores['mrr_at_k'] == 1
    assert scores['direct_mrr_at_k'] == pytest.approx(1/3)
    assert scores['precision_at_k'] == pytest.approx(2/3)
    assert scores['pooled_recall_at_k'] == pytest.approx(2/3)


def test_short_ranking_uses_fixed_precision_denominator():
    scores = score_ranking(['answer'], {'answer': 2}, k=10)
    assert scores['ndcg_at_k'] == 1
    assert scores['precision_at_k'] == .1
    assert scores['pooled_recall_at_k'] == 1


def test_cutoff_excludes_later_answer_and_unjudged_tail():
    scores = score_ranking(['noise', 'answer', 'unjudged'], {'noise': 0, 'answer': 2}, k=1)
    assert scores['mrr_at_k'] == 0
    assert scores['ndcg_at_k'] == 0
    assert scores['pooled_recall_at_k'] == 0


def test_no_positive_ideal_has_undefined_ndcg_and_recall():
    scores = score_ranking(['noise'], {'noise': 0})
    assert scores['ndcg_at_k'] is None
    assert scores['pooled_recall_at_k'] is None
    assert scores['mrr_at_k'] == scores['direct_mrr_at_k'] == scores['precision_at_k'] == 0


def test_empty_retrieval_with_positive_pool_scores_zero():
    scores = score_ranking([], {'answer': 2})
    assert scores['ndcg_at_k'] == scores['mrr_at_k'] == scores['pooled_recall_at_k'] == 0


@pytest.mark.parametrize('grades', [{'a': True}, {'a': 1.0}, {'a': -1}, {'a': 3}])
def test_invalid_grades_are_not_silently_coerced(grades):
    with pytest.raises(ValueError, match='Grades'):
        score_ranking(['a'], grades)


@pytest.mark.parametrize('k', [True, 0, -1, 1.5])
def test_invalid_cutoff_rejected(k):
    with pytest.raises(ValueError, match='positive integer'):
        score_ranking([], {}, k)


def test_unjudged_and_duplicate_results_are_errors():
    with pytest.raises(ValueError, match='Unjudged'):
        score_ranking(['new'], {'old': 2})
    with pytest.raises(ValueError, match='Duplicate'):
        score_ranking(['a', 'a'], {'a': 2})


def paths(root=PILOT):
    return root, root/'runs/comparison-v1', root/'judgments-v1', root/'runs/bm25-v1'


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')


@pytest.fixture
def edited_judgments(tmp_path):
    directory = tmp_path/'judgments'
    shutil.copytree(PILOT/'judgments-v1', directory)
    rows = read_jsonl(directory/'qrels.jsonl')
    return directory, rows


def test_every_saved_result_has_explicit_source_checked_review():
    questions, pool, qrels, grouped = load_inputs(*paths())
    assert len(pool) == len(qrels) == 384
    assert sum(len(rows) for rows in grouped.values()) == 600
    summary, details = evaluate(questions, qrels, grouped)
    assert summary['answerable_questions_in_macro_averages'] == 16
    assert summary['unanswerable_questions_excluded_from_macro_averages'] == 4
    assert len(details) == 60
    for row in details:
        if not row['answerable']:
            assert row['ndcg_at_k'] is None
            assert row['pooled_recall_at_k'] is None


@pytest.mark.parametrize('mutation,expected', [
    ('missing', 'complete non-empty pool'),
    ('duplicate', 'Duplicate judgment'),
    ('unreviewed', 'review metadata'),
    ('bad_excerpt', 'supporting excerpt'),
    ('changed_text', 'text/hash'),
    ('invalid_grade', 'Invalid grade'),
    ('empty_reason', 'review metadata'),
])
def test_invalid_judgment_artifacts_fail_closed(edited_judgments, mutation, expected):
    directory, rows = edited_judgments
    positive = next(row for row in rows if row['grade'] > 0)
    if mutation == 'missing':
        rows.pop()
    elif mutation == 'duplicate':
        rows.append(rows[0])
    elif mutation == 'unreviewed':
        positive['review_status'] = 'unjudged'
    elif mutation == 'bad_excerpt':
        positive['support_excerpt'] = 'a sentence absent from this source'
    elif mutation == 'changed_text':
        positive['text_sha256'] = '0'*64
    elif mutation == 'invalid_grade':
        positive['grade'] = True
    elif mutation == 'empty_reason':
        positive['rationale'] = '  '
    write_rows(directory/'qrels.jsonl', rows)
    dataset, comparison, _, baseline = paths()
    with pytest.raises(ValueError, match=expected):
        load_inputs(dataset, comparison, directory, baseline)


def test_answerable_pool_without_positives_is_not_silently_dropped():
    questions, _, qrels, grouped = load_inputs(*paths())
    for (qid, _), judgment in qrels.items():
        if qid == 'pilot-001':
            judgment['grade'] = 0
    with pytest.raises(ValueError, match='every answerable question'):
        evaluate(questions, qrels, grouped)


def test_duplicate_rank_and_new_unjudged_result_rejected(tmp_path):
    dataset, comparison, judgments, baseline = paths()
    edited = tmp_path/'comparison'
    edited.mkdir()
    for name in ('rankings.jsonl', 'pool.jsonl', 'run.json'):
        shutil.copyfile(comparison/name, edited/name)
    rows = read_jsonl(edited/'rankings.jsonl')
    rows[1]['rank'] = rows[0]['rank']
    write_rows(edited/'rankings.jsonl', rows)
    with pytest.raises(ValueError, match='exactly ranks'):
        load_inputs(dataset, edited, judgments, baseline)
    rows = read_jsonl(comparison/'rankings.jsonl')
    rows[0]['chunk_id'] = 'unjudged-new-chunk'
    write_rows(edited/'rankings.jsonl', rows)
    with pytest.raises(ValueError, match='unjudged ranking'):
        load_inputs(dataset, edited, judgments, baseline)


def test_report_reproduces_saved_artifacts_without_a_model(tmp_path):
    summary = run(*paths(), tmp_path/'metrics')
    saved = PILOT/'runs/metrics-v1'
    assert summary == json.loads((saved/'summary.json').read_text())
    for name in ('summary.json', 'per_question.json', 'REPORT.md', 'run.json'):
        assert (tmp_path/'metrics'/name).read_bytes() == (saved/name).read_bytes()
    with pytest.raises(ValueError, match='not empty'):
        run(*paths(), tmp_path/'metrics')
    with pytest.raises(ValueError, match='input directory'):
        run(*paths(), PILOT)
