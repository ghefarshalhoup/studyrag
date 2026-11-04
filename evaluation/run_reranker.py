"""Run the predeclared local cross-encoder on development candidates only."""
import argparse
from collections import defaultdict
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import statistics
import time

import numpy as np

from evaluation.fetch_embedding_model import fetch, verify_model
from evaluation.keyword import BM25
from evaluation.run_comparison import frozen_inputs
from evaluation.run_metrics import read_json, read_jsonl, sha, write_json
from evaluation.semantic import DenseIndex, reciprocal_rank_fusion
from evaluation.validate_holdout import validate as validate_holdout
from evaluation.verify_comparison import verify as verify_comparison


METHOD = 'reranked_hybrid'
IMPLEMENTATION = ('run_reranker.py', 'semantic.py', 'keyword.py')


def rank_scores(candidates, scores, k=10):
    if type(k) is not int or k < 1:
        raise ValueError('k must be positive')
    candidates, scores = list(candidates), list(scores)
    if len(candidates) != len(scores):
        raise ValueError('Expected exactly one score per candidate')
    if len({c.chunk_id for c in candidates}) != len(candidates):
        raise ValueError('Duplicate reranker candidate')
    if any(not math.isfinite(score) for score in scores):
        raise ValueError('Non-finite reranker score')
    return sorted(zip(candidates, map(float, scores)), key=lambda item: (-item[1], item[0].chunk_id))[:k]


def build_candidates(dataset, baseline, comparison):
    # Verify source/config, saved vectors and all old top-10 identities first.
    verify_comparison(dataset, baseline, comparison)
    chunks, questions, _ = frozen_inputs(dataset, baseline)
    if any(q['split'] != 'dev' for q in questions):
        raise ValueError('This runner is restricted to development questions')
    metadata = read_json(comparison/'run.json')
    with np.load(comparison/'embeddings.npz', allow_pickle=False) as arrays:
        documents, queries = arrays['documents'], arrays['queries']
    bm25, dense = BM25(chunks), DenseIndex(chunks, documents)
    if metadata['question_ids_in_vector_order'] != [q['question_id'] for q in questions]:
        raise ValueError('Query vector identities changed')
    candidates = {}
    for question, vector in zip(questions, queries):
        first = bm25.search(question['question'], 50)
        second = dense.search(vector, 50)
        candidates[question['question_id']] = [c for c, _ in reciprocal_rank_fusion([first, second], k=50, constant=60)]
    return chunks, questions, candidates


def input_paths(dataset, baseline, comparison):
    return {
        'questions': dataset/'questions.jsonl', 'manifest': dataset/'corpus_manifest.json',
        'chunks': baseline/'chunks.jsonl', 'baseline_run': baseline/'run.json',
        'comparison_run': comparison/'run.json', 'comparison_rankings': comparison/'rankings.jsonl',
        'comparison_pool': comparison/'pool.jsonl', 'embeddings': comparison/'embeddings.npz',
        'heldout_freeze': dataset/'heldout-v1/freeze.json',
        'plan': Path(__file__).with_name('reranker_plan.json'),
        'model_spec': Path(__file__).with_name('reranker_model.json'),
    }


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False, allow_nan=False)+'\n' for row in rows), encoding='utf-8')


