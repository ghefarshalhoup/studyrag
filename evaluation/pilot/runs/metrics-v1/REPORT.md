# AI-reviewed pooled development ranking metrics

These scores use the saved BM25, dense and hybrid top-10 rankings. Retrieval was not rerun or tuned during this review. No answer generation or paid API was used.

384 unique question/passage pairs were judged. All top-10 results are covered. Macro averages below include only the 16 answerable development questions.

| Method | nDCG@10 | MRR@10 (grade >=1) | Direct MRR@10 (grade 2) | P@10 | Pooled recall@10 | Direct evidence at 1 |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 0.719 | 0.897 | 0.803 | 0.281 | 0.714 | 12/16 |
| dense | 0.816 | 0.896 | 0.896 | 0.369 | 0.871 | 13/16 |
| hybrid | 0.790 | 0.969 | 0.875 | 0.325 | 0.799 | 13/16 |

## Definitions and limits

- Grade 0: irrelevant; grade 1: useful supporting context; grade 2: direct evidence for at least one requested answer component. A grade-2 hit does not establish a complete multi-part answer.
- nDCG@10 uses gain 2^grade - 1, discount log2(rank + 1), and an ideal ranking drawn from the judged pool for that question.
- MRR@10 uses the first grade >=1 result. Direct MRR@10 requires grade 2, making the difference between background and direct answers visible.
- Precision@10 uses a denominator of 10. Pooled recall@10 divides retrieved positives by positives in the union of these three methods' top 10, not by all relevant passages in the corpus. New methods must have their new results judged before comparison.
- Four questions labeled unanswerable have no positive judgments. Their nDCG and recall are undefined and they are excluded from all macro averages. All three methods still returned ten candidates for each. This experiment does not test answer abstention.
- Chunks overlap and are not independent evidence units. Multiple chunks can support the same fact; passage recall and nDCG are sensitive to this duplication. The earlier source-span coverage diagnostics remain available separately.
- Codex drafted the questions, previously inspected run summaries, and performed this review. These judgments have no independent human validation. Candidate displays omitted methods, ranks and scores, but this was not a blinded or independent evaluation.
- All 20 questions are development data from one small English Python corpus; no held-out generalization or statistical superiority is claimed. These are retrieval metrics, not generated-answer or citation accuracy.

## Per-question ranking quality

| Question | Method | nDCG@10 | MRR@10 | Direct MRR@10 | Pooled recall@10 | Top-1 grade |
|---|---|---:|---:|---:|---:|---:|
| pilot-001 | bm25 | 0.819 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-001 | dense | 0.967 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-001 | hybrid | 1.000 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-002 | bm25 | 0.907 | 1.000 | 1.000 | 0.667 | 2 |
| pilot-002 | dense | 0.549 | 0.333 | 0.333 | 1.000 | 0 |
| pilot-002 | hybrid | 0.834 | 1.000 | 1.000 | 0.667 | 2 |
| pilot-003 | bm25 | 0.966 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-003 | dense | 0.835 | 1.000 | 1.000 | 0.600 | 2 |
| pilot-003 | hybrid | 0.899 | 1.000 | 1.000 | 0.800 | 2 |
| pilot-004 | bm25 | 0.613 | 1.000 | 1.000 | 0.500 | 2 |
| pilot-004 | dense | 0.798 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-004 | hybrid | 0.807 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-005 | bm25 | 0.802 | 1.000 | 1.000 | 0.750 | 2 |
| pilot-005 | dense | 0.906 | 1.000 | 1.000 | 0.750 | 2 |
| pilot-005 | hybrid | 0.833 | 1.000 | 1.000 | 0.750 | 2 |
| pilot-006 | bm25 | 0.874 | 1.000 | 1.000 | 0.750 | 2 |
| pilot-006 | dense | 0.482 | 1.000 | 1.000 | 0.500 | 2 |
| pilot-006 | hybrid | 0.662 | 1.000 | 1.000 | 0.750 | 2 |
| pilot-007 | bm25 | 0.893 | 1.000 | 1.000 | 0.800 | 2 |
| pilot-007 | dense | 0.899 | 1.000 | 1.000 | 0.800 | 2 |
| pilot-007 | hybrid | 0.968 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-008 | bm25 | 0.797 | 1.000 | 0.500 | 1.000 | 1 |
| pilot-008 | dense | 1.000 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-008 | hybrid | 0.797 | 1.000 | 0.500 | 1.000 | 1 |
| pilot-009 | bm25 | 0.500 | 0.250 | 0.250 | 1.000 | 0 |
| pilot-009 | dense | 0.826 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-009 | hybrid | 0.889 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-010 | bm25 | 0.945 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-010 | dense | 0.659 | 0.500 | 0.500 | 1.000 | 0 |
| pilot-010 | hybrid | 1.000 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-011 | bm25 | 0.075 | 0.100 | 0.100 | 0.111 | 0 |
| pilot-011 | dense | 0.857 | 1.000 | 1.000 | 0.889 | 2 |
| pilot-011 | hybrid | 0.499 | 0.500 | 0.500 | 0.444 | 0 |
| pilot-012 | bm25 | 0.223 | 1.000 | 0.000 | 0.400 | 1 |
| pilot-012 | dense | 0.984 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-012 | hybrid | 0.263 | 1.000 | 0.000 | 0.400 | 1 |
| pilot-013 | bm25 | 0.967 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-013 | dense | 1.000 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-013 | hybrid | 1.000 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-014 | bm25 | 0.556 | 1.000 | 1.000 | 0.333 | 2 |
| pilot-014 | dense | 0.966 | 1.000 | 1.000 | 1.000 | 2 |
| pilot-014 | hybrid | 0.622 | 1.000 | 1.000 | 0.667 | 2 |
| pilot-015 | bm25 | 0.823 | 1.000 | 1.000 | 0.571 | 2 |
| pilot-015 | dense | 0.606 | 1.000 | 1.000 | 0.571 | 2 |
| pilot-015 | hybrid | 0.711 | 1.000 | 1.000 | 0.571 | 2 |
| pilot-016 | bm25 | 0.740 | 1.000 | 1.000 | 0.545 | 2 |
| pilot-016 | dense | 0.722 | 0.500 | 0.500 | 0.818 | 0 |
| pilot-016 | hybrid | 0.863 | 1.000 | 1.000 | 0.727 | 2 |
| pilot-017 | bm25 | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-017 | dense | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-017 | hybrid | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-018 | bm25 | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-018 | dense | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-018 | hybrid | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-019 | bm25 | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-019 | dense | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-019 | hybrid | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-020 | bm25 | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-020 | dense | n/a | 0.000 | 0.000 | n/a | 0 |
| pilot-020 | hybrid | n/a | 0.000 | 0.000 | n/a | 0 |
