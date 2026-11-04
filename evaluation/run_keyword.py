"""Run the offline keyword baseline: python -m evaluation.run_keyword.

    Scores are diagnostic coverage of seed evidence, not gold-standard nDCG/MRR.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import sys
import time

from evaluation.keyword import BM25, ChunkConfig, PREPROCESSOR_VERSION, TOKENIZER_VERSION, evidence_diagnostics, make_chunks
from evaluation.pilot.validate_dataset import local_path, validate


def write_json(path, data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')


def percentile95(values):
    return sorted(values)[math.ceil(.95*len(values))-1]


def run(root, output, size=1200, overlap=200, k=10, repeats=5):
    if type(k) is not int or k < 10 or type(repeats) is not int or repeats < 1:
        raise ValueError('Require k >= 10 and repeats >= 1')
    root,output=Path(root),Path(output)
    # Never overwrite the corpus or labels by choosing the dataset as the output folder.
    output=output.resolve()
    if output==root.resolve() or root.resolve().is_relative_to(output):
        raise ValueError('Output cannot be the dataset root or its ancestor')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory is not empty; use a new run directory')
    dataset=validate(root,require_reviewed=True)
    manifest=json.loads((root/'corpus_manifest.json').read_text(encoding='utf-8'))
    questions=[json.loads(l) for l in (root/'questions.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    if not any(q['answerable'] for q in questions):
        raise ValueError('At least one answerable question is needed for evidence diagnostics')
    config=ChunkConfig(size,overlap)
    chunks=[]
    for document in sorted(manifest['documents'],key=lambda d:d['document_id']):
        chunks.extend(make_chunks(document,local_path(root,document['path']).read_bytes(),config))
    index_start=time.perf_counter_ns()
    index=BM25(chunks)
    index_ms=(time.perf_counter_ns()-index_start)/1e6
    rankings=[]
    diagnostics=[]
    all_timings=[]
    for q in questions:
        index.search(q['question'],k)  # warm-up excluded
        timings=[]
        for _ in range(repeats):
            start=time.perf_counter_ns()
            ranked=index.search(q['question'],k)
            timings.append((time.perf_counter_ns()-start)/1e6)
        all_timings.extend(timings)
        retrieved=[c for c,_ in ranked]
        for rank,(chunk,score) in enumerate(ranked,1):
            rankings.append({'question_id':q['question_id'],'rank':rank,'score':score,
                             'chunk_id':chunk.chunk_id,'document_id':chunk.document_id,
                             'start_line':chunk.start_line,'end_line':chunk.end_line})
        diagnostics.append({'question_id':q['question_id'],'category':q['category'],
                            'question':q['question'],'answerable':q['answerable'],
                            'results_returned':len(ranked),
                            'at_5':evidence_diagnostics(q,retrieved[:5]),
                            'at_10':evidence_diagnostics(q,retrieved[:10]),
                            'latency_ms':{'median':statistics.median(timings),'p95':percentile95(timings)}})
    answerable=[d for d in diagnostics if d['answerable']]
    summary={
        'dataset':dataset,'chunks':len(chunks),'answerable_queries':len(answerable),
        'seed_evidence_hit_at_5':sum(d['at_5']['any_known_passage_complete'] for d in answerable)/len(answerable),
        'seed_evidence_hit_at_10':sum(d['at_10']['any_known_passage_complete'] for d in answerable)/len(answerable),
        'mean_seed_passage_character_coverage_at_10':statistics.mean(d['at_10']['mean_passage_character_coverage'] for d in answerable),
        'latency_ms':{'median':statistics.median(all_timings),'p95':percentile95(all_timings)},
        'index_build_ms':index_ms,
        'unanswerable_queries':sum(not d['answerable'] for d in diagnostics),
        'unanswerable_queries_returning_candidates':sum(not d['answerable'] and d['results_returned']>0 for d in diagnostics),
        'interpretation':'Development diagnostics against incomplete AI-reviewed source-span labels; not gold-standard retrieval metrics or answer accuracy.',
    }
    metadata={'method':'bm25','bm25':{'k1':1.2,'b':.75,'query_term_frequency':'binary'},
              'chunking':asdict(config),'preprocessor':PREPROCESSOR_VERSION,'tokenizer':TOKENIZER_VERSION,
              'retrieval_k':k,'timing':{'warmup_per_query':1,'repeats_per_query':repeats,'excludes':'loading, chunking, index building, evidence diagnostics, UI and generation'},
              'python':sys.version.split()[0],'platform':platform.platform(),
              'source_commit':manifest['source_commit'],
              'manifest_sha256':hashlib.sha256((root/'corpus_manifest.json').read_bytes()).hexdigest(),
              'questions_sha256':hashlib.sha256((root/'questions.jsonl').read_bytes()).hexdigest(),
              'implementation_sha256':{name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ['keyword.py','run_keyword.py']},
              'indexed_files':[d['path'] for d in manifest['documents']],
              'attribution':'Corpus text is CPython tutorial content under PSF-2.0; retain evaluation/pilot/ATTRIBUTION.md and licenses/CPYTHON-LICENSE.txt when redistributing chunks.'}
    output.mkdir(parents=True,exist_ok=True)
    write_jsonl(output/'chunks.jsonl',[c.record() for c in chunks])
    write_jsonl(output/'rankings.jsonl',rankings)
    write_json(output/'diagnostics.json',diagnostics)
    write_json(output/'summary.json',summary)
    write_json(output/'run.json',metadata)
    lines=['# Keyword baseline development run','',
           'This run uses the frozen Python tutorial corpus and 20 AI-reviewed development questions. It makes no API calls. Results describe known source-evidence coverage, not answer accuracy or a held-out benchmark.','',
           f'- Source documents: {dataset["documents"]}; searchable chunks: {len(chunks)}.',
           f'- Complete known-passage hit at 5: {summary["seed_evidence_hit_at_5"]:.1%} of {len(answerable)} answerable questions.',
           f'- Complete known-passage hit at 10: {summary["seed_evidence_hit_at_10"]:.1%}.',
           f'- Mean known-passage character coverage at 10: {summary["mean_seed_passage_character_coverage_at_10"]:.1%}.',
           f'- Local warm retrieval median / p95: {summary["latency_ms"]["median"]:.3f} / {summary["latency_ms"]["p95"]:.3f} ms. These exclude ingestion and answer generation.',
           f'- Unanswerable questions returning candidates: {summary["unanswerable_queries_returning_candidates"]}/4. Lexical matches are not evidence that these questions are answerable.','',
           '## What these numbers mean','',
           'A hit requires the union of retrieved source intervals to cover an entire annotated positive passage, not just touch it. Overlaps are counted once. Any one known passage is sufficient for the hit diagnostic, so this does not establish complete answers for multi-part questions. The separate character-coverage diagnostic averages coverage over annotated passages; some are alternatives and some are complementary. Unlabeled passages remain unjudged. There are no nDCG, MRR, gold recall, or generation scores yet.','',
           '## Per-question diagnostics','',
           '| Question | Category | Hit at 5 | Hit at 10 | Passage coverage at 10 |',
           '|---|---|---|---|---|']
    for d in diagnostics:
        a,b=d['at_5'],d['at_10']
        lines.append(f'| {d["question_id"]} | {d["category"]} | {"yes" if a and a["any_known_passage_complete"] else "no" if a else "n/a"} | {"yes" if b and b["any_known_passage_complete"] else "no" if b else "n/a"} | {format(b["mean_passage_character_coverage"],".1%") if b else "n/a"} |')
    lines+=['','## Inspect the retrieved evidence','',
            'Source excerpts below retain the Python Software Foundation attribution and PSF-2.0 license described in run.json and evaluation/pilot/ATTRIBUTION.md. Line numbers refer to the pinned source files, not PDF pages.','']
    by_id={c.chunk_id:c for c in chunks}
    for q in questions:
        lines += [f'### {q["question_id"]}','',q['question'],'']
        for r in [r for r in rankings if r['question_id']==q['question_id']][:3]:
            c=by_id[r['chunk_id']]
            lines += [f'**Rank {r["rank"]}: {c.document_id}, source lines {c.start_line}-{c.end_line}** (BM25 {r["score"]:.3f})','',
                      '````text',c.text[:650]+(' ...' if len(c.text)>650 else ''),'````','']
    lines+=['## Next checks','',
            'Inspect failures and partial-coverage cases before changing retrieval settings. Some misses can reflect chunk boundaries or alternative evidence rather than irrelevant retrieval. Add judged alternatives from the candidate pool; keep a record of label changes and rerun against the new label hash. Freeze a shared chunk configuration for later dense/hybrid comparisons. Add a genuine held-out set before claiming generalization.','']
    (output/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=Path('evaluation/pilot'))
    parser.add_argument('--output',type=Path,default=Path('evaluation/pilot/runs/bm25-v1'))
    parser.add_argument('--chunk-size',type=int,default=1200)
    parser.add_argument('--overlap',type=int,default=200)
    args=parser.parse_args()
    try:
        print(json.dumps(run(args.dataset,args.output,args.chunk_size,args.overlap),indent=2))
    except (ValueError,OSError) as exc:
        parser.exit(1,f'Baseline failed: {exc}\n')
