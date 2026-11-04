# Passage relevance judgments, version 1

Codex reviewed the 384 unique question/chunk pairs in the union of the saved BM25, dense and hybrid top-10 results. There are 186 distinct chunks across those pairs. Judgments are **AI-reviewed development annotations**, not human gold labels. The questions, source documents, chunks and retrieval runs were left unchanged.

## Rubric

- **0 — irrelevant:** does not support the requested answer. A matching word, generic programming concept, or merely related example is insufficient.
- **1 — supporting context:** supplies a useful premise, contrast or related operation, but needs additional evidence to establish a requested answer component. For example, installing a pinned package version helps manage dependencies but does not establish isolation between two applications.
- **2 — direct evidence:** explicitly states or demonstrates at least one requested answer component, including a cause or a fix. It need not answer every part. A passage explaining inexact binary representation can receive 2 even if it omits the requested comparison helper.

Use grade >=1 for ordinary MRR, precision and pooled recall. Report grade-2-only MRR alongside it so that useful background at rank 1 does not look like a direct answer. nDCG uses graded gains of 0, 1 and 3. The rubric was applied to passages as presented to retrieval, without extending their text across chunk boundaries.

## Review record

`qrels.jsonl` contains one explicit decision per pair: stable chunk ID, document and line range, SHA-256 of the normalized passage text, grade, rationale, positive supporting excerpt, review status and reviewer. Every positive excerpt must occur verbatim inside its passage. Grade-0 passages have no supporting excerpt. The text itself remains in the frozen pool, which retains its CPython licensing and attribution.

Candidates were displayed by question and source position with methods, ranks and scores omitted. Repeated chunks were displayed in full on their first occurrence and referenced on later occurrences; question-specific relevance was decided separately. The reviewer had already seen comparison summaries and authored the questions, so this was **not independent or blinded review**. Source-span overlap did not determine passage grades.

The four out-of-scope questions ask about pandas, GridSearchCV, PostgreSQL JSONB and Qdrant. Their candidates contain general Python examples, not the requested APIs. All their passage grades are 0. Negative judgments apply to these candidates; a finite pool alone cannot prove that a topic is absent from the entire corpus. The original source review supplies the separate unanswerable labels.

There are 313 grade-0, 28 grade-1 and 43 grade-2 pairs. A human should independently check a sample, especially borderline grade-1/2 decisions, before these annotations are used for external performance claims. This review is complete for the existing top-10 union; it is incomplete for the full corpus, top-50 candidates or any future method's new passages.

## Interpretation limits

All questions are development data. Overlapping chunks can repeat a fact, making chunk recall and nDCG sensitive to duplicate evidence. A direct passage hit does not prove that all parts of a question can be answered. In particular, pilot-015's pooled results explain default-list sharing and the class-list fix but do not include the None-sentinel default-list fix. Neither MRR nor nDCG measures complete-answer coverage.

Metrics are macro-averaged over the 16 answerable questions only. The four unanswerable questions have undefined nDCG/recall and are reported separately. Retrieving candidates for an unanswerable question is not itself an abstention failure: generation and answerability decisions are outside this experiment.

Run from the repository root, with any Python 3.11+ interpreter:

```powershell
python -m evaluation.run_metrics --output evaluation/pilot/runs/my-metrics
```

Use a new output directory. No API key, model download or optional embedding dependencies are required. The runner validates frozen input hashes, complete judgments, supporting excerpts, unique rankings and method/question coverage before writing any report. Its run manifest records input and implementation hashes. See [the recorded report](../runs/metrics-v1/REPORT.md) and [plain-language findings](../runs/metrics-v1/FINDINGS.md).
