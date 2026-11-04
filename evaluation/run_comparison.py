"""Compare BM25, local BGE cosine retrieval, and RRF on frozen baseline inputs.

The model must already be downloaded explicitly. Inference is local-only.
"""
import argparse
from collections import defaultdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import statistics
import sys
import time

import numpy as np

from evaluation.fetch_embedding_model import verify_model
from evaluation.keyword import BM25, Chunk, ChunkConfig, evidence_diagnostics, make_chunks
from evaluation.pilot.validate_dataset import local_path, validate
from evaluation.run_keyword import percentile95, write_json, write_jsonl
from evaluation.semantic import DenseIndex, reciprocal_rank_fusion

QUERY_PREFIX='Represent this sentence for searching relevant passages: '
DEPTH=50
RRF_CONSTANT=60


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_inputs(root, baseline):
    root,baseline=Path(root),Path(baseline)
    validate(root,require_reviewed=True)
    meta=json.loads((baseline/'run.json').read_text(encoding='utf-8'))
    if sha(root/'questions.jsonl')!=meta['questions_sha256'] or sha(root/'corpus_manifest.json')!=meta['manifest_sha256']:
        raise ValueError('Corpus or labels differ from the frozen BM25 baseline')
    manifest=json.loads((root/'corpus_manifest.json').read_text(encoding='utf-8'))
    chunks=[Chunk(**json.loads(l)) for l in (baseline/'chunks.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    rebuilt=[]
    for doc in sorted(manifest['documents'],key=lambda d:d['document_id']):
        rebuilt.extend(make_chunks(doc,local_path(root,doc['path']).read_bytes(),ChunkConfig(**meta['chunking'])))
    if rebuilt!=chunks:
        raise ValueError('Frozen chunk records differ from current source/configuration')
    questions=[json.loads(l) for l in (root/'questions.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    return chunks,questions,meta


def aggregate(diagnostics):
    summaries={}
    for method in ('bm25','dense','hybrid'):
        rows=[d for d in diagnostics if d['method']==method]
        answerable=[d for d in rows if d['answerable']]
        summaries[method]={
            'answerable_queries':len(answerable),
            'hit_count_at_5':sum(d['at_5']['any_known_passage_complete'] for d in answerable),
            'hit_count_at_10':sum(d['at_10']['any_known_passage_complete'] for d in answerable),
            'mean_seed_passage_character_coverage_at_10':statistics.mean(d['at_10']['mean_passage_character_coverage'] for d in answerable),
            'unanswerable_queries_returning_candidates':sum(not d['answerable'] and d['results_returned']>0 for d in rows),
            'median_query_latency_ms':statistics.median(t for d in rows for t in d['timings_ms']),
            'p95_query_latency_ms':percentile95([t for d in rows for t in d['timings_ms']]),
        }
    return summaries


def run(root, baseline, model_dir, output, repeats=5):
    if type(repeats) is not int or repeats<1:
        raise ValueError('repeats must be positive')
    root,baseline,output=Path(root),Path(baseline),Path(output).resolve()
    if output==root.resolve() or root.resolve().is_relative_to(output) or output==Path(model_dir).resolve():
        raise ValueError('Output cannot replace the dataset or model root')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use a new empty output directory')
    chunks,questions,base_meta=frozen_inputs(root,baseline)
    spec_path=Path(__file__).with_name('embedding_model.json')
    spec=json.loads(spec_path.read_text(encoding='utf-8'))
    verify_model(model_dir,spec)
    from fastembed import TextEmbedding
    from tokenizers import Tokenizer
    tokenizer=Tokenizer.from_file(str(Path(model_dir)/'tokenizer.json'))
    tokenizer.no_padding(); tokenizer.no_truncation()
    passages=[c.text for c in chunks]
    queries=[QUERY_PREFIX+q['question'] for q in questions]
    passage_lengths=[len(e.ids) for e in tokenizer.encode_batch(passages)]
    query_lengths=[len(e.ids) for e in tokenizer.encode_batch(queries)]
    if max(passage_lengths+query_lengths)>512:
        raise ValueError('Some inputs exceed 512 tokens; refusing silent truncation of frozen evidence')
    start=time.perf_counter_ns()
    model=TextEmbedding(model_name=spec['model_name'],specific_model_path=str(Path(model_dir).resolve()),
                        local_files_only=True,cache_dir=str(Path(model_dir)/'runtime-cache'),
                        providers=['CPUExecutionProvider'],threads=2)
    load_ms=(time.perf_counter_ns()-start)/1e6
    print('Encoding',len(chunks),'frozen passages locally...',flush=True)
    start=time.perf_counter_ns()
    document_vectors=np.asarray(list(model.passage_embed(passages,batch_size=16)),dtype=np.float32)
    doc_encode_ms=(time.perf_counter_ns()-start)/1e6
    dense=DenseIndex(chunks,document_vectors)
    bm25=BM25(chunks)
    rankings=[]; candidate_rows=[]; diagnostics=[]; vectors=[]; pools={}
    def encode(text):
        return np.asarray(next(iter(model.query_embed(QUERY_PREFIX+text))),dtype=np.float32)
    # Check BM25 ranking identity against the original saved run before comparison.
    prior=[json.loads(l) for l in (baseline/'rankings.jsonl').read_text().splitlines() if l.strip()]
    for q in questions:
        expected=[r['chunk_id'] for r in prior if r['question_id']==q['question_id']]
        actual=[c.chunk_id for c,_ in bm25.search(q['question'],10)]
        if expected!=actual:
            raise ValueError('BM25 rankings changed from the frozen baseline')
    for q in questions:
        text=q['question']
        dense.search(encode(text),DEPTH)  # real query warm-up, excluded
        timings=defaultdict(list)
        for _ in range(repeats):
            start=time.perf_counter_ns(); lexical=bm25.search(text,DEPTH)
            lexical_ms=(time.perf_counter_ns()-start)/1e6
            start=time.perf_counter_ns(); vector=encode(text); semantic=dense.search(vector,DEPTH)
            semantic_ms=(time.perf_counter_ns()-start)/1e6
            start=time.perf_counter_ns(); hybrid=reciprocal_rank_fusion([lexical,semantic],k=10,constant=RRF_CONSTANT)
            fusion_ms=(time.perf_counter_ns()-start)/1e6
            timings['bm25'].append(lexical_ms); timings['dense'].append(semantic_ms)
            timings['hybrid'].append(lexical_ms+semantic_ms+fusion_ms)
        vectors.append(vector)
        for method,ranking in [('bm25',lexical),('dense',semantic),('hybrid',hybrid)]:
            if method!='hybrid':
                candidate_rows.extend({'question_id':q['question_id'],'method':method,'rank':i,'chunk_id':c.chunk_id,'score':score}
                                      for i,(c,score) in enumerate(ranking,1))
            top=ranking[:10]
            for i,(c,score) in enumerate(top,1):
                rankings.append({'question_id':q['question_id'],'method':method,'rank':i,'score':score,
                                 'chunk_id':c.chunk_id,'document_id':c.document_id,
                                 'start_line':c.start_line,'end_line':c.end_line})
                item=pools.setdefault((q['question_id'],c.chunk_id),
                    {'question_id':q['question_id'],'chunk_id':c.chunk_id,'document_id':c.document_id,
                     'start_line':c.start_line,'end_line':c.end_line,'text':c.text,'retrieved_by':[],
                     'judgment':'unjudged'})
                item['retrieved_by'].append({'method':method,'rank':i})
            diagnostics.append({'question_id':q['question_id'],'method':method,'category':q['category'],
                                'answerable':q['answerable'],'results_returned':len(top),
                                'at_5':evidence_diagnostics(q,[c for c,_ in top[:5]]),
                                'at_10':evidence_diagnostics(q,[c for c,_ in top]),
                                'timings_ms':timings[method]})
        print('Compared',q['question_id'],flush=True)
    summary=aggregate(diagnostics)
    output.mkdir(parents=True,exist_ok=True)
    write_jsonl(output/'rankings.jsonl',rankings)
    write_jsonl(output/'candidate_rankings.jsonl',candidate_rows)
    write_jsonl(output/'pool.jsonl',list(pools.values()))
    write_json(output/'diagnostics.json',diagnostics)
    write_json(output/'summary.json',summary)
    np.savez_compressed(output/'embeddings.npz',documents=document_vectors,queries=np.asarray(vectors))
    metadata={'model':spec,'model_spec_sha256':sha(spec_path),'query_prefix':QUERY_PREFIX,'passage_prefix':'',
              'pooling':'CLS embedding then L2 normalization, via FastEmbed OnnxTextEmbedding',
              'dimension':int(document_vectors.shape[1]),'model_load_ms':load_ms,'passage_encoding_ms':doc_encode_ms,
              'max_passage_tokens':max(passage_lengths),'max_query_tokens_with_prefix':max(query_lengths),'truncated_inputs':0,
              'baseline_chunks_sha256':sha(baseline/'chunks.jsonl'),'questions_sha256':sha(root/'questions.jsonl'),
              'manifest_sha256':sha(root/'corpus_manifest.json'),'baseline_run_sha256':sha(baseline/'run.json'),
              'embedding_file_sha256':sha(output/'embeddings.npz'),'chunk_ids_in_vector_order':[c.chunk_id for c in chunks],
              'question_ids_in_vector_order':[q['question_id'] for q in questions],
              'rrf':{'constant':RRF_CONSTANT,'candidate_depth_per_method':DEPTH,'weights':[1,1]},
              'timing':{'warmups':1,'repeats_per_query':repeats,'dense':'includes real query encoding and exact cosine ranking',
                        'hybrid':'sum of sequential BM25, query encoding, cosine ranking, and fusion measurements',
                        'excluded':'document embedding, model loading, UI, generation, diagnostics, disk serialization'},
              'providers':['CPUExecutionProvider'],'onnx_threads':2,'python':sys.version.split()[0],'platform':platform.platform(),
              'packages':{dist.metadata['Name']:dist.version for dist in importlib.metadata.distributions()},
              'implementation_sha256':{name:sha(Path(__file__).with_name(name)) for name in ['keyword.py','semantic.py','run_comparison.py','fetch_embedding_model.py']},
              'limitations':'Incomplete AI-reviewed development labels. No answer generation, gold relevance metrics or held-out claims. No reranker in this comparison.'}
    write_json(output/'run.json',metadata)
    report=['# Retrieval comparison','',
            'All three methods searched the same frozen 250 chunks for the same 20 development questions. No paid APIs were used. Scores below measure known evidence coverage, not answer accuracy or held-out performance.','',
            '| Method | Complete passage at 5 | Complete passage at 10 | Mean passage character coverage at 10 | Median query ms |',
            '|---|---|---|---|---|']
    for method,s in summary.items():
        report.append(f'| {method} | {s["hit_count_at_5"]}/16 | {s["hit_count_at_10"]}/16 | {s["mean_seed_passage_character_coverage_at_10"]:.1%} | {s["median_query_latency_ms"]:.2f} |')
    report+=['','Dense search uses the pinned quantized ONNX export of BAAI/bge-small-en-v1.5. Hybrid search fuses top-50 BM25 and dense candidates using equal-weight RRF with constant 60. No settings were tuned to these results. Dense timings include query encoding; hybrid timings sum its sequential components. Passage encoding and model loading are recorded separately in run.json.','',
             '## Per-question known-evidence hits at 10','',
             '| Question | BM25 | Dense | Hybrid |','|---|---|---|---|']
    lookup={(d['question_id'],d['method']):d for d in diagnostics}
    for q in questions:
        flags=[]
        for method in summary:
            d=lookup[q['question_id'],method]['at_10']
            flags.append('n/a' if d is None else 'yes' if d['any_known_passage_complete'] else 'no')
        report.append(f'| {q["question_id"]} | '+ ' | '.join(flags)+' |')
    report+=['','## Inspect examples','',
             'Source excerpts retain Python Software Foundation attribution and PSF-2.0 terms; see evaluation/pilot/ATTRIBUTION.md. Lines refer to original pinned RST.','']
    by_id={c.chunk_id:c for c in chunks}
    for q in questions:
        report += [f'### {q["question_id"]}','',q['question'],'']
        for method in summary:
            result=next((r for r in rankings if r['question_id']==q['question_id'] and r['method']==method and r['rank']==1),None)
            if result:
                c=by_id[result['chunk_id']]
                report += [f'**{method}: {c.document_id}, lines {c.start_line}-{c.end_line}**','',
                           '````text',c.text[:650]+(' ...' if len(c.text)>650 else ''),'````','']
    report+=['## Limits and next stage','',
             'All four unanswerable questions can still retrieve candidates. Neither cosine similarity nor RRF is an answerability guarantee. Seed-passage hits can miss sufficient subpassages or alternative evidence and do not establish multi-part answer completeness. The pooled candidates are saved in pool.jsonl as unjudged; review them before calculating nDCG, MRR or gold recall. Keep separate held-out questions for later generalization checks.','']
    (output/'REPORT.md').write_text('\n'.join(report),encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=Path('evaluation/pilot'))
    parser.add_argument('--baseline',type=Path,default=Path('evaluation/pilot/runs/bm25-v1'))
    parser.add_argument('--model-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=Path('evaluation/pilot/runs/comparison-v1'))
    args=parser.parse_args()
    try:
        print(json.dumps(run(args.dataset,args.baseline,args.model_dir,args.output),indent=2))
    except (ValueError,OSError,ImportError) as exc:
        parser.exit(1,f'Comparison failed: {exc}\n')
