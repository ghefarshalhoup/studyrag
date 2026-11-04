# Local reranker: AI-reviewed development comparison

All four methods are rescored on the same expanded pool of 430 question/passage pairs (46 newly judged). Original rankings and existing judgments are unchanged. All top-10 results have explicit judgments.

| Method | nDCG@10 | MRR@10 >=1 | Direct MRR@10 | P@10 | Pooled recall@10 | Direct top-1 |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 0.718 | 0.897 | 0.803 | 0.281 | 0.714 | 12/16 |
| dense | 0.812 | 0.896 | 0.896 | 0.369 | 0.865 | 13/16 |
| hybrid | 0.788 | 0.969 | 0.875 | 0.325 | 0.796 | 13/16 |
| reranked_hybrid | 0.844 | 1.000 | 0.969 | 0.350 | 0.828 | 15/16 |

## Method and interpretation

- The frozen MiniLM cross-encoder scores the fused top 50 candidates from BM25 top 50 plus dense top 50, equal-weight RRF constant 60. The top 10 reranker logits are returned. No query rewrite, answer generation, model training or alternative model trial was used.
- The configuration was frozen before scoring. The 16 prospective held-out questions remain unexecuted; results here concern the original 20 development questions only. All macro averages use the 16 answerable questions.
- nDCG ideal rankings and pooled-recall denominators now include new positives introduced by the fourth method. Therefore these numbers must not be compared directly with the older three-method report. That report remains a historical snapshot.
- Grade 1 is supporting context, grade 2 direct evidence for at least one answer component. MRR >=1 and grade-2-only MRR are separate. nDCG uses gain 2^grade-1 and log2(rank+1) discounts. Precision divides by 10. Pooled recall counts only positives in this four-method top-10 union.
- Judgments are from the same AI that authored questions and saw earlier summaries, without independent human validation. Overlapping chunks can repeat evidence. A direct hit does not establish full multi-part answer coverage, reliable citations or good generated answers.
- Four unanswerable questions have zero positives and undefined nDCG/recall; they are excluded from macro averages. Returning candidates is not a measured abstention failure.
- Local CPU reranking median: 3081.4 ms per 50-candidate query. One timed pass per question; excludes first-stage retrieval and model loading. Model loading: 138.0 ms. These timings are descriptive, not a controlled speed comparison with earlier runs.
- Pair context is limited to 512 tokens. 8/1000 scored pairs had passage-tail truncation; queries were preserved. Maximum original pair length: 535. Returned source passages retain their full text. Raw logits are not confidence probabilities.

## Per-question scores

