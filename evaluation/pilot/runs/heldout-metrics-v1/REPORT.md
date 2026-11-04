# Final held-out retrieval check

The fixed comparison executed all 16 reserved questions after locking implementation, model configuration and input hashes. Quality metrics were calculated only after explicit AI review of all 323 pooled question/passage pairs. No configuration was selected or tuned using these results.

Macro averages below cover 12 answerable questions. The 4 unanswerable questions have undefined nDCG/recall and are reported separately.

| Method | nDCG@10 | MRR@10 >=1 | Direct MRR@10 | P@10 | Pooled recall@10 | Direct first |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 0.812 | 0.875 | 0.806 | 0.283 | 0.925 | 9/12 |
| dense | 0.692 | 0.806 | 0.711 | 0.258 | 0.808 | 7/12 |
| hybrid | 0.804 | 0.896 | 0.757 | 0.292 | 0.942 | 7/12 |
| reranked_hybrid | 0.814 | 0.847 | 0.764 | 0.283 | 0.928 | 7/12 |

## Limits and interpretation

- This was a prospective holdout for the final configuration. Its questions were created after earlier development findings, on the same previously inspected corpus. Families differ from development questions, but documents and some source passages are shared. Neither independent authorship nor absence of model pretraining contamination is established.
- Codex authored the questions, inspected source documents and performed the passage review, without independent human validation. Candidate review displays omit method, rank and score; this is not an independent or fully blinded evaluation.
- Grade 0 is irrelevant, grade 1 useful supporting context, grade 2 direct evidence for at least one requested component. Direct evidence at rank 1 does not prove complete multi-part answers. nDCG gains are 2^grade-1 with log2(rank+1) discounts. MRR >=1 and grade-2-only MRR are separate.
- Ideal nDCG rankings and recall denominators use this four-method top-10 union. Pooled recall is not exhaustive corpus recall. Chunks overlap and can repeat facts. All returned top-10 passages are judged; no unjudged passage is treated as irrelevant.
- All methods return candidates for the four missing-detail questions. This retrieval check does not generate answers, test citation support or measure abstention behavior.
- The reranker scored 800 pairs. 10 pairs exceeded 512 tokens (maximum 537); only passage tails were truncated for scoring, and queries were preserved. Returned passages retain full text.
- Timings below are descriptive CPU measurements, one timed pass per question, with development-only warmup. Query encoding is included in dense timings. Model loading, disk output and review are excluded. No paid API was called.

## Timing

| Method | Median query ms |
|---|---:|
| bm25 | 0.39 |
| dense | 13.08 |
| hybrid | 13.51 |
| reranked_hybrid | 3414.75 |

## Per-question results

