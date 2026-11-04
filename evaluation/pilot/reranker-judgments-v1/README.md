# Expanded development passage review

This review extends [judgments-v1](../judgments-v1/README.md) to include the reranked method's top 10. All 384 existing decisions are retained without changing their grades, explanations or metadata. Codex reviewed the 46 new question/passage pairs using the same rubric: 0 irrelevant, 1 useful supporting context, 2 direct evidence for at least one requested answer component.

The new passages were displayed by question with full source text and source line ranges, without their numerical scores or ranks. The reviewer knew they were new reranker results and had seen earlier development summaries. This is not blinded or independent review. The same AI authored the questions. No human validation is claimed.

Of the 46 new pairs, one is grade 2 and 45 are grade 0. The positive passage explains the actual binary approximation stored for 0.1 in pilot-011; it does not give the requested comparison helper. Newly retrieved examples about Python modules, list comprehensions or generic exceptions do not answer the unrelated questions merely because they share vocabulary. In particular, a success-only file-closing example does not establish exception-safe closing.

The expanded pool contains **430 pairs: 358 grade 0, 28 grade 1, 44 grade 2**. Positive decisions have verbatim supporting excerpts and all decisions identify the normalized passage text by hash. `qrels.jsonl` is the authoritative review file. Source text and retrieval provenance remain in `runs/reranker-v1/pool.jsonl`, under the existing CPython attribution and license.

Every top-10 result from all four methods is judged. Metrics must be recalculated for every method on this expanded pool: nDCG's ideal ranking and pooled recall's denominator can change when new positives are discovered. These are development retrieval metrics with overlapping chunks, incomplete full-corpus judgments, and no generated-answer evaluation. None of the held-out questions was run or passage-judged during this stage.
