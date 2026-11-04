# Reproduce the keyword baseline

This is the first retrieval-only experiment for StudyRAG. It compares raw user questions with the pinned Python tutorial text using an in-memory BM25 index. There is no query rewriting, relevance-grading LLM, answer generation, semantic embedding, or network request in this path.

## Run

From the repository root, using Python 3.11 or later:

```sh
python -m evaluation.run_keyword
```

No third-party dependencies are needed for this command. The existing virtual environment can also run it:

```powershell
.\.venv\Scripts\python.exe -m evaluation.run_keyword
```

The default run directory is `evaluation/pilot/runs/bm25-v1`. Existing nonempty run directories are protected from overwrite. Reproduce into a new directory:

```sh
python -m evaluation.run_keyword --output evaluation/pilot/runs/bm25-reproduction
```

## Fixed baseline choices

- Inputs: only the 12 source paths listed in `evaluation/pilot/corpus_manifest.json`. Questions, answers, labels, licenses, and previous outputs are excluded from the index.
- Sources: validate byte hashes, decode UTF-8, normalize CRLF to LF.
- Chunking: raw-source windows of at most 1,200 characters, preferring newline boundaries. Adjacent windows overlap by at most 200 characters, with a preference for whole lines. Chunking is independent of labels. Later retrieval methods must use these same chunks for a fair first comparison.
- IDs: SHA-256 of document ID, source hash, preprocessing version, chunk configuration, and source start/end offsets. Document order does not affect IDs.
- Preprocessing: lightweight RST cleanup removes standalone directives/anchors and role wrappers, but preserves code and prose. It is not a full Sphinx renderer. Unresolved substitutions and some directive content remain; windows can start/end inside paragraphs or markup. Source coordinates always refer to the original normalized RST, not positions within the cleaned text. Preserve this limitation in comparisons.
- Tokenization: Unicode word tokens, case folding; code identifiers with underscores remain intact. No stemming, stopword removal, typo correction, or special decimal-number handling. For example, decimals split at the dot, and equlity is not normalized to equality.
- BM25: k1=1.2, b=0.75; positive IDF `log(1+(N-df+0.5)/(df+0.5))`; binary query-term frequency. Standard TF saturation includes the `(k1+1)` factor. This is an explicit standalone baseline, not bit-for-bit parity with a particular search engine. IDF/parameter reference: https://lucene.apache.org/core/9_12_1/core/org/apache/lucene/search/similarities/BM25Similarity.html
- Ranking: omit zero-score candidates; break ties by stable chunk ID; retain top 10.
- Timings: one warm-up per question followed by five runs. Median and nearest-rank p95 exclude preparation, index creation, diagnostics, UI, and generation. Local timings are not deployment latency claims.

## Outputs

| File | Contents |
|---|---|
| chunks.jsonl | Shared source-traceable corpus chunks |
| rankings.jsonl | Ranked chunk IDs, source lines and scores for each question |
| diagnostics.json | Per-question known-passage coverage and latency |
| summary.json | Aggregate development diagnostics |
| run.json | Configurations, source/label/implementation hashes, environment and timing scope |
| REPORT.md | Readable results and top-three excerpts for all questions |

The output chunks and excerpts are derived from Python tutorial content. Retain its attribution and license from `evaluation/pilot/ATTRIBUTION.md` and `evaluation/pilot/licenses/CPYTHON-LICENSE.txt`; these third-party passages are not relicensed under MIT.

## Interpreting results

Seed-evidence hit at k means the union of the top-k raw source windows fully covers at least one annotated positive passage for that question. A small overlap is not a hit. Character coverage measures the fraction of each annotated passage covered by that union, averaged over passages and then questions. Overlapping chunks do not double-count characters. Some passages are alternative evidence; others support different parts of a multi-part question. These diagnostics are not answer completeness.

These are incomplete AI-reviewed seed judgments, so do not present the numbers as gold-standard nDCG, MRR, recall, answer accuracy, or held-out performance. A useful retrieved passage may not match the full boundaries of its seed label. Pool retrieved candidates, judge alternatives and sufficient subpassages, and track label revisions before calculating conventional relevance metrics. No labels were changed based on this first run.

Unanswerable questions are excluded from known-evidence metrics. BM25 can still return lexical matches; it does not determine answerability, and its scores are not calibrated confidence values.

## Tests

```sh
python -m pytest tests/test_keyword.py
```

Checks include a hand-calculated BM25 score, stable tie ordering, source integrity, stable chunk IDs and coordinates, overlap union, non-matching queries, reproducible outputs, and protection against overwriting run directories.
