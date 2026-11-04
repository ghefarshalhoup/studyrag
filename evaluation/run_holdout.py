"""Execute the locked final retrieval check, or replay its saved vectors/logits."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import statistics
import time

import numpy as np

from evaluation.fetch_embedding_model import verify_model
from evaluation.keyword import BM25
from evaluation.run_comparison import QUERY_PREFIX, frozen_inputs
from evaluation.run_metrics import read_json, read_jsonl, sha, unique, pair, write_json
from evaluation.run_reranker import rank_scores, write_jsonl, verify as verify_development
from evaluation.semantic import DenseIndex, reciprocal_rank_fusion
from evaluation.validate_holdout import validate as validate_holdout


METHODS = ('bm25', 'dense', 'hybrid', 'reranked_hybrid')
CODE = ('run_holdout.py', 'score_holdout.py', 'keyword.py', 'semantic.py',
        'metrics.py', 'run_comparison.py', 'run_reranker.py', 'score_reranker.py',
        'fetch_embedding_model.py', 'validate_holdout.py', 'run_metrics.py',
        'verify_comparison.py', 'pilot/validate_dataset.py')


def input_paths(root):
    return {
        'questions': root/'heldout-v1/questions.jsonl', 'question_freeze': root/'heldout-v1/freeze.json',
        'corpus_manifest': root/'corpus_manifest.json', 'chunks': root/'runs/bm25-v1/chunks.jsonl',
        'baseline_run': root/'runs/bm25-v1/run.json', 'comparison_run': root/'runs/comparison-v1/run.json',
        'document_vectors': root/'runs/comparison-v1/embeddings.npz',
        'development_reranker_run': root/'runs/reranker-v1/run.json',
        'retrieval_plan': root.parent/'reranker_plan.json',
        'embedding_spec': root.parent/'embedding_model.json',
        'reranker_spec': root.parent/'reranker_model.json',
    }


def execution_lock(root):
    """Write once, before final inference; no model/quality result is read."""
    root = Path(root)
    path = root.parent/'heldout_execution.json'
    if path.exists():
        raise ValueError('Execution lock already exists; do not silently replace it')
    validate_holdout(root)
    verify_development(root, root/'runs/bm25-v1', root/'runs/comparison-v1', root/'runs/reranker-v1')
    lock = {
        'phase': 'final-heldout-v1', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'input_sha256': {name: sha(path) for name, path in input_paths(root).items()},
        'implementation_sha256': {name: sha(Path(__file__).parent/name) for name in CODE},
        'configuration': read_json(root.parent/'reranker_plan.json'),
        'embedding_query_prefix': QUERY_PREFIX,
        'corpus_policy': 'Reuse the original document vectors and chunks; encode only the 16 new queries.',
        'warmup_policy': 'Use the first development question for embedding and eight reranker pairs; no heldout warmup.',
        'timing_policy': 'One timed retrieval/rerank pass per heldout question; model loading and initial warmup excluded.',
        'review_policy': 'Pool all four top-10 rankings; explicit AI grades with source excerpts before scoring. No unjudged-as-zero.',
        'metrics_policy': 'Same graded nDCG, MRR, direct MRR, P@10 and pooled recall as development; macro-average answerable questions only.',
        'selection_policy': 'Report all four fixed methods, including regressions; no model, threshold, prompt, depth or weight tuning on these results.',
    }
    write_json(path, lock)
    return lock


def validate_lock(root):
    validate_holdout(root)
    lock = read_json(root.parent/'heldout_execution.json')
    for name, path in input_paths(root).items():
        if sha(path) != lock['input_sha256'][name]:
            raise ValueError(f'Final execution input changed: {name}')
    for name, digest in lock['implementation_sha256'].items():
        if sha(Path(__file__).parent/name) != digest:
            raise ValueError(f'Final implementation changed: {name}')
    if lock['phase'] != 'final-heldout-v1' or lock['embedding_query_prefix'] != QUERY_PREFIX:
        raise ValueError('Unsupported final execution lock')
    return lock


def load_frozen(root):
    chunks, dev, _ = frozen_inputs(root, root/'runs/bm25-v1')
    questions = read_jsonl(root/'heldout-v1/questions.jsonl')
    metadata = read_json(root/'runs/comparison-v1/run.json')
    with np.load(root/'runs/comparison-v1/embeddings.npz', allow_pickle=False) as arrays:
        documents, dev_vectors = arrays['documents'], arrays['queries']
    if metadata['chunk_ids_in_vector_order'] != [c.chunk_id for c in chunks]:
        raise ValueError('Document-vector identities differ')
    if documents.shape != (len(chunks), metadata['dimension']) or not np.isfinite(documents).all():
        raise ValueError('Invalid frozen document vectors')
    if any(q['split'] != 'test' for q in questions):
        raise ValueError('Final runner requires test questions')
    return chunks, questions, documents, dev[0], dev_vectors[0]


def retrieve(bm25, dense, query, vector):
    lexical = bm25.search(query, 50)
    semantic = dense.search(vector, 50)
    fused = reciprocal_rank_fusion([lexical, semantic], k=50, constant=60)
    return lexical, semantic, fused


def record_rankings(qid, named_rankings, pool):
    rows = []
    for method, ranking in named_rankings:
        for rank, (chunk, score) in enumerate(ranking[:10], 1):
            rows.append({'question_id': qid, 'method': method, 'rank': rank, 'score': float(score),
                         'chunk_id': chunk.chunk_id, 'document_id': chunk.document_id,
                         'start_line': chunk.start_line, 'end_line': chunk.end_line})
            candidate = pool.setdefault((qid, chunk.chunk_id), {
                'question_id': qid, 'chunk_id': chunk.chunk_id, 'document_id': chunk.document_id,
                'start_line': chunk.start_line, 'end_line': chunk.end_line, 'text': chunk.text,
                'retrieved_by': [], 'judgment': 'unjudged'})
            candidate['retrieved_by'].append({'method': method, 'rank': rank})
    return rows


def run(root, embedding_dir, reranker_dir, output):
    root, embedding_dir, reranker_dir = map(Path, (root, embedding_dir, reranker_dir))
    output = Path(output).resolve()
    if any(path.resolve().is_relative_to(output) for path in (root, embedding_dir, reranker_dir)):
        raise ValueError('Output cannot replace an input directory or its ancestor')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a new empty final-run directory')
    lock = validate_lock(root)
    chunks, questions, documents, warmup_question, warmup_vector = load_frozen(root)
    plan = lock['configuration']
    bge_spec = read_json(root.parent/'embedding_model.json')
    reranker_spec = read_json(root.parent/'reranker_model.json')
    verify_model(embedding_dir, bge_spec); verify_model(reranker_dir, reranker_spec)
    from fastembed import TextEmbedding
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    from tokenizers import Tokenizer
    query_tokenizer = Tokenizer.from_file(str(embedding_dir/'tokenizer.json'))
    query_tokenizer.no_truncation(); query_tokenizer.no_padding()
    pair_tokenizer = Tokenizer.from_file(str(reranker_dir/'tokenizer.json'))
    pair_tokenizer.no_truncation(); pair_tokenizer.no_padding()
    if max(len(q.ids) for q in query_tokenizer.encode_batch([QUERY_PREFIX+q['question'] for q in questions])) > 512:
        raise ValueError('Embedding query would be truncated')
    if any(len(pair_tokenizer.encode(q['question']).ids)+1 >= 512 for q in questions):
        raise ValueError('Reranker query would be truncated')
    start = time.perf_counter_ns()
    embedding = TextEmbedding(model_name=bge_spec['model_name'], specific_model_path=str(embedding_dir.resolve()),
                              local_files_only=True, providers=[plan['provider']], threads=plan['threads'],
                              cache_dir=str(embedding_dir/'runtime-cache'))
    reranker = TextCrossEncoder(model_name=reranker_spec['model_name'], specific_model_path=str(reranker_dir.resolve()),
                                local_files_only=True, providers=[plan['provider']], threads=plan['threads'],
                                cache_dir=str(reranker_dir/'runtime-cache'))
    model_load_ms = (time.perf_counter_ns()-start)/1e6
    reranker.model.tokenizer.enable_truncation(max_length=512, strategy='only_second', direction='right')
    bm25, dense = BM25(chunks), DenseIndex(chunks, documents)
    def encode(query):
        return np.asarray(next(iter(embedding.query_embed(QUERY_PREFIX+query))), dtype=np.float32)
    encode(warmup_question['question'])
    warm = retrieve(bm25, dense, warmup_question['question'], warmup_vector)[2][:plan['warmup_pairs']]
    list(reranker.rerank(warmup_question['question'], [c.text for c, _ in warm], batch_size=plan['batch_size']))
    rankings, candidates, scores, vectors, timings, pool = [], [], [], [], [], {}
    for q in questions:
        qid, query = q['question_id'], q['question']
        start = time.perf_counter_ns(); lexical = bm25.search(query, 50)
        lexical_ms = (time.perf_counter_ns()-start)/1e6
        start = time.perf_counter_ns(); vector = encode(query); semantic = dense.search(vector, 50)
        dense_ms = (time.perf_counter_ns()-start)/1e6
        start = time.perf_counter_ns(); fused = reciprocal_rank_fusion([lexical, semantic], k=50, constant=60)
        fusion_ms = (time.perf_counter_ns()-start)/1e6
        selected = [c for c, _ in fused]
        lengths = [len(tokens.ids) for tokens in pair_tokenizer.encode_batch([(query, c.text) for c in selected])]
        start = time.perf_counter_ns()
        logits = list(reranker.rerank(query, [c.text for c in selected], batch_size=plan['batch_size']))
        reranked = rank_scores(selected, logits)
        rerank_ms = (time.perf_counter_ns()-start)/1e6
        vectors.append(vector)
        timings.append({'question_id': qid, 'bm25_ms': lexical_ms, 'dense_ms': dense_ms,
                        'hybrid_ms': lexical_ms+dense_ms+fusion_ms, 'rerank_only_ms': rerank_ms,
                        'reranked_total_ms': lexical_ms+dense_ms+fusion_ms+rerank_ms})
        for method, ranked in [('bm25', lexical), ('dense', semantic), ('hybrid', fused)]:
            candidates.extend({'question_id': qid, 'method': method, 'rank': rank,
                               'chunk_id': chunk.chunk_id, 'score': score}
                              for rank, (chunk, score) in enumerate(ranked, 1))
        scores.extend({'question_id': qid, 'candidate_rank': rank, 'chunk_id': chunk.chunk_id,
                       'score': float(score), 'pair_tokens_before_truncation': length, 'passage_truncated': length > 512}
                      for rank, (chunk, score, length) in enumerate(zip(selected, logits, lengths), 1))
        rankings.extend(record_rankings(qid, [('bm25', lexical), ('dense', semantic), ('hybrid', fused),
                                               ('reranked_hybrid', reranked)], pool))
        print('Final check:', qid, f'rerank {rerank_ms:.0f} ms', flush=True)
    output.mkdir(parents=True, exist_ok=True)
    write_jsonl(output/'rankings.jsonl', rankings); write_jsonl(output/'candidate_rankings.jsonl', candidates)
    write_jsonl(output/'scores.jsonl', scores); write_jsonl(output/'pool.jsonl', list(pool.values()))
    np.savez_compressed(output/'query_vectors.npz', queries=np.asarray(vectors, dtype=np.float32))
    metadata = {
        'phase': 'final-heldout-v1', 'executed_at_utc': datetime.now(timezone.utc).isoformat(),
        'execution_lock_sha256': sha(root.parent/'heldout_execution.json'),
        'question_freeze_sha256': sha(root/'heldout-v1/freeze.json'), 'split': 'test',
        'question_ids_in_vector_order': [q['question_id'] for q in questions],
        'document_ids_in_vector_order': [c.chunk_id for c in chunks],
        'output_sha256': {name: sha(output/name) for name in ('rankings.jsonl', 'candidate_rankings.jsonl',
                                                            'scores.jsonl', 'pool.jsonl', 'query_vectors.npz')},
        'timings': timings, 'model_load_ms': model_load_ms,
        'median_rerank_only_ms': statistics.median(row['rerank_only_ms'] for row in timings),
        'truncated_pairs': sum(row['passage_truncated'] for row in scores),
        'scored_pairs': len(scores), 'max_pair_tokens_before_truncation': max(row['pair_tokens_before_truncation'] for row in scores),
        'heldout_queries_executed': len(questions), 'query_embedding_calls': len(questions),
        'development_warmup': {'query_encodes': 1, 'reranker_pairs': plan['warmup_pairs']},
        'packages': {name: importlib.metadata.version(name) for name in ('fastembed', 'numpy', 'onnxruntime', 'tokenizers')},
        'platform': platform.platform(), 'quality_results_used_for_tuning': False,
        'limitations': 'Prospective same-corpus AI-authored holdout. One fixed configuration. Retrieval only; no generated answers, citations or abstention decisions.',
    }
    write_json(output/'run.json', metadata)
    return {'questions_executed': len(questions), 'pooled_pairs': len(pool), 'scored_pairs': len(scores)}


def verify(root, output):
    """Replay every ranking and source identity from saved queries/logits."""
    root, output = Path(root), Path(output)
    validate_lock(root)
    metadata = read_json(output/'run.json')
    if metadata['execution_lock_sha256'] != sha(root.parent/'heldout_execution.json'):
        raise ValueError('Final execution lock differs from recorded run')
    for name, digest in metadata['output_sha256'].items():
        if sha(output/name) != digest:
            raise ValueError(f'Final output hash mismatch: {name}')
    chunks, questions, documents, _, _ = load_frozen(root)
    if (metadata['question_ids_in_vector_order'] != [q['question_id'] for q in questions]
            or metadata['document_ids_in_vector_order'] != [c.chunk_id for c in chunks]):
        raise ValueError('Saved vector row identity mismatch')
    with np.load(output/'query_vectors.npz', allow_pickle=False) as arrays:
        queries = arrays['queries']
    if queries.shape != (len(questions), documents.shape[1]) or not np.isfinite(queries).all():
        raise ValueError('Invalid saved query vectors')
    bm25, dense = BM25(chunks), DenseIndex(chunks, documents)
    logits = read_jsonl(output/'scores.jsonl')
    saved = read_jsonl(output/'rankings.jsonl')
    candidate_rows = read_jsonl(output/'candidate_rankings.jsonl')
    expected, expected_candidates, pool = [], [], {}
    if len(logits) != len(questions)*50 or len(saved) != len(questions)*40:
        raise ValueError('Incorrect final score/ranking counts')
    for q, vector in zip(questions, queries):
        qid = q['question_id']
        lexical, semantic, fused = retrieve(bm25, dense, q['question'], vector)
        rows = [row for row in logits if row['question_id'] == qid]
        if ([row['candidate_rank'] for row in rows] != list(range(1, 51))
                or [row['chunk_id'] for row in rows] != [c.chunk_id for c, _ in fused]):
            raise ValueError('Final reranker candidate identity/order mismatch')
        reranked = rank_scores([c for c, _ in fused], [row['score'] for row in rows])
        expected.extend(record_rankings(qid, [('bm25', lexical), ('dense', semantic), ('hybrid', fused),
                                              ('reranked_hybrid', reranked)], pool))
        for method, ranked in [('bm25', lexical), ('dense', semantic), ('hybrid', fused)]:
            expected_candidates.extend({'question_id': qid, 'method': method, 'rank': rank,
                                        'chunk_id': c.chunk_id, 'score': score}
                                       for rank, (c, score) in enumerate(ranked, 1))
    for actual, wanted in ((saved, expected), (candidate_rows, expected_candidates)):
        if len(actual) != len(wanted):
            raise ValueError('Final saved ranking length mismatch')
        for row, target in zip(actual, wanted):
            if (row.keys() != target.keys() or any(row[key] != value for key, value in target.items() if key != 'score')
                    or not math.isclose(row['score'], target['score'], rel_tol=1e-6, abs_tol=1e-7)):
                raise ValueError('Final ranking does not replay')
    saved_pool = unique(read_jsonl(output/'pool.jsonl'), pair, 'final pool pair')
    if saved_pool != pool:
        raise ValueError('Final pool source/provenance differs from replay')
    return {'questions': len(questions), 'ranked_results_verified': len(saved),
            'reranker_scores_verified': len(logits), 'pooled_pairs': len(pool), 'model_calls': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=Path('evaluation/pilot'))
    parser.add_argument('--output', type=Path, default=Path('evaluation/pilot/runs/heldout-final-v1'))
    parser.add_argument('--embedding-dir', type=Path)
    parser.add_argument('--reranker-dir', type=Path)
    parser.add_argument('--lock', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    try:
        if args.lock:
            execution_lock(args.dataset)
            print('Final implementation and inputs locked; no heldout inference performed.')
        elif args.verify:
            print(json.dumps(verify(args.dataset, args.output), indent=2))
        elif args.embedding_dir is None or args.reranker_dir is None:
            parser.error('Inference requires --embedding-dir and --reranker-dir')
        else:
            print(json.dumps(run(args.dataset, args.embedding_dir, args.reranker_dir, args.output), indent=2))
    except (ValueError, KeyError, OSError, ImportError) as exc:
        parser.exit(1, f'Final check failed: {exc}\n')
