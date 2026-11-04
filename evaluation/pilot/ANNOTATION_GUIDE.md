# Annotation guide

## Review task

Decide whether each question is clear, answerable from the frozen corpus, and supported by the proposed evidence. The reference answer is a draft of the expected content, not an exact-match target. Use the source documents, not your general Python knowledge, to determine answerability.

Records begin as `draft`. After source-based AI review, use `ai_reviewed` and name the AI reviewer. Reserve `accepted` for a human decision. Do not mark any label reviewed merely because the structural validator passes. The current records are AI-reviewed; optional human review can correct them.

## Relevance grades

| Grade | Decision |
|---|---|
| 0 | Does not support answering the question, even if it shares topic words. |
| 1 | Provides useful, substantive but incomplete evidence. |
| 2 | Directly supports answering the question or one necessary subquestion. |

For multi-evidence questions, one grade-2 passage may support only one required subquestion. Grade 2 is not a claim that a single passage is sufficient for the entire answer. Later answer-completeness checks must cover both required parts. Topical overlap alone is not grade 1.

Relevance does not determine truth or authority. In the separate contradiction suite, two conflicting passages can both be relevant. Do not add arbitrary trust scores to force an answer.

## Review each record

1. Read the question before the answer. Is the intent natural and unambiguous? Preserve the intended typo or abbreviation rather than correcting it away.
2. Read each source passage and enough surrounding text to understand it. Use the pinned local RST; live documentation can differ.
3. Check that the draft answer is fully supported, does not add an unsupported detail, and makes all required distinctions.
4. Check each evidence grade and rationale. Seek alternative supporting passages in the other 11 chapters; record additional passages when useful. Do not treat absent labels as grade 0.
5. For an unanswerable question, inspect nearby topics as well as searching the named terms. A missing literal term alone does not prove the answer is absent. Keep evidence empty and explain why related text does not answer it.
6. Record `accepted`, `revise`, or `rejected`; enter your reviewer name and review notes. A substantive correction requires reviewing the changed record again before acceptance.

Each `group_id` groups one underlying intent. Future paraphrases must share that group and stay in the same split. The current exposed pilot stays entirely in `dev`. Write future held-out questions separately, freeze them before tuning, and keep their near-duplicates out of development.

## Evidence coordinates

The source file is UTF-8. Normalize CRLF to LF for coordinate calculations; the supplied upstream files use LF. `start_line` and `end_line` are one-based and inclusive. `start_char` is zero-based and inclusive; `end_char` is exclusive. Character offsets count Unicode characters, not bytes. A quote includes the selected complete lines, including the final newline when present.

`question.schema.json` describes record structure. `validate_dataset.py` checks that quotes and coordinates agree with the exact hashed sources. If editing evidence ranges, update both offsets and quote; do not edit the source documents to make a label fit.

These are source-span labels. They are not chunk IDs or exhaustive chunk-level qrels. When chunking is frozen, inspect how a passage is divided; do not grade a chunk 2 solely because it touches a few characters of a grade-2 span. Overlapping chunks can duplicate evidence and inflate conventional chunk recall. Report the unit of relevance and consider distinct-evidence coverage alongside chunk metrics.

## Before scoring

- Every included record must have a recorded review. AI-reviewed labels are sufficient for provisional development experiments when disclosed as such. Human review is recommended before presenting labels as a gold-standard benchmark. The --require-reviewed gate accepts ai_reviewed or accepted and reports the status counts.
- Preserve an immutable dataset version and hash the question file in each run record.
- Pool candidate passages from every compared retrieval configuration; review unjudged top results without revealing which system retrieved them where practical.
- Report nDCG/MRR/recall only for answerable queries with a stated relevance threshold, gain convention, and judgment coverage. Treat pilot results as development findings.
- Evaluate abstention separately on unanswerable queries; nearest-neighbor search always returning something is not itself a successful answer.
- Keep retrieval evaluation distinct from factual correctness, grounding, citation validity, and answer completeness.
