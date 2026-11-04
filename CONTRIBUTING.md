# Working on StudyRAG

Use Python 3.13 and install `requirements-dev-lock.txt` in a fresh virtual environment. Run:

```powershell
python -m pytest tests evaluation/pilot/test_dataset.py
python examples/offline_agent_demo.py
python -m evaluation.run_holdout --verify
```

These checks use local fixtures and saved vectors/logits. No API key or downloaded model weights are needed. The interactive app and optional inference reproduction have separate setup instructions in the README and evaluation guides.

## Preserve recorded evidence

Evaluation snapshots include exact file/code hashes. `.gitattributes` disables newline rewriting so Windows checkouts preserve those identities. Do not normalize or edit frozen corpus, questions, implementations or run artifacts to make checks pass. Intentional experiment changes need a new version, recorded configuration, appropriate passage review and new final-check data when earlier results informed tuning.

The final comparison is retrieval-only, with AI-reviewed pooled labels. Keep those limits visible in new reports and distinguish full-corpus recall from pooled recall. Do not infer generated-answer accuracy from a retrieved passage hit.

## Figures and source archive

```powershell
python -m pip install -r requirements-figures.txt
python scripts/render_results.py
python scripts/package_source.py --output dist/studyrag-source.zip
```

The figure reads recorded metrics/timings directly. The source package includes a file-hash manifest and excludes local environments, environment secrets, model binaries and scratch results. Add behavior tests for implementation changes; documentation-only edits do not need tests that mirror their text.

Project code is MIT-licensed. Preserve the separate CPython tutorial attribution/license and model-license notices when redistributing their material.
