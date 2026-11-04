"""Cosine, fusion, model-integrity and frozen-input checks without model calls."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import pytest

from evaluation.fetch_embedding_model import verify_model
from evaluation.keyword import Chunk
from evaluation.run_comparison import frozen_inputs
from evaluation.semantic import DenseIndex, reciprocal_rank_fusion
from evaluation.verify_comparison import verify


def chunk(name):
    return Chunk(name,'doc','hash','doc.rst',0,5,1,1,'text')


def test_cosine_uses_normalized_vectors_and_known_angles():
    a,b,c=map(chunk,['a','b','c'])
    result=DenseIndex([a,b,c],[[2,0],[0,3],[-4,0]]).search([7,0])
    assert [c.chunk_id for c,_ in result]==['a','b','c']
    assert [s for _,s in result]==pytest.approx([1,0,-1])


def test_cosine_ties_are_stable_across_input_order():
    a,b=chunk('a'),chunk('b')
    assert DenseIndex([b,a],[[1,0],[1,0]]).search([1,0])==DenseIndex([a,b],[[1,0],[1,0]]).search([1,0])


@pytest.mark.parametrize('vectors',[[[0,0]],[[float('nan'),1]],[[float('inf'),1]],[[1,0],[0,1]],[1,0]])
def test_invalid_document_embeddings_rejected(vectors):
    with pytest.raises(ValueError):
        DenseIndex([chunk('a')],vectors)


@pytest.mark.parametrize('query',[[0,0],[1],[float('nan'),1],[[1,0]]])
def test_invalid_query_embeddings_rejected(query):
    with pytest.raises(ValueError):
        DenseIndex([chunk('a')],[[1,0]]).search(query)


def test_rrf_matches_hand_calculated_scores_without_mixing_raw_scores():
    a,b,c=map(chunk,['a','b','c'])
    result=reciprocal_rank_fusion([[(a,1000),(b,.1)],[(b,-3),(c,-100)]])
    assert [c.chunk_id for c,_ in result]==['b','a','c']
    assert [s for _,s in result]==pytest.approx([1/62+1/61,1/61,1/62])


def test_rrf_empty_and_duplicate_rankings():
    assert reciprocal_rank_fusion([[],[]])==[]
    a=chunk('a')
    with pytest.raises(ValueError,match='Duplicate chunk'):
        reciprocal_rank_fusion([[(a,1),(a,.5)]])
    with pytest.raises(ValueError,match='Conflicting'):
        reciprocal_rank_fusion([[(a,1)],[(replace(a,text='changed'),1)]])


def test_model_files_require_exact_hashes(tmp_path):
    data=b'example model file'
    (tmp_path/'model.onnx').write_bytes(data)
    spec={'files':[{'path':'model.onnx','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}]}
    verify_model(tmp_path,spec)
    (tmp_path/'model.onnx').write_bytes(b'changed')
    with pytest.raises(ValueError,match='hash mismatch'):
        verify_model(tmp_path,spec)


def test_model_path_cannot_escape_directory(tmp_path):
    with pytest.raises(ValueError,match='escapes'):
        verify_model(tmp_path,{'files':[{'path':'../outside.onnx','bytes':1,'sha256':'x'}]})


def test_frozen_inputs_match_baseline_and_detect_label_change(tmp_path):
    original=Path(__file__).resolve().parents[1]/'evaluation'/'pilot'
    root=tmp_path/'pilot'
    shutil.copytree(original,root,ignore=shutil.ignore_patterns('__pycache__'))
    baseline=root/'runs'/'bm25-v1'
    chunks,questions,_=frozen_inputs(root,baseline)
    assert len(chunks)==250 and len(questions)==20
    path=root/'questions.jsonl'
    path.write_bytes(path.read_bytes()+b'\n')
    with pytest.raises(ValueError,match='differ from'):
        frozen_inputs(root,baseline)


def test_frozen_chunks_cannot_be_silently_changed(tmp_path):
    root=Path(__file__).resolve().parents[1]/'evaluation'/'pilot'
    baseline=tmp_path/'baseline'
    shutil.copytree(root/'runs'/'bm25-v1',baseline)
    path=baseline/'chunks.jsonl'
    rows=[json.loads(l) for l in path.read_text(encoding='utf-8').splitlines()]
    rows[0]['text']='tampered source'
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    with pytest.raises(ValueError,match='chunk records differ'):
        frozen_inputs(root,baseline)


def test_saved_real_run_replays_without_model_calls():
    root=Path(__file__).resolve().parents[1]/'evaluation'/'pilot'
    result=verify(root,root/'runs'/'bm25-v1',root/'runs'/'comparison-v1')
    assert result=={'questions':20,'methods':3,'ranked_results_verified':600,'model_calls':0}


def test_modified_saved_ranking_is_detected(tmp_path):
    root=Path(__file__).resolve().parents[1]/'evaluation'/'pilot'
    comparison=tmp_path/'comparison'
    shutil.copytree(root/'runs'/'comparison-v1',comparison)
    path=comparison/'rankings.jsonl'
    rows=[json.loads(l) for l in path.read_text().splitlines()]
    rows[0]['score']+=1
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    with pytest.raises(ValueError,match='Score mismatch'):
        verify(root,root/'runs'/'bm25-v1',comparison)
