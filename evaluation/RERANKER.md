# Local reranker experiment

The predeclared experiment adds one cross-encoder to the frozen development comparison. Read [the findings](pilot/runs/reranker-metrics-v1/FINDINGS.md) for the outcome, [the full report](pilot/runs/reranker-metrics-v1/REPORT.md) for every metric, and [the holdout protocol](pilot/heldout-v1/README.md) for the reserved final-check questions.

## Fixed configuration

- Model: `Xenova/ms-marco-MiniLM-L-6-v2`, revision `a09144355adeed5f58c8ed011d209bf8ee5a1fec`, full-precision ONNX file `onnx/model.onnx`, Apache-2.0. The [export model card](https://huggingface.co/Xenova/ms-marco-MiniLM-L-6-v2) identifies the [upstream cross-encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2).
- Candidate input: existing BM25 top 50 and dense top 50, fused with equal-weight RRF constant 60; take fused top 50. Query embeddings and document embeddings are replayed from the original run, without recomputation.
- Output: top 10 by descending cross-encoder logit, ties by stable chunk ID. Raw logits are not confidence probabilities. No threshold or answer generation is involved.
- Context: 512 tokens for the query/passage pair. Preserve the query and truncate only the passage tail when necessary. Truncation is counted per scored pair. Returned passages retain their full text.
- Runtime: existing pinned FastEmbed 0.9.1 / ONNX Runtime environment, CPU, two threads, batches of eight. One warm-up batch of eight pairs is excluded; one full scoring pass is timed per question. Timings exclude candidate retrieval and model loading.

`reranker_plan.json` fixes the choices. Its hash is in the prospective holdout freeze. No alternative reranker or configuration was tried after seeing the scores. The [FastEmbed reranker documentation](https://qdrant.tech/documentation/fastembed/fastembed-rerankers/) describes the local `TextCrossEncoder` interface.

## Reproduce on Windows

From the repository root, use an environment installed from `requirements-retrieval-lock.txt` as described in [SEMANTIC_COMPARISON.md](SEMANTIC_COMPARISON.md). No API key is required. Model files need about 92 MB and should remain under the ignored `.models/` directory.

```powershell
python -m evaluation.validate_holdout
python -m evaluation.run_reranker --fetch-model --model-dir .models/minilm-reranker
python -m evaluation.run_reranker --model-dir .models/minilm-reranker --output evaluation/pilot/runs/my-reranker
```

The fetch command explicitly downloads only the public files in `reranker_model.json`, checking sizes and SHA-256 hashes. Inference verifies the files and uses local-only loading. It sends no query or source text to a service.

For the recorded run, replay the candidate selection, logits and sorting without loading any model:

```powershell
python -m evaluation.run_reranker --verify
python -m evaluation.score_reranker --output evaluation/pilot/runs/my-reranker-metrics
```

Use a new output directory each time. The scoring command makes no model calls; it needs NumPy to verify the original saved vector rankings. Model reruns may vary slightly across numerical runtimes, so exact reproduction is established for saved-logit replay and scoring, not promised for logits on every platform.

## Review and artifacts

`pilot/runs/reranker-v1/` contains the 800 ranked results (200 per method), 1,000 candidate logits, the expanded 430-pair top-10 pool, and the model/config/input/output fingerprints and timing record. `pilot/reranker-judgments-v1/` retains the old 384 decisions and adds the 46 new passage reviews. No new passage is treated as irrelevant without review.

All four methods are rescored on the expanded pool. Its new positive evidence changes ideal nDCG rankings and recall denominators, so compare methods within this report rather than combining numbers from differently sized pools. Precision and ordinary/direct MRR keep their prior definitions. Recall remains pooled, not full-corpus recall. Overlapping chunks may repeat one fact; neither nDCG nor a direct hit proves complete multi-part answers.

No prospective held-out question was executed during this development stage. The later [final check](FINAL_CHECK.md) is now complete and reported separately. These development metrics have no independent human validation, answer generation, citation checks or statistical superiority claim. The app's retrieval path is unchanged; this stage is a reproducible experiment.