| Question | Method | nDCG@10 | Direct MRR@10 | Top-1 grade |
|---|---|---:|---:|---:|
| pilot-001 | bm25 | 0.819 | 1.000 | 2 |
| pilot-001 | dense | 0.967 | 1.000 | 2 |
| pilot-001 | hybrid | 1.000 | 1.000 | 2 |
| pilot-001 | reranked_hybrid | 0.704 | 1.000 | 2 |
| pilot-002 | bm25 | 0.907 | 1.000 | 2 |
| pilot-002 | dense | 0.549 | 0.333 | 0 |
| pilot-002 | hybrid | 0.834 | 1.000 | 2 |
| pilot-002 | reranked_hybrid | 0.907 | 1.000 | 2 |
| pilot-003 | bm25 | 0.966 | 1.000 | 2 |
| pilot-003 | dense | 0.835 | 1.000 | 2 |
| pilot-003 | hybrid | 0.899 | 1.000 | 2 |
| pilot-003 | reranked_hybrid | 1.000 | 1.000 | 2 |
| pilot-004 | bm25 | 0.613 | 1.000 | 2 |
| pilot-004 | dense | 0.798 | 1.000 | 2 |
| pilot-004 | hybrid | 0.807 | 1.000 | 2 |
| pilot-004 | reranked_hybrid | 0.877 | 1.000 | 2 |
| pilot-005 | bm25 | 0.802 | 1.000 | 2 |
| pilot-005 | dense | 0.906 | 1.000 | 2 |
| pilot-005 | hybrid | 0.833 | 1.000 | 2 |
| pilot-005 | reranked_hybrid | 0.972 | 1.000 | 2 |
| pilot-006 | bm25 | 0.874 | 1.000 | 2 |
| pilot-006 | dense | 0.482 | 1.000 | 2 |
| pilot-006 | hybrid | 0.662 | 1.000 | 2 |
| pilot-006 | reranked_hybrid | 0.496 | 1.000 | 2 |
| pilot-007 | bm25 | 0.893 | 1.000 | 2 |
| pilot-007 | dense | 0.899 | 1.000 | 2 |
| pilot-007 | hybrid | 0.968 | 1.000 | 2 |
| pilot-007 | reranked_hybrid | 0.974 | 1.000 | 2 |
| pilot-008 | bm25 | 0.797 | 0.500 | 1 |
| pilot-008 | dense | 1.000 | 1.000 | 2 |
| pilot-008 | hybrid | 0.797 | 0.500 | 1 |
| pilot-008 | reranked_hybrid | 0.797 | 0.500 | 1 |
| pilot-009 | bm25 | 0.500 | 0.250 | 0 |
| pilot-009 | dense | 0.826 | 1.000 | 2 |
| pilot-009 | hybrid | 0.889 | 1.000 | 2 |
| pilot-009 | reranked_hybrid | 0.649 | 1.000 | 2 |
| pilot-010 | bm25 | 0.945 | 1.000 | 2 |
| pilot-010 | dense | 0.659 | 0.500 | 0 |
| pilot-010 | hybrid | 1.000 | 1.000 | 2 |
| pilot-010 | reranked_hybrid | 1.000 | 1.000 | 2 |
| pilot-011 | bm25 | 0.070 | 0.100 | 0 |
| pilot-011 | dense | 0.794 | 1.000 | 2 |
| pilot-011 | hybrid | 0.462 | 0.500 | 0 |
| pilot-011 | reranked_hybrid | 0.693 | 1.000 | 2 |
| pilot-012 | bm25 | 0.223 | 0.000 | 1 |
| pilot-012 | dense | 0.984 | 1.000 | 2 |
| pilot-012 | hybrid | 0.263 | 0.000 | 1 |
| pilot-012 | reranked_hybrid | 0.986 | 1.000 | 2 |
| pilot-013 | bm25 | 0.967 | 1.000 | 2 |
| pilot-013 | dense | 1.000 | 1.000 | 2 |
| pilot-013 | hybrid | 1.000 | 1.000 | 2 |
| pilot-013 | reranked_hybrid | 0.967 | 1.000 | 2 |
| pilot-014 | bm25 | 0.556 | 1.000 | 2 |
| pilot-014 | dense | 0.966 | 1.000 | 2 |
| pilot-014 | hybrid | 0.622 | 1.000 | 2 |
| pilot-014 | reranked_hybrid | 0.987 | 1.000 | 2 |
| pilot-015 | bm25 | 0.823 | 1.000 | 2 |
| pilot-015 | dense | 0.606 | 1.000 | 2 |
| pilot-015 | hybrid | 0.711 | 1.000 | 2 |
| pilot-015 | reranked_hybrid | 0.656 | 1.000 | 2 |
| pilot-016 | bm25 | 0.740 | 1.000 | 2 |
| pilot-016 | dense | 0.722 | 0.500 | 0 |
| pilot-016 | hybrid | 0.863 | 1.000 | 2 |
| pilot-016 | reranked_hybrid | 0.834 | 1.000 | 2 |
| pilot-017 | bm25 | n/a | 0.000 | 0 |
| pilot-017 | dense | n/a | 0.000 | 0 |
| pilot-017 | hybrid | n/a | 0.000 | 0 |
| pilot-017 | reranked_hybrid | n/a | 0.000 | 0 |
| pilot-018 | bm25 | n/a | 0.000 | 0 |
| pilot-018 | dense | n/a | 0.000 | 0 |
| pilot-018 | hybrid | n/a | 0.000 | 0 |
| pilot-018 | reranked_hybrid | n/a | 0.000 | 0 |
| pilot-019 | bm25 | n/a | 0.000 | 0 |
| pilot-019 | dense | n/a | 0.000 | 0 |
| pilot-019 | hybrid | n/a | 0.000 | 0 |
| pilot-019 | reranked_hybrid | n/a | 0.000 | 0 |
| pilot-020 | bm25 | n/a | 0.000 | 0 |
| pilot-020 | dense | n/a | 0.000 | 0 |
| pilot-020 | hybrid | n/a | 0.000 | 0 |
| pilot-020 | reranked_hybrid | n/a | 0.000 | 0 |

## Reproduce

Replay candidates and logits without a model: `python -m evaluation.run_reranker --verify`.
Recompute metrics: `python -m evaluation.score_reranker --output evaluation/pilot/runs/my-reranker-metrics`.
Use a new output directory. See evaluation/RERANKER.md for the frozen model download, inference command, review protocol and limits.
