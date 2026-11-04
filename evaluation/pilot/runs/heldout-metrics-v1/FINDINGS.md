# Final check: the development gain did not clearly carry over

**Reranking has no clear advantage over BM25 in this small final check.** Its nDCG@10 is 0.814 versus 0.812 for BM25, while adding roughly 3.4 seconds of CPU processing per query. BM25 also puts direct evidence first more often on these questions. The development-stage gain should not be presented as a general improvement.

The comparison used the 16 previously reserved questions with unchanged model settings, chunks and retrieval configuration. Twelve questions are answerable in the tutorial corpus; four ask for details it does not specify. All 323 question/passage pairs in the four-method top-10 union received explicit AI relevance grades before metric calculation. No reranker, threshold, prompt, depth or fusion-weight alternative was tried after inspecting these results.

## Results on the 12 answerable questions

| Method | nDCG@10 | Direct MRR@10 | Direct evidence first | Pooled recall@10 |
|---|---:|---:|---:|---:|
| BM25 | 0.812 | **0.806** | **9/12** | 0.925 |
| Dense | 0.692 | 0.711 | 7/12 | 0.808 |
| Hybrid | 0.804 | 0.757 | 7/12 | **0.942** |
| Reranked hybrid | 0.814 | 0.764 | 7/12 | 0.928 |

The 0.0014 nDCG gap between reranked hybrid and BM25 is too small to establish a reliable winner from this 12-question, AI-reviewed sample. This is a descriptive comparison, not a statistical-superiority claim. All methods retrieve some direct evidence within their top 10 for all 12 answerable questions except dense, which does so for 11.

The source corpus, question mix and judged pool differ in role from the development runs; compare methods within this final report rather than interpreting a development-to-test score change as a controlled causal effect. Pooled recall counts only relevant chunks found in the four-method union. It is not full-corpus recall. Overlapping chunks can support the same fact more than once.

## What worked and what failed

- **Exception chaining, heldout-007:** dense retrieves no grade-2 direct answer in its top 10. BM25 and reranked hybrid put direct evidence first. Reranking raises hybrid nDCG from 0.689 to 1.000.
- **Weak-reference caches, heldout-010:** reranking raises hybrid nDCG from 0.501 to 1.000 and moves direct evidence from rank 4 to rank 1. BM25 also has its first direct evidence at rank 4; dense finds it first.
- **Variadic argument containers, heldout-003:** reranking demotes direct evidence from hybrid rank 1 to rank 3. nDCG falls from 0.862 to 0.544. Related call/unpacking examples do not fully identify the tuple/dictionary collection types.
- **Exception-handler ordering, heldout-006:** BM25 puts direct evidence first. Hybrid and reranked hybrid first do so at rank 2, and reranking lowers nDCG from 0.712 to 0.536.
- **Name mangling, heldout-012:** reranking lowers hybrid nDCG from 0.906 to 0.531 and moves the first direct evidence from rank 1 to rank 2. A passage about class mechanics or attribute conventions can be related without explaining the requested renaming rule.
- **Regular expressions, heldout-009:** every method places the relevant passage first. Reranking offers no quality improvement for this case.

These examples support a practical reading: exact API terms remain useful retrieval signals in a small programming-document corpus, while the reranker helps some semantic cases and harms others. This is an inference from these examples, not an explanation of the models' internal reasoning or a general rule for other datasets.

## Runtime and missing-answer cases

Recorded median times, one timed CPU pass per question:

| Method | Median query time |
|---|---:|
| BM25 | 0.39 ms |
| Dense, including query encoding | 13.08 ms |
| Hybrid | 13.51 ms |
| Reranked hybrid, including first-stage retrieval | 3,414.75 ms |

Model loading and the initial development-query warmup are excluded. Timings are descriptive measurements on this machine. Of the 800 reranker pairs, 10 exceeded the 512-token context (maximum 537); only passage tails were truncated for scoring, with full queries preserved. Returned passages retain their full text.

The four missing-detail questions concern HTTP-429 retries, multiprocessing start methods, garbage-collector thresholds and native struct sizing. Every method returns candidates, all judged grade 0 for these requested details. This is not a measured abstention failure: this experiment does not generate answers or decide whether to abstain.

## What is defensible in the portfolio

The project demonstrates frozen data/configuration, shared source-traceable chunks, four retrieval approaches, explicit pooled relevance judgments, test/development separation, runtime measurements, failure analysis and offline reproduction. A useful interview account is that a reranker improved development results but did not establish a worthwhile gain on the reserved final questions, so the evaluation exposed the tradeoff.

The questions and labels are AI-authored/reviewed on an already inspected corpus. This was a prospective same-corpus holdout, not independent human gold, a new-document/domain test, or proof of pretraining-data isolation. Direct evidence can cover one component of a question; it does not establish complete answers, citation correctness or reliable abstention.

The retrieval comparison stage is complete. Preserve these results. Any further tuning informed by them needs a new final-check set. The next portfolio work is packaging and independent spot-checking of judgments, rather than trying more configurations on these questions.

See [the full report](REPORT.md), [execution and reproduction protocol](../../../FINAL_CHECK.md), and [passage-review protocol](../../heldout-judgments-v1/README.md).
