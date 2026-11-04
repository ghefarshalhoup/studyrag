# AI source review

Codex reviewed the 20 development questions against their cited source passages and nearby context. This was a second pass by the same AI assistant, not independent human review. Labels are marked ai_reviewed, not accepted.

The original source files are unchanged. Mechanical validation checks their hashes and exact evidence locations. The --require-reviewed gate accepts ai_reviewed or accepted; passing it does not imply human approval.

## Corrections and decisions

| Question | Decision |
|---|---|
| pilot-001 | Checked FIFO semantics, shifting cost, deque recommendation, and the explicit irrelevant set passage. |
| pilot-002 | Clarified that a fresh list is created for calls which omit the argument; the example does not copy explicitly supplied lists. |
| pilot-003 | Replaced the invalid srot() code with a typo in ordinary prose. The old literal call would raise AttributeError, so its None premise was misleading. |
| pilot-004 | Checked the empty-set versus empty-dictionary distinction. |
| pilot-005 | Checked list-key and tuple-of-strings claims against the source. This is not a general claim that all immutable Python objects are hashable. |
| pilot-006 | Both file-handling passages independently support closing the file on an exception; either can supply evidence. |
| pilot-007 | Checked bytes versus text and the explicit restriction on encoding in binary mode. |
| pilot-008 | Checked dump/load file operations versus dumps returning a string. |
| pilot-009 | Completed the source paragraph and checked local module shadowing; question concerns a Python library module, not a built-in module. |
| pilot-010 | Checked main-guard code and the explanation of imported versus directly executed modules. |
| pilot-011 | Added the direct explanation of binary approximation so the causal part is explicitly supported. |
| pilot-012 | Checked conflicting package requirements and per-application environment isolation. Removed a leading blank line from the evidence. |
| pilot-013 | Checked normal exhaustion, break, return, and exception cases. |
| pilot-014 | Extended the excerpt to include the complete opening sentence; checked next and StopIteration. |
| pilot-015 | Checked both causes and both fixes; clarified omitted function argument and instance-specific attributes. |
| pilot-016 | Added explicit binary-representation evidence alongside the equality example and Decimal use cases. |
| pilot-017 | Checked absence of pandas/groupby/DataFrame and reviewed list, dictionary, statistics, and file-handling sections; none specifies the pandas API requested. |
| pilot-018 | Checked absence of scikit-learn/GridSearchCV and reviewed function arguments and standard-library chapters; none provides the requested tuning API. |
| pilot-019 | Checked absence of PostgreSQL/JSONB and reviewed JSON serialization; file serialization does not answer database-index configuration. |
| pilot-020 | Checked absence of Qdrant/model identifier and reviewed numeric types and package management; none specifies vector collection settings. |

## Limitations

The four unanswerable items are relatively easy out-of-corpus questions. Later expansion should include harder missing-detail questions within Python. Evidence labels are seed judgments, not exhaustive qrels: pool retrieval results before reporting benchmark metrics. All questions remain development data; no held-out generalization claim is supported. Semantic review can miss errors even when source offsets and hashes are correct.

## Label snapshots

- Before this review: `1d05caf81bd0059e1d574f8a5df2ec588801bca2707c506eefb57d6907da00c8`
- After this review: `9eb888cc94bbae62a6a73da8793917ecc799eda14ba8f2ed4cbf725737a8c0ac`
