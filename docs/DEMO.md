# Run the evidence, not just the UI

All commands below run from the repository root in the environment described in the README.

## 1. Inspect the final result

Open [the final findings](../evaluation/pilot/runs/heldout-metrics-v1/FINDINGS.md). They explain the quality/latency tradeoff, specific failures and the limits of the AI-reviewed labels.

## 2. Exercise the actual agent graph offline

```powershell
.\.venv\Scripts\python.exe examples/offline_agent_demo.py
```

This runs the real LangGraph pipeline using a scripted model and deterministic fake embeddings. It demonstrates an answer with a source, abstention after evidence rejection and persisted conversation turns. It makes no paid API call and does not measure model/search quality. [Recorded output](assets/offline-demo.txt).

## 3. Verify actual retrieval rankings

```powershell
.\.venv\Scripts\python.exe -m evaluation.run_holdout --verify
.\.venv\Scripts\python.exe -m evaluation.score_holdout --output local-results/final-metrics
```

Replay uses saved real query embeddings and cross-encoder logits, not the scripted demo responses. It checks all 640 ranked results against the fixed inputs. Scoring validates all 323 explicit relevance judgments and regenerates the summary, per-question metrics, report and fingerprints. No model weights or API key are required. Use a fresh output directory.

## 4. Run the tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests evaluation/pilot/test_dataset.py
```

Tests cover normal graph flow, rejected/empty evidence, current-answer return, state persistence, source integrity, stable rankings, analytical metric examples and malformed review artifacts.

## Optional interactive app

Copy `.env.example` to `.env`, set your own `OPENAI_API_KEY`, then run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Upload a PDF/DOCX and ask about its contents. Interactive mode uses the configured OpenAI models and sends relevant document text to that API. The recorded evaluation uses public tutorial text and local models. Live OpenAI generation was not exercised in the offline checks.
