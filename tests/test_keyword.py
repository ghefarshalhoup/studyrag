"""Offline retrieval tests with analytical scores and source-coordinate checks."""
import hashlib
import json
import math
from pathlib import Path

import pytest

from evaluation.keyword import BM25, Chunk, ChunkConfig, covered_fraction, evidence_diagnostics, make_chunks, normalize_rst, tokenize
from evaluation.run_keyword import run


def document(text, name='notes'):
    raw=text.encode('utf-8')
    return {'document_id':name,'path':f'corpus/{name}.rst',
            'sha256':hashlib.sha256(raw).hexdigest()},raw


def chunk(text, name='c', start=0, end=10, doc='notes'):
    return Chunk(name,doc,'hash','notes.rst',start,end,1,1,text)


def test_bm25_matches_hand_calculated_score():
    index=BM25([chunk('apple apple','a'),chunk('pear','b')])
    ranked=index.search('apple')
    assert len(ranked)==1
    assert ranked[0][0].chunk_id=='a'
    # N=2, df=1, tf=2, dl=2, avgdl=1.5: log(2) * 4.4 / 3.5.
    assert ranked[0][1]==pytest.approx(math.log(2)*4.4/3.5)


def test_query_repetition_does_not_change_binary_query_weight():
    index=BM25([chunk('apple apple','a'),chunk('pear','b')])
    assert index.search('apple apple')==index.search('APPLE')


def test_ties_do_not_depend_on_index_order():
    chunks=[chunk('apple','b'),chunk('apple','a')]
    first=BM25(chunks).search('apple')
    second=BM25(list(reversed(chunks))).search('apple')
    assert first==second
    assert [c.chunk_id for c,_ in first]==['a','b']


def test_empty_or_unknown_query_returns_no_candidates():
    assert BM25([]).search('apple')==[]
    index=BM25([chunk('apple')])
    assert index.search('unknown')==[]
    assert index.search('!!!')==[]


@pytest.mark.parametrize('k',[0,-1,True,1.5])
def test_invalid_search_depth_rejected(k):
    with pytest.raises(ValueError):
        BM25([]).search('q',k)


def test_duplicate_chunk_ids_rejected():
    with pytest.raises(ValueError,match='Duplicate chunk IDs'):
        BM25([chunk('a'),chunk('b')])


@pytest.mark.parametrize('config',[ChunkConfig(0,0),ChunkConfig(20,20),ChunkConfig(20,-1)])
def test_invalid_chunk_configuration_rejected(config):
    doc,raw=document('text')
    with pytest.raises(ValueError):
        make_chunks(doc,raw,config)


def test_source_mutation_rejected():
    doc,raw=document('text')
    with pytest.raises(ValueError,match='hash mismatch'):
        make_chunks(doc,raw+b'changed')


def test_chunks_are_stable_and_reconstruct_source_locations():
    text=''.join(f'Line {i}: evidence about Python data.\n' for i in range(25))
    doc,raw=document(text)
    config=ChunkConfig(140,25)
    chunks=make_chunks(doc,raw,config)
    assert chunks==make_chunks(doc,raw,config)
    assert len({c.chunk_id for c in chunks})==len(chunks)
    for c in chunks:
        assert c.text==normalize_rst(text[c.start_char:c.end_char])
        assert c.start_line==text.count('\n',0,c.start_char)+1
        assert c.end_line==text.count('\n',0,c.end_char-1)+1
        assert c.end_char-c.start_char<=config.size
    # Windows touch every character of this prose-only test without gaps.
    assert covered_fraction({'document_id':'notes','start_char':0,'end_char':len(text)},chunks)==1
    assert chunks[0].chunk_id!=make_chunks(doc,raw,ChunkConfig(150,25))[0].chunk_id


def test_crlf_coordinates_use_normalized_text():
    doc,raw=document('alpha\r\nbeta\r\ngamma')
    chunks=make_chunks(doc,raw)
    assert chunks[0].text=='alpha\nbeta\ngamma'
    assert chunks[0].end_char==len('alpha\nbeta\ngamma')


def test_long_unbroken_line_makes_progress_without_losing_content():
    doc,raw=document('x'*500)
    chunks=make_chunks(doc,raw,ChunkConfig(30,5))
    assert chunks[-1].end_char==500
    assert all(c.end_char>c.start_char for c in chunks)


def test_rst_cleaning_preserves_code_identifiers():
    text='.. _anchor:\n\nA heading\n=========\nUse :class:`collections.deque`.\n   >>> x = next(it)\n'
    cleaned=normalize_rst(text)
    assert 'anchor' not in cleaned and '=========' not in cleaned
    assert 'collections.deque' in cleaned and 'next(it)' in cleaned
    assert tokenize('__main__ + Decimal(1)')==['__main__','decimal','1']


def test_interval_union_never_double_counts_overlap_or_other_documents():
    evidence={'document_id':'notes','start_char':10,'end_char':30}
    chunks=[chunk('a','a',0,20),chunk('b','b',15,25),chunk('c','c',10,30,doc='other')]
    assert covered_fraction(evidence,chunks)==.75
    assert covered_fraction(evidence,chunks+[chunk('d','d',25,35)])==1


def test_small_overlap_is_not_a_complete_evidence_hit():
    question={'evidence':[{'document_id':'notes','start_char':10,'end_char':30,'relevance':2}]}
    d=evidence_diagnostics(question,[chunk('a',start=29,end=40)])
    assert d['any_known_passage_complete'] is False
    assert d['mean_passage_character_coverage']==.05
    assert evidence_diagnostics({'evidence':[]},[]) is None


def test_run_is_reproducible_and_indexes_only_manifest_sources(tmp_path):
    root=Path(__file__).resolve().parents[1]/'evaluation'/'pilot'
    first,second=tmp_path/'first',tmp_path/'second'
    summary=run(root,first,repeats=1)
    run(root,second,repeats=1)
    # Rankings and chunks are deterministic; measured runtimes need not be.
    assert (first/'rankings.jsonl').read_bytes()==(second/'rankings.jsonl').read_bytes()
    assert (first/'chunks.jsonl').read_bytes()==(second/'chunks.jsonl').read_bytes()
    metadata=json.loads((first/'run.json').read_text())
    assert len(metadata['indexed_files'])==12
    assert all(p.startswith('corpus/') and p.endswith('.rst') for p in metadata['indexed_files'])
    assert summary['answerable_queries']==16
    assert summary['unanswerable_queries']==4
    assert 0<=summary['seed_evidence_hit_at_5']<=summary['seed_evidence_hit_at_10']<=1
    assert {p.name for p in first.iterdir()}=={
        'chunks.jsonl','rankings.jsonl','diagnostics.json','summary.json','run.json','REPORT.md',
    }
    with pytest.raises(ValueError,match='not empty'):
        run(root,first,repeats=1)


def test_output_cannot_replace_dataset_root(tmp_path):
    with pytest.raises(ValueError,match='dataset root'):
        run(tmp_path,tmp_path)
