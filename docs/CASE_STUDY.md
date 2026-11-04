# StudyRAG: engineering decisions and evidence

## The problem

A document assistant has two distinct responsibilities: retrieve useful evidence and handle the resulting answer state correctly. A more elaborate retrieval pipeline can improve a development score while making the application slower or failing on different questions.

StudyRAG combines a Python/LangGraph document assistant with a separate, reproducible retrieval evaluation. The work started as an M.Sc. course project and was extended into an engineering portfolio project.

## What the implementation demonstrates

**Document workflow.** PDF/DOCX loading preserves source/page metadata. A linear LangGraph workflow rewrites the question using conversation history, retrieves chunks, grades relevance and generates an answer from accepted context. The UI exposes workflow events and source excerpts. Citation formatting is requested in the prompt; citation correctness is not automatically verified.

**Failure handling.** Two concrete bugs were fixed with regression tests. First, rejecting every retrieved chunk previously caused generation to fall back to the original rejected evidence. Generation now uses only accepted documents; no accepted evidence produces a deterministic abstention and no generation call. Second, the completion event could arrive before conversation memory was committed, causing the non-streaming method to return an earlier answer. Completed answers are now committed before the event, and the method reads the current answer from that event. See [the implementation](../src/rag_agent.py) and [regression tests](../tests/test_agent.py).

**Retrieval experiment.** The corpus is 12 pinned CPython tutorial chapters, split into 250 stable chunks with document IDs, source lines and character offsets. BM25, exact dense cosine search, equal-weight RRF and cross-encoder reranking all use the same chunks. Original document embeddings are reused in the final check; only the new queries are encoded.

**Evaluation discipline.** Twenty questions were development data. Sixteen different question families were frozen prospectively before reranker execution and reserved for the final check. Source/configuration/code hashes, saved query vectors, candidate logits and explicit pooled relevance grades support offline replay. All returned top-10 passages are judged; unjudged results cannot silently become negatives.

## The result that mattered

Reranking raised development nDCG@10 from 0.788 for hybrid to 0.844. That was not enough to justify choosing it without the reserved check.

On the 12 answerable reserved questions:

| Method | nDCG@10 | Direct evidence first | Median query time |
|---|---:|---:|---:|
| BM25 | 0.812 | 9/12 | 0.39 ms |
| Dense | 0.692 | 7/12 | 13.08 ms |
| Hybrid | 0.804 | 7/12 | 13.51 ms |
| Reranked hybrid | 0.814 | 7/12 | 3,414.75 ms |

The final nDCG difference between reranking and BM25 was tiny, and BM25 put direct evidence first more often. Reranking helped exception chaining and weak-reference questions, but demoted useful evidence for variadic arguments, handler ordering and name mangling. The result did not establish a clear benefit for the additional CPU cost. No parameter search was performed on these final results.

## What the results do and do not establish

The final set is a small, prospective **same-corpus** holdout with AI-authored questions and AI-reviewed relevance judgments, without independent human validation. Documents were shared across splits. Pooled recall is not exhaustive corpus recall; overlapping chunks may repeat one fact. Direct evidence can cover only one component of a question. The experiment evaluates retrieval, not generated-answer accuracy, citation support or abstention decisions.

The four missing-detail questions still retrieve candidates, all judged unsupported for the requested details. Returning those candidates alone does not establish an abstention failure.

## Review the evidence

- [Final findings and failure examples](../evaluation/pilot/runs/heldout-metrics-v1/FINDINGS.md)
- [Full metrics and per-question results](../evaluation/pilot/runs/heldout-metrics-v1/REPORT.md)
- [Final execution/reproduction protocol](../evaluation/FINAL_CHECK.md)
- [Passage-review rubric and limits](../evaluation/pilot/heldout-judgments-v1/README.md)
- [Historical course robustness experiment](../evaluation/README.md), kept separate from the reproduced retrieval runs

Ghefar Shalhoup maintains this project. Code and evaluation tooling were extended with Codex assistance; annotation status and limitations are disclosed so reviewers can inspect the evidence rather than infer stronger claims from a headline score.
