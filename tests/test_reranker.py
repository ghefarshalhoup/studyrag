"""Frozen holdout integrity, reranking boundaries and expanded-pool scoring."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from evaluation.run_metrics import read_json, read_jsonl
from evaluation.run_reranker import rank_scores, verify
from evaluation.score_reranker import load_review, run, score_results
from evaluation.validate_holdout import validate


ROOT = Path(__file__).resolve().parents[1]/'evaluation/pilot'
RERANKER = ROOT/'runs/reranker-v1'
JUDGMENTS = ROOT/'reranker-judgments-v1'


@dataclass(frozen=True)
class Candidate:
    chunk_id: str


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(row)+'\n' for row in rows), encoding='utf-8')


def test_cross_encoder_sort_uses_logits_and_stable_id_ties():
    a, b, c = map(Candidate, ['a', 'b', 'c'])
    ranked = rank_scores([c, b, a], [-9, 2, 2], k=2)
    assert ranked == [(a, 2), (b, 2)]
    assert rank_scores([], []) == []


@pytest.mark.parametrize('scores', [[], [1, 2], [float('nan')], [float('inf')]])
def test_malformed_model_score_arrays_rejected(scores):
    with pytest.raises(ValueError):
        rank_scores([Candidate('a')], scores)


def test_duplicate_candidates_and_invalid_cutoff_rejected():
    with pytest.raises(ValueError, match='Duplicate'):
        rank_scores([Candidate('a'), Candidate('a')], [1, 2])
    with pytest.raises(ValueError, match='positive'):
        rank_scores([], [], k=True)


def test_holdout_is_frozen_source_supported_and_not_run():
    assert validate(ROOT) == {'questions': 16, 'answerable': 12, 'unanswerable': 4,
                              'family_overlap': 0, 'retrieval_calls': 0, 'review_status': 'ai_reviewed'}
    metadata = read_json(RERANKER/'run.json')
    assert metadata['heldout_queries_executed'] == 0
    assert {r['question_id'] for r in read_jsonl(RERANKER/'scores.jsonl')} == {
        q['question_id'] for q in read_jsonl(ROOT/'questions.jsonl')}


@pytest.fixture
def copied_pilot(tmp_path):
    root = tmp_path/'pilot'
    shutil.copytree(ROOT, root)
    shutil.copyfile(ROOT.parent/'reranker_plan.json', tmp_path/'reranker_plan.json')
    return root


def refreeze_questions_for_validation_test(root):
    # Simulate a newly frozen but semantically invalid dataset, so source and
    # family checks are exercised independently of the outer checksum gate.
    frozen = read_json(root/'heldout-v1/freeze.json')
    frozen['questions_sha256'] = hashlib.sha256((root/'heldout-v1/questions.jsonl').read_bytes()).hexdigest()
    (root/'heldout-v1/freeze.json').write_text(json.dumps(frozen))


def test_edited_holdout_question_fails_frozen_hash(copied_pilot):
    path = copied_pilot/'heldout-v1/questions.jsonl'
    path.write_text(path.read_text(encoding='utf-8')+'\n')
    with pytest.raises(ValueError, match='freeze hash'):
        validate(copied_pilot)


def test_frozen_holdout_requires_exact_source_quotes(copied_pilot):
    path = copied_pilot/'heldout-v1/questions.jsonl'
    rows = read_jsonl(path)
    rows[0]['evidence'][0]['quote'] = 'Invented source evidence.'
    write_rows(path, rows)
    refreeze_questions_for_validation_test(copied_pilot)
    with pytest.raises(ValueError, match='quote/offset'):
        validate(copied_pilot)


def test_development_family_cannot_be_reused_in_holdout(copied_pilot):
    path = copied_pilot/'heldout-v1/questions.jsonl'
    rows = read_jsonl(path)
    rows[0]['group_id'] = read_jsonl(copied_pilot/'questions.jsonl')[0]['group_id']
    write_rows(path, rows)
    refreeze_questions_for_validation_test(copied_pilot)
    with pytest.raises(ValueError, match='family overlaps'):
        validate(copied_pilot)


def test_changed_source_and_plan_fail_freeze(copied_pilot):
    path = copied_pilot/'corpus/classes.rst'
    path.write_bytes(path.read_bytes()+b'\n')
    with pytest.raises(ValueError, match='Corpus path/hash'):
        validate(copied_pilot)
    shutil.copyfile(ROOT/'corpus/classes.rst', path)
    plan = copied_pilot.parent/'reranker_plan.json'
    plan.write_bytes(plan.read_bytes()+b'\n')
    with pytest.raises(ValueError, match='freeze hash'):
        validate(copied_pilot)


def test_saved_candidates_and_logits_replay_without_model():
    assert verify(ROOT, ROOT/'runs/bm25-v1', ROOT/'runs/comparison-v1', RERANKER) == {
        'rankings_verified': 800, 'scores_verified': 1000, 'model_calls': 0, 'heldout_queries_executed': 0}


def test_modified_saved_logit_is_detected(tmp_path):
    directory = tmp_path/'reranker'
    shutil.copytree(RERANKER, directory)
    rows = read_jsonl(directory/'scores.jsonl')
    rows[0]['score'] += 1
    write_rows(directory/'scores.jsonl', rows)
    with pytest.raises(ValueError, match='output hash'):
        verify(ROOT, ROOT/'runs/bm25-v1', ROOT/'runs/comparison-v1', directory)


@pytest.fixture
def copied_judgments(tmp_path):
    directory = tmp_path/'judgments'
    shutil.copytree(JUDGMENTS, directory)
    return directory


def test_new_passages_cannot_be_scored_without_review(copied_judgments):
    path = copied_judgments/'qrels.jsonl'
    rows = read_jsonl(path)
    write_rows(path, rows[:-1])
    with pytest.raises(ValueError, match='entire expanded pool'):
        load_review(ROOT, RERANKER, copied_judgments)


def test_original_judgment_cannot_be_changed_during_extension(copied_judgments):
    path = copied_judgments/'qrels.jsonl'
    rows = read_jsonl(path)
    rows[0]['rationale'] = 'Changed during reranker review.'
    write_rows(path, rows)
    with pytest.raises(ValueError, match='Existing reviewed decision'):
        load_review(ROOT, RERANKER, copied_judgments)


def test_new_positive_requires_excerpt_from_its_own_passage(copied_judgments):
    path = copied_judgments/'qrels.jsonl'
    rows = read_jsonl(path)
    positive = next(row for row in rows[384:] if row['grade'] > 0)
    positive['support_excerpt'] = 'This was never in the passage.'
    write_rows(path, rows)
    with pytest.raises(ValueError, match='supporting excerpt'):
        load_review(ROOT, RERANKER, copied_judgments)


def test_pool_expansion_changes_ideal_and_recall_even_without_ranking_changes():
    questions = {'q': {'answerable': True}}
    rankings = [{'question_id': 'q', 'method': method, 'rank': rank, 'chunk_id': str(rank)}
                for method in ('bm25', 'dense', 'hybrid', 'reranked_hybrid') for rank in range(1, 11)]
    qrels = {('q', str(rank)): {'grade': 2 if rank == 1 else 0} for rank in range(1, 11)}
    before, _ = score_results(questions, qrels, rankings)
    qrels['q', 'unretrieved-positive'] = {'grade': 2}
    after, _ = score_results(questions, qrels, rankings)
    assert before['methods']['dense']['ndcg_at_k'] == 1
    assert after['methods']['dense']['ndcg_at_k'] == pytest.approx(1/(1+1/1.584962500721156))
    assert after['methods']['dense']['pooled_recall_at_k'] == .5
    assert after['methods']['dense']['direct_mrr_at_k'] == 1


def test_expanded_metrics_reproduce_every_artifact(tmp_path):
    output = tmp_path/'metrics'
    summary = run(ROOT, RERANKER, JUDGMENTS, output)
    assert summary['judged_pairs'] == 430
    assert summary['top_10_judgment_coverage'] == 1
    saved = ROOT/'runs/reranker-metrics-v1'
    for name in ('summary.json', 'per_question.json', 'run.json', 'REPORT.md'):
        assert (output/name).read_bytes() == (saved/name).read_bytes()
    with pytest.raises(ValueError, match='new empty'):
        run(ROOT, RERANKER, JUDGMENTS, output)
