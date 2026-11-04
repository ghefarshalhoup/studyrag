# Reproduce semantic and hybrid retrieval

This experiment compares BM25, a free local embedding model, and reciprocal rank fusion on the same frozen 250 chunks and the same 20 AI-reviewed development questions. There is no answer generation or reranker in this run. Neither the source corpus nor the labels were changed after seeing results.

## Local model

The model is BAAI/bge-small-en-v1.5 using Qdrant's quantized ONNX export, revision `aa8f8b060edb00e03bfdd08813a2949946c8ba55`. Model/export license: MIT. Model card: https://huggingface.co/BAAI/bge-small-en-v1.5 . Export: https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q . Exact file hashes and download URLs are in `evaluation/embedding_model.json`.

Inference uses FastEmbed 0.9.1 with ONNX Runtime on CPU, two threads, CLS pooling and L2-normalized embeddings. Queries use the model author's recommended retrieval instruction, recorded in run.json. Passages have no prefix. Maximum input length is 512 tokens, including special tokens. The runner checks the complete untruncated inputs first and fails rather than silently truncate source evidence. The recorded corpus had a maximum passage length of 508 tokens and zero truncated inputs.

No document or question is sent to a remote embedding API. The explicit fetch command downloads public weights and tokenizer files; the comparison runner loads only verified local files. Model binaries are not included in Git.

## Setup

Use a separate environment so optional model dependencies do not change the app environment. These commands are for Windows; the recorded lockfile was exercised with Python 3.13.5 on Windows CPU. Other platforms are not verified.

```powershell
python -m venv .retrieval-venv
.\.retrieval-venv\Scripts\python.exe -m pip install -r requirements-retrieval-lock.txt
.\.retrieval-venv\Scripts\python.exe -m evaluation.fetch_embedding_model --output .models/bge-small-en-v1.5
```

The download is about 67 MB plus tokenizer/configuration files. All downloads are checked against pinned SHA-256 hashes. The optional direct dependencies are also listed in requirements-retrieval.txt. The full captured package versions are recorded in run.json and requirements-retrieval-lock.txt.

## Run

```powershell
$env:HF_HUB_OFFLINE='1'
$env:HF_HUB_DISABLE_TELEMETRY='1'
.\.retrieval-venv\Scripts\python.exe -m evaluation.run_comparison --model-dir .models/bge-small-en-v1.5 --output evaluation/pilot/runs/comparison-reproduction
```

Choose a new output directory. Existing run directories are protected against overwrite. The runner validates source hashes, the original question-file hash, and every frozen chunk against current preprocessing. It also requires BM25 top-ten rankings to reproduce the original run before performing the comparison.

## Fixed comparison settings

- Dense retrieval: exact cosine search over the 250 embeddings, with stable chunk-ID tie breaking. All returned scores are ranking values, not confidence probabilities.
- Hybrid retrieval: top 50 candidates from each of BM25 and dense, equal weights, RRF constant 60, score equal to the sum of `1 / (60 + rank)` across rankings. Original BM25/cosine scores are not mixed.
- Output: top 10 for each method; top 50 lexical/dense candidates saved separately for later analysis. Parameters were fixed before this first run, not tuned to maximize its scores.
- Diagnostics: the same complete-known-passage coverage and character-coverage definitions as the keyword baseline. They are not conventional nDCG, MRR, gold recall, answer accuracy, or held-out performance.
- Timing: real query encoding is included in dense timings. Hybrid timing sums sequential lexical search, query encoding, cosine search, and fusion. Model loading and passage encoding are separate, not hidden in query timing. Five measured runs per question follow one warm-up.

## Output and replay

The recorded run is `evaluation/pilot/runs/comparison-v1/`:

| File | Purpose |
|---|---|
| REPORT.md | Readable side-by-side findings and top-one source excerpts |
| summary.json | Method-level diagnostics and timings |
| diagnostics.json | Per-question coverage and timing samples |
| rankings.jsonl | Top ten per method and question |
| candidate_rankings.jsonl | Top fifty BM25/dense candidates used by fusion |
| pool.jsonl | Deduplicated top-ten candidate pool, explicitly unjudged |
| embeddings.npz | Saved document/query vectors for model-free ranking replay |
| run.json | Model revision/file hashes, label/source/code hashes, row ordering, package versions, and measurement scope |

Replay using NumPy, without FastEmbed, model weights or network access:

```powershell
.\.venv\Scripts\python.exe -m evaluation.verify_comparison
```

The replay validates the run inputs and implementation hashes, then recomputes BM25, dense cosine and RRF rankings from the saved vectors. It checks ranked IDs and scores, not just that files exist. Numerical scores allow a small floating-point tolerance. This replay verifies ranking calculations; it does not independently reproduce model inference. Re-running the comparison is the inference reproduction step.

## Interpretation and next work

Read COMPARISON_NOTES.md in the run directory for a plain-language explanation. On this development pilot, dense search has the highest complete-known-passage hit count; hybrid does not automatically improve on it. The seed labels are incomplete, and strict passage boundaries can count useful partial passages as misses. The saved pool should be judged before reporting standard relevance metrics. Human review is recommended before calling the labels a gold standard. Preserve a separate held-out set for generalization claims.

The source excerpts in reports and pool.jsonl retain the Python Software Foundation copyright and PSF-2.0 terms; see evaluation/pilot/ATTRIBUTION.md. The corpus is not relicensed under the model's MIT license.
