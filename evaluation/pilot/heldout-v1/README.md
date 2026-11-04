# Prospective held-out questions, version 1

**16 questions: 12 answerable and 4 unanswerable in the corpus.** The file was frozen before the MiniLM reranker was executed. None of these questions was run through retrieval or used for tuning during the development stage. The later final check is now complete; read [the findings](../runs/heldout-metrics-v1/FINDINGS.md). `freeze.json` retains the original question, development-data, corpus, chunk and experiment-plan hashes, with a UTC timestamp.

The answerable questions cover enumeration, list comprehensions, variadic arguments, parameter kinds, docstrings, exception-handler ordering, exception chaining, logging defaults, regular expressions, weak references, byte compression and name mangling. These are new question families rather than paraphrases of the existing development questions. Some Python chapters and source chunks are shared; this is not a document-held-out dataset.

The four missing-detail questions concern HTTP-429 retry policy, multiprocessing start methods, garbage-collector thresholds and native struct sizing. They use vocabulary close to the corpus, making them less obviously out of scope than the development set's third-party-tool questions. They are labeled unanswerable only with respect to the provided tutorial text.

`questions.jsonl` contains the questions, reference answers, source-line and character evidence for positives, and source-search rationales for negatives. Codex authored the questions and checked source support; labels are **AI-reviewed**, not independent human gold. Absence of distinctive search terms supports the manual source review but is not a general proof that an answer cannot be inferred.

## Check integrity

```powershell
python -m evaluation.validate_holdout
```

This command checks the freeze, exact evidence text and coordinates, source hashes, separate family IDs and negative-search terms. It makes no retrieval or model calls. Tests cover edited questions, invented quotes, reused family IDs and modified sources/configuration. Family-ID checks complement manual topic review; they cannot automatically detect all semantic overlap.

## Final execution protocol

The final run locked the complete retrieval configuration and implementation before running these questions and recorded the hash of this freeze. It pooled the top results from every compared method, judged all 323 pairs without treating unjudged passages as zero, and reported all methods using the same pool. Unanswerable cases are separate; generation/abstention needs its own checks. See [the execution and replay protocol](../../FINAL_CHECK.md).

Once results have been inspected, further choices based on them make this set development data. A new version is needed for another final check after such tuning. Do not silently edit this frozen version.

This is a prospective same-corpus holdout created after earlier development findings. It does not establish unseen-domain generalization, independence from AI authorship, or absence of pretraining contamination. The freeze's `evaluated: false` describes its state at freezing; any later execution must be recorded in a separate run manifest rather than editing the freeze.
