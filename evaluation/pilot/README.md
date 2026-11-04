# StudyRAG retrieval evaluation

This package contains frozen source documents, 20 AI-reviewed development questions, reproducible retrieval runs and passage-level relevance judgments. The final check on 16 separately frozen questions is complete. Start with [START_HERE.md](START_HERE.md) for the shortest path through the results.

## Current results and protocols

| Stage | What it establishes | Read |
|---|---|---|
| BM25 baseline | Stable chunks and known-source-span coverage | [Baseline notes](runs/bm25-v1/BASELINE_NOTES.md) |
| Dense + hybrid | Same corpus/chunks, local BGE embeddings and RRF | [Comparison notes](runs/comparison-v1/COMPARISON_NOTES.md) |
| Graded three-method comparison | 384 explicit AI passage judgments, reproducible ranking metrics | [Findings](runs/metrics-v1/FINDINGS.md) |
| Reranked hybrid | One frozen MiniLM configuration, shared expanded pool of 430 judged pairs | [Reranker findings](runs/reranker-metrics-v1/FINDINGS.md) |
| Final same-corpus holdout | 12 answerable + 4 unanswerable questions, fixed configuration and 323 pooled passage judgments | [Final findings](runs/heldout-metrics-v1/FINDINGS.md) |

These are retrieval experiments. They do not establish generated-answer accuracy, citation quality or abstention reliability. Development and final-check results use separate questions, with AI judgments and no independent human validation. Recall is limited to the judged pool, and overlapping chunks may repeat a fact.

## Corpus

The corpus consists of 12 unmodified RST chapters from the official Python tutorial at CPython v3.13.0, commit `60403a5409ff2c3f3b07dd2ca91a7a3e096839c7`. It covers Python foundations, data structures, files, modules, exceptions, classes, standard-library tools, virtual environments and floating-point arithmetic. Chunking produces 250 stable, source-traceable passages.

`corpus_manifest.json` records the source bytes, sizes, SHA-256 hashes and URLs. See [ATTRIBUTION.md](ATTRIBUTION.md) and [the CPython license](licenses/CPYTHON-LICENSE.txt). These third-party texts retain their original terms and are not relicensed under the project's MIT license.

Only manifest-listed source documents are indexed. Questions, reference answers, review notes, annotations and licenses must not enter the search index. Source RST lines provide provenance; they are not PDF page numbers. The app's PDF/DOCX ingestion path is separate from this benchmark adapter.

## Development data and review

The original 20 questions contain 16 answerable and four out-of-scope cases. Categories include exact terms, paraphrases, typos in prose, shorthand and multi-source questions. They remain development data and must not be relabeled as a held-out set after inspecting results.

- `questions.jsonl` is the authoritative question/reference-evidence store.
- [AI_REVIEW.md](AI_REVIEW.md) documents the source-based corrections. Status `ai_reviewed` is distinct from human acceptance.
- [REVIEW.md](REVIEW.md) is an optional readable snapshot; [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md) describes the original seed-evidence protocol.
- [judgments-v1](judgments-v1/README.md) records the initial three-method pool's 384 explicit passage grades.
- [reranker-judgments-v1](reranker-judgments-v1/README.md) retains those decisions and adds the 46 new pairs from reranked results.
- [heldout-judgments-v1](heldout-judgments-v1/README.md) records all 323 final-check question/passage pairs separately, using the same rubric.

Seed source spans are incomplete labels. The later pooled passage judgments evaluate actual returned chunks and can recognize sufficient evidence that the exact-span diagnostic misses. Every compared top-10 result must be explicitly judged; unjudged passages are not implicit negatives.

## Offline validation and reproduction

From the repository root:

```powershell
python evaluation/pilot/validate_dataset.py --require-reviewed
python -m evaluation.validate_holdout
python -m evaluation.run_metrics --output evaluation/pilot/runs/my-metrics
python -m evaluation.run_reranker --verify
python -m evaluation.score_reranker --output evaluation/pilot/runs/my-reranker-metrics
python -m evaluation.run_holdout --verify
python -m evaluation.score_holdout --output evaluation/pilot/runs/my-final-metrics
```

Choose fresh output directories. Dataset validation and three-method metric scoring use the standard library. Reranker replay and four-method scoring also use NumPy to verify saved vectors. No command above requires an API key, model download or inference. See [SEMANTIC_COMPARISON.md](../SEMANTIC_COMPARISON.md) and [RERANKER.md](../RERANKER.md) for optional local model inference.

Run regression checks with `python -m pytest tests evaluation/pilot/test_dataset.py`. Tests cover source integrity, stable retrieval, saved-vector/logit replay, analytical metric formulas, incomplete judgments and the held-out freeze.

## Boundaries

The prospective holdout has new question families, shared corpus documents and AI-authored labels. It was created after earlier development findings and does not establish independent authorship or pretraining-data isolation. The final configuration and implementation were locked before execution; [FINAL_CHECK.md](../FINAL_CHECK.md) documents the completed run. If its results inform later changes, treat it as development data for those changes and create new final-check data.

The original [synthetic robustness suite](../README.md) remains separate. No false documents or conflicting-source experiments were added here. Known Python facts may be memorized by language models; future answer evaluation must require both factual correctness and source support.
