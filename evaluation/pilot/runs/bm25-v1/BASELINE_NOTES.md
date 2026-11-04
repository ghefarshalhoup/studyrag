# First keyword baseline in plain language

The first real search run is complete. BM25 searched 250 chunks from the 12 Python tutorial chapters for all 20 pilot questions. It used no embeddings, LLM calls, query rewriting, or answer generation.

## What happened

- For 11 of the 16 answerable questions, the top five chunks collectively covered at least one complete annotated passage.
- For 13 of the 16 answerable questions, the top ten chunks did so.
- All four unanswerable questions still received keyword matches. Finding a match does not establish that a question is answerable.
- These are development diagnostics using incomplete AI-reviewed evidence labels. They are not answer accuracy, gold-standard retrieval quality, or results on unseen questions.

## A successful example

Question: Removing the oldest item from my Python list keeps getting slower as the list grows. What should I use for a FIFO queue, and why?

The first result was `py313-datastructures`, source lines 145-183. It includes the explanation that removing from the beginning of a list shifts other elements and the recommendation to use `collections.deque`. This was actual retrieval from the source corpus, not a scripted model answer.

## Three cases needing inspection

| Question | Observation | Interpretation |
|---|---|---|
| pilot-005: dictionary keys | Rank 1 contains the substantive answer about lists and tuple keys, but starts at line 497 while the seed label starts at line 495. Known-passage character coverage is about 79.6%. | The strict full-passage diagnostic marks a miss despite useful evidence. Refine judgments through candidate review before using conventional relevance metrics. Do not simply relabel to make BM25 look better. |
| pilot-011: floating-point equality | The top ten do not cover either labeled supporting passage. The first result concerns file handling. | A genuine failure relative to the known evidence. The baseline splits decimal numbers at punctuation and does not correct the typo in equlity. These are possible factors, not causally isolated explanations. |
| pilot-012: conflicting package versions | Rank 1 discusses installing or upgrading a specific package version. The labeled explanation about separate virtual environments is absent from the top ten. | Related vocabulary led to a passage that does not supply the required isolation explanation. This is a useful case for later semantic and hybrid comparison. |

## Where to look

- `REPORT.md`: per-question results and the top three excerpts for each question.
- `rankings.jsonl`: all top-ten results, including source locations.
- `chunks.jsonl`: the exact text searched and stable source coordinates.
- `run.json`: configurations, source/label/code hashes, and timing scope.

The original source passages in the outputs retain the PSF-2.0 licensing and Python Software Foundation attribution described in `run.json` and `../../ATTRIBUTION.md`.

## Next stage

Use these same frozen chunks for semantic and hybrid retrieval. Pool the retrieved candidates and review sufficient evidence and alternatives before calculating nDCG/MRR/recall. Keep these 20 questions in development. Freeze separate held-out questions before tuning. Confirm model access and costs before paid embedding or reranking runs.
