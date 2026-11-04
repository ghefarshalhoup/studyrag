# Portfolio package

## Included

- A LangGraph/Streamlit document assistant with PDF/DOCX source/page metadata.
- Fixes and regression tests for rejected-evidence fallback and completion/memory ordering.
- BM25, local dense cosine, RRF hybrid and cross-encoder reranking experiments over 250 frozen chunks from 12 public CPython tutorial chapters.
- Twenty development questions and a separately frozen final set of sixteen, with explicit AI-reviewed pooled passage judgments.
- Saved vectors/logits, configuration and code fingerprints, replay commands, nDCG/MRR/precision/pooled recall, CPU timings and failure analysis.
- A short engineering case study, final-results figure, offline demonstration, reproducible dependency snapshots and offline CI workflow.

## Main finding

The reranker's development gain did not establish a clear practical benefit in the final same-corpus check: nDCG@10 0.814 versus BM25 0.812, with around 3.4 seconds of added CPU reranking. BM25 put direct evidence first on 9/12 answerable reserved questions versus 7/12 for reranked hybrid.

## Scope

These are small, same-corpus, AI-reviewed retrieval experiments. No independent human-gold labels, production deployment, generated-answer accuracy, verified citations or measured abstention reliability are claimed. The original course robustness experiment is preserved separately as historical work.

Python 3.13 on Windows CPU is the verified environment. Model-free replay does not require downloaded weights. The live app requires a user-supplied OpenAI API key.

## Publication

Repository: https://github.com/ghefarshalhoup/studyrag

Suggested commit title: `Package StudyRAG with reproducible retrieval evaluation and portfolio documentation`

Suggested release title: `StudyRAG: reproducible retrieval evaluation`

The prepared source archive excludes Git history, local environments, API keys, model weights and reproduction scratch output. It includes the public corpus's attribution/license and a file-level SHA-256 manifest. Local checks do not assert that GitHub-hosted CI has already run; the workflow executes when published.