| Question | Method | nDCG@10 | Direct MRR@10 | Top-1 grade |
|---|---|---:|---:|---:|
| heldout-001 | bm25 | 0.519 | 0.250 | 0 |
| heldout-001 | dense | 0.765 | 1.000 | 2 |
| heldout-001 | hybrid | 0.634 | 0.500 | 0 |
| heldout-001 | reranked_hybrid | 0.618 | 0.333 | 0 |
| heldout-002 | bm25 | 0.496 | 0.167 | 1 |
| heldout-002 | dense | 0.692 | 0.500 | 0 |
| heldout-002 | hybrid | 0.732 | 0.500 | 1 |
| heldout-002 | reranked_hybrid | 0.773 | 0.500 | 1 |
| heldout-003 | bm25 | 0.874 | 1.000 | 2 |
| heldout-003 | dense | 0.604 | 0.333 | 0 |
| heldout-003 | hybrid | 0.862 | 1.000 | 2 |
| heldout-003 | reranked_hybrid | 0.544 | 0.333 | 0 |
| heldout-004 | bm25 | 0.989 | 1.000 | 2 |
| heldout-004 | dense | 0.908 | 1.000 | 2 |
| heldout-004 | hybrid | 1.000 | 1.000 | 2 |
| heldout-004 | reranked_hybrid | 1.000 | 1.000 | 2 |
| heldout-005 | bm25 | 0.913 | 1.000 | 2 |
| heldout-005 | dense | 0.947 | 1.000 | 2 |
| heldout-005 | hybrid | 1.000 | 1.000 | 2 |
| heldout-005 | reranked_hybrid | 0.922 | 1.000 | 2 |
| heldout-006 | bm25 | 0.888 | 1.000 | 2 |
| heldout-006 | dense | 0.401 | 0.200 | 1 |
| heldout-006 | hybrid | 0.712 | 0.500 | 1 |
| heldout-006 | reranked_hybrid | 0.536 | 0.500 | 1 |
| heldout-007 | bm25 | 0.964 | 1.000 | 2 |
| heldout-007 | dense | 0.098 | 0.000 | 0 |
| heldout-007 | hybrid | 0.689 | 0.333 | 1 |
| heldout-007 | reranked_hybrid | 1.000 | 1.000 | 2 |
| heldout-008 | bm25 | 1.000 | 1.000 | 2 |
| heldout-008 | dense | 0.964 | 1.000 | 2 |
| heldout-008 | hybrid | 1.000 | 1.000 | 2 |
| heldout-008 | reranked_hybrid | 0.964 | 1.000 | 2 |
| heldout-009 | bm25 | 1.000 | 1.000 | 2 |
| heldout-009 | dense | 1.000 | 1.000 | 2 |
| heldout-009 | hybrid | 1.000 | 1.000 | 2 |
| heldout-009 | reranked_hybrid | 1.000 | 1.000 | 2 |
| heldout-010 | bm25 | 0.264 | 0.250 | 0 |
| heldout-010 | dense | 0.613 | 1.000 | 2 |
| heldout-010 | hybrid | 0.501 | 0.250 | 0 |
| heldout-010 | reranked_hybrid | 1.000 | 1.000 | 2 |
| heldout-011 | bm25 | 1.000 | 1.000 | 2 |
| heldout-011 | dense | 0.387 | 0.500 | 0 |
| heldout-011 | hybrid | 0.613 | 1.000 | 2 |
| heldout-011 | reranked_hybrid | 0.877 | 1.000 | 2 |
| heldout-012 | bm25 | 0.840 | 1.000 | 2 |
| heldout-012 | dense | 0.922 | 1.000 | 2 |
| heldout-012 | hybrid | 0.906 | 1.000 | 2 |
| heldout-012 | reranked_hybrid | 0.531 | 0.500 | 0 |
| heldout-013 | bm25 | n/a | 0.000 | 0 |
| heldout-013 | dense | n/a | 0.000 | 0 |
| heldout-013 | hybrid | n/a | 0.000 | 0 |
| heldout-013 | reranked_hybrid | n/a | 0.000 | 0 |
| heldout-014 | bm25 | n/a | 0.000 | 0 |
| heldout-014 | dense | n/a | 0.000 | 0 |
| heldout-014 | hybrid | n/a | 0.000 | 0 |
| heldout-014 | reranked_hybrid | n/a | 0.000 | 0 |
| heldout-015 | bm25 | n/a | 0.000 | 0 |
| heldout-015 | dense | n/a | 0.000 | 0 |
| heldout-015 | hybrid | n/a | 0.000 | 0 |
| heldout-015 | reranked_hybrid | n/a | 0.000 | 0 |
| heldout-016 | bm25 | n/a | 0.000 | 0 |
| heldout-016 | dense | n/a | 0.000 | 0 |
| heldout-016 | hybrid | n/a | 0.000 | 0 |
| heldout-016 | reranked_hybrid | n/a | 0.000 | 0 |

## Reproduce without model calls

`python -m evaluation.run_holdout --verify` replays all rankings from the saved query vectors and reranker logits.
`python -m evaluation.score_holdout --output evaluation/pilot/runs/my-final-metrics` recalculates this report. Use a fresh directory. See evaluation/FINAL_CHECK.md for protocol and inference details.

Further choices based on these results make this set development data for those choices. Preserve this run and use a new set for a later final check.
