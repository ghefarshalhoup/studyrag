"""Final-check execution gates, common-pool metrics and saved-artifact replay."""
from dataclasses import dataclass
import json
from pathlib import Path
import shutil

import pytest

from evaluation.keyword import Chunk
from evaluation.run_holdout import record_rankings, retrieve, validate_lock, verify
from evaluation.run_metrics import read_json, read_jsonl
from evaluation.score_holdout import load_review, summarize, run


ROOT = Path(__file__).resolve().parents[1]/'evaluation/pilot'
RUN = ROOT/'runs/heldout-final-v1'
REVIEW = ROOT/'heldout-judgments-v1'
ARTIFACTS = not (RUN/'run.json').exists()


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(row)+'\n' for row in rows), encoding='utf-8')


def test_all_methods_keep_source_identity_and_share_one_review_pair():
    chunk = Chunk('id', 'source', 'hash', 'source.rst', 0, 4, 1, 1, 'text')
    pool = {}
    rows = record_rankings('heldout-001', [('bm25', [(chunk, 3)]), ('dense', [(chunk, .8)])], pool)
    assert len(rows) == 2 and len(pool) == 1
    assert rows[0]['start_line'] == 1 and rows[0]['document_id'] == 'source'
    assert pool['heldout-001', 'id']['retrieved_by'] == [{'method': 'bm25', 'rank': 1}, {'method': 'dense', 'rank': 1}]


def test_candidates_use_top50_and_fixed_rrf_without_scores_from_labels():
    a = Chunk('a', 'source', 'hash', 'source.rst', 0, 4, 1, 1, 'a')
    b = Chunk('b', 'source', 'hash', 'source.rst', 0, 4, 1, 1, 'b')
    class Lexical:
        def search(self, query, k):
            assert query == 'question' and k == 50
            return [(a, 1000), (b, 1)]
    class Dense:
        def search(self, vector, k):
            assert vector == [1, 0] and k == 50
            return [(b, .9), (a, .8)]
    _, _, fused = retrieve(Lexical(), Dense(), 'question', [1, 0])
    assert [chunk.chunk_id for chunk, _ in fused] == ['a', 'b']
    assert fused[0][1] == pytest.approx(1/61+1/62)


def test_final_summary_does_not_inherit_development_metadata():
    questions = {'answerable': {'answerable': True}, 'missing': {'answerable': False}}
    qrels = {(qid, str(rank)): {'grade': 2 if qid == 'answerable' and rank == 1 else 0}
             for qid in questions for rank in range(1, 11)}
    rankings = [{'question_id': qid, 'method': method, 'rank': rank, 'chunk_id': str(rank)}
                for qid in questions for method in ('bm25', 'dense', 'hybrid', 'reranked_hybrid')
                for rank in range(1, 11)]
    summary, details = summarize(questions, qrels, rankings)
    assert summary['split'] == 'test'
    assert summary['phase'] == 'final-heldout-v1'
    assert summary['answerable_questions_in_macro_averages'] == 1
    assert summary['unanswerable_questions_excluded_from_macro_averages'] == 1
    assert 'heldout_queries_executed' not in summary
    assert summary['methods']['dense']['ndcg_at_k'] == 1
    assert all(d['ndcg_at_k'] is None for d in details if not d['answerable'])


@pytest.mark.skipif(ARTIFACTS, reason='Final inference artifacts not created yet')
def test_final_run_replays_without_model_or_new_inference():
    result = verify(ROOT, RUN)
    assert result['questions'] == 16
    assert result['ranked_results_verified'] == 640
    assert result['reranker_scores_verified'] == 800
    assert result['model_calls'] == 0
    metadata = read_json(RUN/'run.json')
    assert metadata['heldout_queries_executed'] == metadata['query_embedding_calls'] == 16
    assert metadata['quality_results_used_for_tuning'] is False


@pytest.mark.skipif(ARTIFACTS, reason='Final inference artifacts not created yet')
def test_changed_final_logit_is_detected(tmp_path):
    directory = tmp_path/'run'
    shutil.copytree(RUN, directory)
    rows = read_jsonl(directory/'scores.jsonl')
    rows[0]['score'] += .5
    write_rows(directory/'scores.jsonl', rows)
    with pytest.raises(ValueError, match='output hash mismatch'):
        verify(ROOT, directory)


@pytest.mark.skipif(not (REVIEW/'qrels.jsonl').exists(), reason='Final passage review not created yet')
def test_missing_final_judgment_cannot_be_silently_negative(tmp_path):
    directory = tmp_path/'review'
    shutil.copytree(REVIEW, directory)
    rows = read_jsonl(directory/'qrels.jsonl')
    write_rows(directory/'qrels.jsonl', rows[:-1])
    with pytest.raises(ValueError, match='exactly the entire pool'):
        load_review(ROOT, RUN, directory)


@pytest.mark.skipif(not (REVIEW/'qrels.jsonl').exists(), reason='Final passage review not created yet')
def test_invalid_final_excerpt_is_rejected(tmp_path):
    directory = tmp_path/'review'
    shutil.copytree(REVIEW, directory)
    rows = read_jsonl(directory/'qrels.jsonl')
    positive = next(row for row in rows if row['grade'] > 0)
    positive['support_excerpt'] = 'This statement is not in the source.'
    write_rows(directory/'qrels.jsonl', rows)
    with pytest.raises(ValueError, match='verbatim supporting excerpt'):
        load_review(ROOT, RUN, directory)


@pytest.mark.skipif(not (ROOT.parent/'heldout_execution.json').exists(), reason='Execution lock not created yet')
def test_final_execution_checks_its_code_and_input_hashes():
    lock = validate_lock(ROOT)
    assert lock['phase'] == 'final-heldout-v1'
    assert 'run_holdout.py' in lock['implementation_sha256']
    assert 'score_holdout.py' in lock['implementation_sha256']


@pytest.mark.skipif(not (ROOT/'runs/heldout-metrics-v1/run.json').exists(), reason='Final metric artifacts not created yet')
def test_final_metrics_reproduce_exactly(tmp_path):
    output = tmp_path/'metrics'
    run(ROOT, RUN, REVIEW, output)
    saved = ROOT/'runs/heldout-metrics-v1'
    for name in ('summary.json', 'per_question.json', 'run.json', 'REPORT.md'):
        assert (output/name).read_bytes() == (saved/name).read_bytes()
    with pytest.raises(ValueError, match='new empty'):
        run(ROOT, RUN, REVIEW, output)
