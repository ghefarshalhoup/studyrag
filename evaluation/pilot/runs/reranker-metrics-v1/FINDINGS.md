# What changed after reranking

**The reranker improved early direct-answer ranking on this development set, with a substantial CPU latency cost.** It did not improve every question or retrieve all missing answer components.

We froze 16 separate evaluation questions before running the model. Those remain reserved and unexecuted. The measurements below use the original 16 answerable development questions; four unanswerable development cases are reported separately.

## Fair four-method comparison

All methods use the same expanded pool of 430 AI-reviewed question/passage pairs. The 46 newly introduced pairs were reviewed and the old 384 decisions were retained. One new passage directly supports the binary approximation explanation; the other 45 do not answer their questions.

| Method | nDCG@10 | Direct-evidence MRR@10 | Direct evidence first | Pooled recall@10 |
|---|---:|---:|---:|---:|
| BM25 | 0.718 | 0.803 | 12/16 | 0.714 |
| Dense | 0.812 | 0.896 | 13/16 | 0.865 |
| Hybrid | 0.788 | 0.875 | 13/16 | 0.796 |
| Reranked hybrid | **0.844** | **0.969** | **15/16** | 0.828 |

Dense still has higher pooled recall than reranked hybrid. Ordinary MRR, which also counts supporting context, reaches 1.000 for reranked hybrid, but this does not mean all questions have complete answers. Scores differ slightly from the earlier three-method report because the expanded pool changes ideal rankings and recall denominators. Existing retrieval rankings did not change.

## Improvements and regressions

- **Package isolation, pilot-012:** hybrid had no direct explanation in its top 10. Reranking puts the separate-virtual-environments explanation first; nDCG rises from 0.263 to 0.986.
- **Decimal equality, pilot-011:** direct evidence moves from hybrid rank 2 to reranker rank 1. nDCG rises from 0.462 to 0.693.
- **Iterator protocol, pilot-014:** nDCG rises from 0.622 to 0.987 by improving the ordering of useful protocol evidence.
- **Queues, pilot-001:** nDCG falls from 1.000 to 0.704, although the first result still directly answers the question. Other useful queue evidence is ranked less effectively.
- **File cleanup, pilot-006:** nDCG falls from 0.662 to 0.496. A direct answer remains first, but other useful cleanup passages are lost or demoted.
- **Shared lists, pilot-015:** the pool still omits the None-sentinel default-list fix. Reranking cannot establish complete answer coverage. It scores only the candidate shortlist, not every source passage.

Relative to hybrid, nDCG improves on 8 answerable questions, declines on 6 and is unchanged on 2. Report these tradeoffs alongside the mean.

## Runtime and limits

Scoring the 50 candidates took a median of **3.08 seconds per query** on this machine, excluding retrieval and model loading. This was a single timed pass per development question with one initial warm-up batch; it is descriptive, not a controlled speed benchmark against earlier runs.

Eight of the 1,000 scored query/passage pairs exceeded the 512-token context (maximum 535). Their passage tails were truncated for scoring and their queries preserved. Returned source passages remain complete. The model ran locally with no paid API call; its weights stay outside the repository.

The four unanswerable development questions still produce candidates from every method. No generated answers or abstention decisions were tested. These are AI-reviewed same-corpus development results, not independent human-gold or held-out results.

## Next step

Lock the final comparison implementation and run the reserved 16 questions once, pool and judge the returned passages, and report that final check separately. If its results guide further tuning, treat that set as development data thereafter. Independent review of a judgment sample would strengthen the portfolio evidence.

See [the full report](REPORT.md), [reranker setup and replay](../../../RERANKER.md), and [the prospective holdout](../../heldout-v1/README.md).
