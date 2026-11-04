# Semantic and hybrid comparison in plain language

The comparison is complete. All methods searched the same 250 source chunks for the same 20 development questions, with no label changes. The embedding model ran locally on CPU. No paid APIs were used.

## Results

The denominator below is the 16 questions with annotated answers; the four unanswerable questions are handled separately.

| Search method | Complete known passage within top 5 | Complete known passage within top 10 |
|---|---:|---:|
| Keyword BM25 | 11/16 | 13/16 |
| Semantic BGE | 13/16 | 15/16 |
| Hybrid BM25 + BGE | 13/16 | 14/16 |

These are strict source-passage coverage diagnostics against incomplete AI-reviewed labels. They are not answer accuracy or results on unseen questions. A question counts as a hit if retrieved chunks jointly cover at least one full annotated passage; this does not require every part of a multi-part answer.

## What we learned

**Semantic search helped find the virtual-environment explanation.** For the question about two applications needing different package versions, dense rank 1 was the introduction to virtual environments and rank 2 continued that explanation. Keyword rank 1 instead discussed installing a specific package version. Hybrid boosted package-installation passages and did not cover the complete annotated explanation in its top ten.

**Semantic search recovered floating-point evidence.** The decimal-equality question did not reach either labeled passage in BM25's top ten. Dense and hybrid covered known evidence in their top ten. Dense rank 1 showed math.isclose and related floating-point discussion; hybrid rank 1 was less directly useful. A top-ten evidence hit should not be confused with having the best first result.

**Hybrid was not automatically better.** Equal-weight rank fusion rescued one complete-passage hit that dense missed but lost two hits dense obtained. We kept the first fixed configuration instead of tuning weights after seeing scores.

**Some differences are annotation-boundary effects.** For the dictionary-key question, all three methods had the same useful rank-1 passage. Dense additionally retrieved enough preceding context somewhere in its top ten to cover the full seed label, while the other methods did not. That difference alone does not show a better answer. Candidate review should judge sufficient evidence, not reward irrelevant introductory lines.

**Unanswerable queries still produced results.** All methods returned candidates for all four such questions. Search similarities and fusion scores do not establish that an answer is supported. Answerability remains a separate task.

## Cost and reproducibility

- Model: BAAI/bge-small-en-v1.5, pinned quantized ONNX export, MIT license.
- 384-dimensional embeddings; CPU only; model weights about 67 MB.
- All 250 passages fit within 512 tokens; no source input was truncated.
- Exact model revision, file hashes, package versions and timing scope are in run.json.
- embeddings.npz stores the document and query vectors. Model-free replay recomputes 600 ranked results (20 questions x 3 methods x 10 results).
- This run used no generative model to answer the questions. Its output is ranked source passages.

## What is next

The run saved a deduplicated pool of 384 candidate passages in pool.jsonl. Their judgments are explicitly unjudged, not assumed irrelevant. Review this pool against the questions to build defensible relevance judgments before calculating nDCG, MRR or recall. Then consider a reranker and a separate held-out question set. The user does not need to manually edit JSON to inspect the current findings.

Source excerpts in the detailed report and pool retain Python Software Foundation attribution and PSF-2.0 terms; see ../../ATTRIBUTION.md.
