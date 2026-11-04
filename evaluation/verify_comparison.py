"""Replay saved vectors and rankings offline, without downloading or loading a model."""
import argparse
import json
import math
from pathlib import Path

import numpy as np

from evaluation.keyword import BM25
from evaluation.run_comparison import DEPTH, RRF_CONSTANT, frozen_inputs, sha
from evaluation.semantic import DenseIndex, reciprocal_rank_fusion


def verify(root, baseline, comparison):
    root,baseline,comparison=Path(root),Path(baseline),Path(comparison)
    chunks,questions,_=frozen_inputs(root,baseline)
    metadata=json.loads((comparison/'run.json').read_text(encoding='utf-8'))
    required={
        'baseline_chunks_sha256':baseline/'chunks.jsonl',
        'baseline_run_sha256':baseline/'run.json',
        'questions_sha256':root/'questions.jsonl',
        'manifest_sha256':root/'corpus_manifest.json',
        'embedding_file_sha256':comparison/'embeddings.npz',
        'model_spec_sha256':Path(__file__).with_name('embedding_model.json'),
    }
    for key,path in required.items():
        if sha(path)!=metadata[key]:
            raise ValueError(f'Run artifact hash mismatch: {key}')
    for name,digest in metadata['implementation_sha256'].items():
        if sha(Path(__file__).with_name(name))!=digest:
            raise ValueError(f'Implementation changed since run: {name}')
    if metadata['chunk_ids_in_vector_order']!=[c.chunk_id for c in chunks] or metadata['question_ids_in_vector_order']!=[q['question_id'] for q in questions]:
        raise ValueError('Vector row identity mismatch')
    with np.load(comparison/'embeddings.npz',allow_pickle=False) as arrays:
        documents=arrays['documents']; queries=arrays['queries']
    if queries.shape!=(len(questions),metadata['dimension']) or documents.shape!=(len(chunks),metadata['dimension']):
        raise ValueError('Stored embedding shape mismatch')
    dense=DenseIndex(chunks,documents)
    bm25=BM25(chunks)
    saved=[json.loads(line) for line in (comparison/'rankings.jsonl').read_text().splitlines() if line.strip()]
    if len(saved)!=len(questions)*30:
        raise ValueError('Expected ten results per question per method')
    for question,vector in zip(questions,queries):
        lexical=bm25.search(question['question'],DEPTH)
        semantic=dense.search(vector,DEPTH)
        hybrid=reciprocal_rank_fusion([lexical,semantic],k=10,constant=RRF_CONSTANT)
        for method,ranking in [('bm25',lexical[:10]),('dense',semantic[:10]),('hybrid',hybrid)]:
            rows=[r for r in saved if r['question_id']==question['question_id'] and r['method']==method]
            if [r['rank'] for r in rows]!=list(range(1,11)) or [r['chunk_id'] for r in rows]!=[c.chunk_id for c,_ in ranking]:
                raise ValueError(f'Ranking mismatch: {question["question_id"]}/{method}')
            if any(not math.isclose(row['score'],score,rel_tol=1e-6,abs_tol=1e-7) for row,(_,score) in zip(rows,ranking)):
                raise ValueError(f'Score mismatch: {question["question_id"]}/{method}')
    return {'questions':len(questions),'methods':3,'ranked_results_verified':len(saved),'model_calls':0}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=Path('evaluation/pilot'))
    parser.add_argument('--baseline',type=Path,default=Path('evaluation/pilot/runs/bm25-v1'))
    parser.add_argument('--comparison',type=Path,default=Path('evaluation/pilot/runs/comparison-v1'))
    args=parser.parse_args()
    try:
        print(json.dumps(verify(args.dataset,args.baseline,args.comparison),indent=2))
    except (ValueError,OSError) as exc:
        parser.exit(1,f'Replay failed: {exc}\n')
