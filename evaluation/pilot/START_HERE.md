# What is ready

The 20 questions have been checked and corrected against their source documents by Codex. You do not need to fill in the annotation files. This is AI review, not independent human review.

Two agent bugs are fixed: rejected evidence stays rejected, and completed answers are returned and saved correctly. The offline example demonstrates both an answer with a source and an abstention without sources.

## Try the example

From the StudyRAG repository, using its existing virtual environment:

```powershell
.\.venv\Scripts\python.exe examples\offline_agent_demo.py
```

No API key or paid model call is needed. Responses and embeddings are fake so this checks application behavior, not real search quality.

## Try the keyword search experiment

The keyword baseline is implemented. It searches the actual tutorial text using BM25 and records the ranked passages for all 20 questions. It does not use the scripted demo model. From the repository root:

```powershell
.\.venv\Scripts\python.exe -m evaluation.run_keyword --output evaluation/pilot/runs/my-run
```

Use a new output directory for each run. Open `runs/bm25-v1/REPORT.md` for the recorded first run and `runs/bm25-v1/BASELINE_NOTES.md` for a short explanation of the findings. No API key is needed.

## What comes next

The semantic/hybrid comparison is now complete using a free local model. Open `runs/comparison-v1/COMPARISON_NOTES.md` for the short explanation, or `runs/comparison-v1/REPORT.md` for detailed results. All three methods used the same chunks and labels.

The pooled passage review and standard ranking metrics are also complete. Read [the plain-language findings](runs/metrics-v1/FINDINGS.md) first. All 384 question/passage pairs have explicit AI-reviewed grades. The scoring report includes nDCG@10, MRR@10, direct-evidence MRR, precision and pooled recall, with full top-10 judgment coverage.

You can reproduce the scoring with any Python 3.11+ interpreter, without API keys or embedding dependencies:

```powershell
python -m evaluation.run_metrics --output evaluation/pilot/runs/my-metrics
```

Use a new output directory. These are AI-reviewed development results, not human gold labels, exhaustive corpus recall, answer accuracy or performance on unseen questions.

## Reranking is now tested

Read [the reranker findings](runs/reranker-metrics-v1/FINDINGS.md). A local cross-encoder reranks the fused top 50 candidates. All 46 new top-10 passage pairs have been reviewed, giving a shared pool of 430 pairs for the four-method comparison. The earlier reports are retained as separate snapshots.

You can verify the recorded reranker rankings and recalculate scores without loading a model, using an environment with the retrieval dependencies installed:

```powershell
python -m evaluation.run_reranker --verify
python -m evaluation.score_reranker --output evaluation/pilot/runs/my-reranker-metrics
```

## Final check is complete

The comparison has now run on the [16 separately frozen questions](heldout-v1/README.md). Read [the final findings](runs/heldout-metrics-v1/FINDINGS.md): the reranker's development gain did not establish a clear advantage over BM25 on the reserved questions. Every one of the 323 pooled question/passage pairs has an explicit AI-reviewed relevance grade.

No annotation-file editing or API key is required from you. You can verify the final rankings and reproduce the report without running a model:

```powershell
python -m evaluation.run_holdout --verify
python -m evaluation.score_holdout --output evaluation/pilot/runs/my-final-metrics
```

Use a new metric output directory. See [the final-check protocol](../FINAL_CHECK.md) for the lock, artifacts and limitations. The retrieval evaluation stage is complete; further tuning based on these results needs new final-check questions.

For optional inspection, REVIEW.md shows the questions and evidence together. AI_REVIEW.md explains the corrections. No action is required from you to run the offline tests or demonstration.