def run(dataset, baseline, comparison, model_dir, output):
    dataset, baseline, comparison = map(Path, (dataset, baseline, comparison))
    output, model_dir = Path(output).resolve(), Path(model_dir).resolve()
    if any(path.resolve().is_relative_to(output) for path in (dataset, baseline, comparison, model_dir)):
        raise ValueError('Output cannot replace an input directory or its ancestor')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a new empty output directory')
    validate_holdout(dataset)
    plan = read_json(Path(__file__).with_name('reranker_plan.json'))
    spec = read_json(Path(__file__).with_name('reranker_model.json'))
    if (plan['split_to_run_now'] != 'dev' or plan['candidate_depth'] != 50
            or plan['rrf_constant'] != 60 or plan['output_depth'] != 10
            or plan['reranker_model'] != spec['model_name'] or plan['revision'] != spec['revision']
            or plan['model_file'] != spec['model_file']):
        raise ValueError('Unsupported or inconsistent frozen plan/model')
    verify_model(model_dir, spec)
    chunks, questions, candidates = build_candidates(dataset, baseline, comparison)
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    from tokenizers import Tokenizer
    raw_tokenizer = Tokenizer.from_file(str(model_dir/'tokenizer.json'))
    raw_tokenizer.no_padding(); raw_tokenizer.no_truncation()
    start = time.perf_counter_ns()
    model = TextCrossEncoder(model_name=spec['model_name'], specific_model_path=str(model_dir),
                             local_files_only=True, providers=[plan['provider']],
                             threads=plan['threads'], cache_dir=str(model_dir/'runtime-cache'))
    load_ms = (time.perf_counter_ns()-start)/1e6
    # Preserve the entire query; only a long passage tail may be truncated.
    tokenizer = model.model.tokenizer
    tokenizer.enable_truncation(max_length=plan['max_pair_tokens'], strategy='only_second', direction='right')
    first = questions[0]
    list(model.rerank(first['question'], [c.text for c in candidates[first['question_id']][:plan['warmup_pairs']]],
                      batch_size=plan['batch_size']))
    rankings = read_jsonl(comparison/'rankings.jsonl')
    pool = {(row['question_id'], row['chunk_id']): row for row in read_jsonl(comparison/'pool.jsonl')}
    scores_saved, timings = [], []
    for question in questions:
        qid, query = question['question_id'], question['question']
        selected = candidates[qid]
        if len(raw_tokenizer.encode(query).ids)+1 >= plan['max_pair_tokens']:
            raise ValueError('Query exceeds pair context; refusing query truncation')
        pairs = [(query, c.text) for c in selected]
        lengths = [len(tokens.ids) for tokens in raw_tokenizer.encode_batch(pairs)]
        start = time.perf_counter_ns()
        logits = list(model.rerank(query, [c.text for c in selected], batch_size=plan['batch_size']))
        ranked = rank_scores(selected, logits, k=10)
        elapsed = (time.perf_counter_ns()-start)/1e6
        timings.append({'question_id': qid, 'rerank_ms': elapsed})
        for index, (chunk, score, length) in enumerate(zip(selected, logits, lengths), 1):
            scores_saved.append({'question_id': qid, 'candidate_rank': index, 'chunk_id': chunk.chunk_id,
                                 'score': float(score), 'pair_tokens_before_truncation': length,
                                 'passage_truncated': length > plan['max_pair_tokens']})
        for rank, (chunk, score) in enumerate(ranked, 1):
            rankings.append({'question_id': qid, 'method': METHOD, 'rank': rank, 'score': score,
                             'chunk_id': chunk.chunk_id, 'document_id': chunk.document_id,
                             'start_line': chunk.start_line, 'end_line': chunk.end_line})
            item = pool.setdefault((qid, chunk.chunk_id), {
                'question_id': qid, 'chunk_id': chunk.chunk_id, 'document_id': chunk.document_id,
                'start_line': chunk.start_line, 'end_line': chunk.end_line,
                'text': chunk.text, 'retrieved_by': [], 'judgment': 'unjudged'})
            item['retrieved_by'].append({'method': METHOD, 'rank': rank})
        print('Reranked', qid, f'{elapsed:.1f} ms', flush=True)
    output.mkdir(parents=True, exist_ok=True)
    write_jsonl(output/'rankings.jsonl', rankings)
    write_jsonl(output/'pool.jsonl', list(pool.values()))
    write_jsonl(output/'scores.jsonl', scores_saved)
    metadata = {
        'method': METHOD, 'split': 'dev', 'plan': plan, 'model': spec,
        'input_sha256': {name: sha(path) for name, path in input_paths(dataset, baseline, comparison).items()},
        'implementation_sha256': {name: sha(Path(__file__).with_name(name)) for name in IMPLEMENTATION},
        'output_sha256': {name: sha(output/name) for name in ('rankings.jsonl', 'pool.jsonl', 'scores.jsonl')},
        'model_load_ms': load_ms, 'timings': timings,
        'median_rerank_ms': statistics.median(row['rerank_ms'] for row in timings),
        'max_pair_tokens_before_truncation': max(row['pair_tokens_before_truncation'] for row in scores_saved),
        'truncated_pairs': sum(row['passage_truncated'] for row in scores_saved),
        'scored_pairs': len(scores_saved), 'warmup_pairs_excluded': plan['warmup_pairs'],
        'packages': {name: importlib.metadata.version(name) for name in ('fastembed', 'numpy', 'onnxruntime', 'tokenizers')},
        'platform': platform.platform(), 'heldout_queries_executed': 0,
        'limitations': 'Development run only. Raw logits are not probabilities. Only passage tails may be truncated for ranking; returned chunks retain full text. Timings exclude candidate retrieval and model loading.',
    }
    write_json(output/'run.json', metadata)
    print(json.dumps({'scored_pairs': len(scores_saved), 'pooled_pairs': len(pool),
                      'median_rerank_ms': metadata['median_rerank_ms'], 'truncated_pairs': metadata['truncated_pairs']}))
    return metadata


