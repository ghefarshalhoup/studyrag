# What the passage review tells us

The retrieval comparison now has explicit relevance judgments for **all 384 question/passage pairs** in the three methods' top-10 union. You do not need to fill in annotation files. Codex performed the review; it has not been independently checked by a human.

## Results

Macro averages over the **16 answerable development questions**, using identical saved rankings:

| Method | nDCG@10 | MRR@10, supporting or direct | MRR@10, direct evidence only | Pooled recall@10 |
|---|---:|---:|---:|---:|
| BM25 | 0.719 | 0.897 | 0.803 | 0.714 |
| Dense | 0.816 | 0.896 | 0.896 | 0.871 |
| Hybrid, equal-weight RRF | 0.790 | 0.969 | 0.875 | 0.799 |

Dense has the highest nDCG and direct-evidence MRR in this small pilot. Hybrid finds some useful context early more consistently, but that context is not always a direct answer. This is not enough evidence to declare a universally better retriever. Pooled recall counts only known relevant chunks in this pool, not all relevant evidence in the corpus.

## Concrete examples

- **Dictionary keys, pilot-005:** all methods already put a direct answer first. The earlier exact-source-span diagnostic marked BM25 and hybrid as misses because it required a preceding introductory line. Passage review corrects the interpretation; it does not change the rankings.
- **File closing, pilot-006:** all three methods put direct evidence first. Dense has lower nDCG because it retrieves fewer of the other judged useful cleanup passages. The earlier source-span miss was not proof that dense lacked a usable answer.
- **Decimal equality, pilot-011:** BM25's first direct evidence is at rank 10, dense's at rank 1, and hybrid's at rank 2. This is an actual ranking improvement, distinct from source-span boundary effects.
- **Independent package environments, pilot-012:** BM25 and hybrid put useful package-installation context first, but have no grade-2 direct explanation in their top 10. Dense puts the separate-environments explanation first. Ordinary MRR counts the supporting context as relevant; direct MRR exposes this gap.
- **Shared lists, pilot-015:** the pool includes the default-list cause and the class-list cause/fix, but omits the None-sentinel default-list fix. Direct hits and a high nDCG do not prove that every part of this question can be answered.

## What this establishes

There is now a reproducible chain from frozen documents to stable chunks, saved rankings, explicit relevance decisions and ranking metrics. Each positive judgment includes an excerpt from the actual passage. The scorer refuses missing judgments, invalid excerpts, changed text and malformed ranking coverage.

The earlier [source-span diagnostics](../comparison-v1/REPORT.md) remain unchanged and answer a different question: how much of the original seed evidence was retrieved. The [full metric report](REPORT.md) explains formulas and lists every question/method result. The [review protocol](../../judgments-v1/README.md) explains the rubric and review limitations.

## What remains before strong portfolio performance claims

- Independently check a sample of the AI judgments, especially supporting-context versus direct-evidence decisions. The same AI drafted questions and reviewed the results.
- Define and freeze a held-out question set before further tuning; all current questions are development data. Keep related question families together to reduce leakage.
- Evaluate a reranker against the unchanged baselines, judging any new top-10 passages. Reusing this pool and silently grading unseen passages as irrelevant would bias the comparison.
- Evaluate answer completeness, citation support and abstention separately. All methods return candidates for the four unanswerable questions; retrieval alone does not decide whether to answer.

No paid API call, embedding recomputation or application change was required for this stage. Nothing was published to GitHub.

## Reproduce

From the repository root, run with any Python 3.11+ interpreter:

```powershell
python -m evaluation.run_metrics --output evaluation/pilot/runs/my-metrics
```

Choose a new directory. The four generated scoring artifacts (`summary.json`, `per_question.json`, `run.json`, `REPORT.md`) reproduce the recorded files exactly. `FINDINGS.md` is this separately written interpretation.
