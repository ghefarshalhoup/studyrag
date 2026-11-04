# Final held-out passage review

This file documents **323 explicit question/passage relevance decisions** for the union of all four methods' top-10 results on the 16 previously reserved questions. The model configuration, implementation and inputs were locked before final inference. Grades were recorded before calculating ranking-quality metrics. The question text, reference evidence, model settings and rankings were not changed in response to these results.

## Same rubric as development

- **0:** does not support the requested answer. Generic Python examples, matching words or a related but different mechanism are insufficient.
- **1:** useful supporting context, insufficient by itself to establish a requested answer component.
- **2:** direct evidence for at least one requested component, through an explicit statement or a clear code demonstration. It need not establish a complete multi-part answer.

There are **286 grade-0, 9 grade-1 and 28 grade-2 pairs**. All top-10 results are judged. No unjudged result was silently treated as irrelevant. `qrels.jsonl` records the authoritative decisions, source identity, normalized text hash, rationale, reviewer and positive supporting excerpt. Every positive excerpt occurs verbatim in the returned source passage.

## Review process and limits

Codex reviewed candidates grouped by question and source location. Displays omitted retrieval method, rank and score. Review used a complete source-location inventory, topic-based triage and full text for plausible and borderline evidence. Clearly unrelated passages were assessed from their source context and excerpts; keywords did not automatically assign relevance grades. Borderline passages, including general data-hiding statements and argument-collection examples, were inspected in full.

The same AI authored the questions and had seen development results and corpus passages. This is not independent human review or a fully blinded evaluation. Human review of a sample would strengthen the evidence, particularly for supporting-context/direct-evidence boundaries. The labels remain `ai_reviewed`, not human-accepted.

The four missing-detail questions ask for HTTP-429 retry/backoff policy, multiprocessing start-method selection, exact garbage-collector thresholds and the result of `struct.calcsize('P')`. The returned corpus examples do not specify these details. Nearby networking, threading, weak-reference and binary-format passages are not answers to those questions. All their candidate grades are 0. This concerns evidence support in the provided tutorial corpus, not whether an external source could answer them.

Overlapping chunks can repeat a fact. Only the finite top-10 union is judged, so pooled recall is not exhaustive corpus recall. A grade-2 hit does not establish complete answers, supported citations or correct abstention. Retrieved source passages retain their full text; the reranker may have scored a truncated passage tail, as recorded in the run metadata.

The recorded [final report](../runs/heldout-metrics-v1/REPORT.md) compares all four methods using this one pool. If these results guide future tuning, the question set becomes development data for those choices; preserve this snapshot and create new final-check data.