def verify(dataset, baseline, comparison, output):
    """Replay candidate selection and sorting from saved logits, with no model."""
    dataset, baseline, comparison, output = map(Path, (dataset, baseline, comparison, output))
    validate_holdout(dataset)
    meta = read_json(output/'run.json')
    for name, path in input_paths(dataset, baseline, comparison).items():
        if sha(path) != meta['input_sha256'][name]:
            raise ValueError(f'Reranker input hash mismatch: {name}')
    for name, digest in meta['implementation_sha256'].items():
        if sha(Path(__file__).with_name(name)) != digest:
            raise ValueError(f'Reranker implementation changed: {name}')
    for name, digest in meta['output_sha256'].items():
        if sha(output/name) != digest:
            raise ValueError(f'Reranker output hash mismatch: {name}')
    _, questions, candidates = build_candidates(dataset, baseline, comparison)
    scores = read_jsonl(output/'scores.jsonl')
    rankings = read_jsonl(output/'rankings.jsonl')
    if len(scores) != len(questions)*50 or len(rankings) != len(questions)*40:
        raise ValueError('Incorrect saved score/ranking counts')
    for q in questions:
        qid = q['question_id']
        rows = [row for row in scores if row['question_id'] == qid]
        if ([row['candidate_rank'] for row in rows] != list(range(1, 51))
                or [row['chunk_id'] for row in rows] != [c.chunk_id for c in candidates[qid]]):
            raise ValueError('Candidate identity/order mismatch')
        ranked = rank_scores(candidates[qid], [row['score'] for row in rows])
        saved = [row for row in rankings if row['question_id'] == qid and row['method'] == METHOD]
        if [row['rank'] for row in saved] != list(range(1, 11)) or [(row['chunk_id'], row['score']) for row in saved] != [(c.chunk_id, score) for c, score in ranked]:
            raise ValueError('Saved reranker ranking differs from logits')
    prior = [row for row in rankings if row['method'] != METHOD]
    if prior != read_jsonl(comparison/'rankings.jsonl'):
        raise ValueError('Existing baseline rankings changed')
    return {'rankings_verified': len(rankings), 'scores_verified': len(scores), 'model_calls': 0, 'heldout_queries_executed': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=Path('evaluation/pilot'))
    parser.add_argument('--baseline', type=Path, default=Path('evaluation/pilot/runs/bm25-v1'))
    parser.add_argument('--comparison', type=Path, default=Path('evaluation/pilot/runs/comparison-v1'))
    parser.add_argument('--model-dir', type=Path)
    parser.add_argument('--output', type=Path, default=Path('evaluation/pilot/runs/reranker-v1'))
    parser.add_argument('--fetch-model', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    try:
        if args.verify:
            print(json.dumps(verify(args.dataset, args.baseline, args.comparison, args.output), indent=2))
        elif args.model_dir is None:
            parser.error('--model-dir is required for fetching or inference')
        elif args.fetch_model:
            fetch(args.model_dir, read_json(Path(__file__).with_name('reranker_model.json')))
        else:
            run(args.dataset, args.baseline, args.comparison, args.model_dir, args.output)
    except (ValueError, KeyError, OSError, ImportError) as exc:
        parser.exit(1, f'Reranker failed: {exc}\n')
