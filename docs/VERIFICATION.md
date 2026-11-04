# Package verification

The portfolio package was checked locally on **2026-11-04**, using Python 3.13.5 on Windows CPU.

- Installed the captured application/evaluation dependencies into a fresh environment. Optional plotting dependencies were installed to regenerate the results figure.
- Ran the application, evaluation and packaging suite: **124 passed**.
- Ran the actual LangGraph behavior demo with scripted responses and fake embeddings; the recorded output is in `assets/offline-demo.txt`.
- Built and extracted the public-source ZIP, verifying every source file against its SHA-256 manifest.
- Created a temporary Git index from the extracted source with `core.autocrlf=true`, checked the files out again, and verified that every file hash stayed unchanged. `.gitattributes` protects the byte-sensitive evaluation evidence.
- Ran all 124 tests from that fresh checkout.
- Replayed **640 final ranked results and 800 reranker scores** from saved vectors/logits, with zero model calls.
- Recomputed and byte-compared all four final scoring artifacts: `summary.json`, `per_question.json`, `run.json` and `REPORT.md`.
- Checked the new README/documentation links and parsed the CI workflow.

No paid model/API calls were made during package verification. Live OpenAI answer generation was not tested. The frozen evaluation inputs and implementation files were not modified by the portfolio packaging.

The [GitHub Actions workflow](../.github/workflows/ci.yml) is prepared for pushes and pull requests, with the official [checkout](https://github.com/actions/checkout) and [setup-python](https://github.com/actions/setup-python) actions pinned to commits. A GitHub-hosted CI run is pending publication; the local checks above are not a claim that hosted CI has already run.

The ZIP contains a `PACKAGE_MANIFEST.json` with paths, sizes and hashes. Its credential check recognizes several common embedded-key patterns and withholds matched values; it complements file-selection rules and is not a general proof that arbitrary text can contain no secrets.
