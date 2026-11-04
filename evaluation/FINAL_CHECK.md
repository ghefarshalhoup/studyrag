# Final retrieval check

The final comparison is complete. Read [the findings](pilot/runs/heldout-metrics-v1/FINDINGS.md) for the outcome or [the full report](pilot/runs/heldout-metrics-v1/REPORT.md) for formulas and per-question scores. The earlier development reports remain historical snapshots.

## What was fixed before execution

The [prospective question freeze](pilot/heldout-v1/freeze.json) predates reranker development execution. It contains 16 new question families: 12 answerable and four missing-detail cases. Questions, reference evidence, source documents and chunks were not edited for the final run.

`heldout_execution.json` was written after three offline runner tests passed and before any held-out inference. It records input hashes, implementation hashes and the existing `reranker_plan.json` configuration. Code changes invalidate replay against this lock. Its execution phase is final evaluation; the inherited development plan's `split_to_run_now` field records the earlier stage and was not rewritten to bypass the development-only runner.

The final runner reuses the original 250 chunk embeddings, encodes only the 16 new queries with the same pinned BGE model and prefix, and applies the same BM25, dense cosine, equal-weight RRF constant 60 and MiniLM reranker. Candidate depth is 50 per first-stage method, then 50 fused candidates for reranking, with top-10 outputs. No rewriting, answer generation, model training or result-driven parameter selection was added.

Both model snapshots are already pinned in the existing manifests. Inference uses local-only CPU loading, two threads and batches of eight for reranking. Queries remain intact; only passage tails may be truncated to the same 512-token pair context. Warmup uses the first development question, not one of the held-out questions. One timed pass was recorded per final question.

## Artifacts

- `pilot/runs/heldout-final-v1/`: 640 ranked results, 800 reranker scores, first-stage top-50 candidates, 16 saved query vectors, the 323-pair pool and a manifest recording model/runtime, timing, truncation and output hashes.
- `pilot/heldout-judgments-v1/`: explicit relevance decisions for every pool pair, with source line ranges, passage hashes, reasons and positive excerpts.
- `pilot/runs/heldout-metrics-v1/`: summary metrics, per-question results, reproducibility fingerprints, the full report and plain-language findings.

All 323 pairs are judged before quality scoring. Grades and metric definitions are the same as development. Metrics use the 12 answerable questions for macro averages; the four unanswerable cases have undefined nDCG/recall and are handled separately. This finite pool does not exhaust all relevant corpus passages.

## Reproduce without a model

From the repository root, using an environment with NumPy (the existing retrieval environment is sufficient):

```powershell
python -m evaluation.validate_holdout
python -m evaluation.run_holdout --verify
python -m evaluation.score_holdout --output evaluation/pilot/runs/my-final-metrics
```

Use a fresh metric output directory. Replay checks saved vectors, candidate selection, scores, ranked identities, source text, pool provenance, implementation and input hashes. Scoring rejects incomplete judgments, invalid source excerpts or changed passage hashes. The four generated metric artifacts reproduce byte-for-byte from the recorded inputs; tests verify that claim.

No API key, model download or inference is needed for replay/scoring. The app's dependencies are additionally needed for its application tests. Run the combined checks with:

```powershell
python -m pytest tests evaluation/pilot/test_dataset.py
```

## Optional inference reproduction

Fetch the already pinned public model snapshots using the existing [embedding guide](SEMANTIC_COMPARISON.md) and [reranker guide](RERANKER.md). Keep weights in the ignored `.models/` directory. Then:

```powershell
python -m evaluation.run_holdout --embedding-dir .models/bge-small-en-v1.5 --reranker-dir .models/minilm-reranker --output evaluation/pilot/runs/my-final-run
```

The recorded execution lock is already included; do not replace it with `--lock`. New inference runs have new timing/timestamp records and may differ slightly across numerical runtimes. Exact reproduction is established for the saved-artifact replay and metric scoring, not promised for model logits on every machine.

## Interpretation

The small final set shares the source corpus and AI authorship with development. The reviewer inspected source material and used topic-based triage plus full relevant/borderline passages, without method/rank/score displays. This is not independent human gold or an unseen-document/domain test. No statistical superiority, complete-answer accuracy, supported-citation quality or abstention reliability is established.

The development reranker advantage did not clearly carry over: final nDCG@10 is 0.814 for reranked hybrid and 0.812 for BM25, with BM25 putting direct evidence first more often. The roughly 3.4-second reranking cost is material on this machine. Report the result and its limits rather than tuning this set until the desired outcome appears. Once results inform future choices, use new final-check data for those choices.
