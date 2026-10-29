# Robustness evaluation

How does StudyRAG behave when the knowledge base is not clean? The system was tested at seven
levels of increasing difficulty, from irrelevant documents only to sources that directly
contradict the truth.

## Questions

Three questions taken from the course material:

1. Why do people collect data?
2. How do people collect data?
3. What are the stages of data analysis?

## Test documents

All written for this test (in [`documents/`](documents/)):

| File | Content |
|---|---|
| `ground_truth.pdf` | The correct answers, as taught in the course |
| `irrelevant_noise.pdf` | Off-topic text (Gothic cathedral architecture) |
| `false_info.pdf`, `false_info_2.pdf` | Plausible but wrong answers on the same topics, in the same style as the ground truth |
| `false_info_contradictory.pdf`, `false_info_contradictory_2.pdf` | Texts that explicitly contradict the ground truth ("hypothesis testing is outdated", ...) |

## Levels

| Level | Knowledge base | What it tests |
|---|---|---|
| 0 | `irrelevant_noise` | Does it hallucinate when nothing relevant exists? |
| 1 | `ground_truth` | Baseline accuracy |
| 2 | `ground_truth` + `irrelevant_noise` | Can it ignore distractions? |
| 3 | + `false_info` (truth : false = 1 : 1) | Can it pick the correct source? |
| 4 | + `false_info_2` (1 : 2) | What if false information outweighs the truth? |
| 5 | `ground_truth` + `false_info_contradictory` (1 : 1) | How does it handle direct contradiction? |
| 6 | + `false_info_contradictory_2` (1 : 2) | Contradiction in the majority |

Each answer was graded as **Correct** (matches the ground truth), **Partial** (some right,
some wrong or missing), **Misled** (follows the false information), **Hallucinated** (wrong
and from no source), or **Abstained** (says it doesn't know).

## Results

| Level | Correct | Partial | Misled | Hallucinated | Abstained | Accuracy |
|---|---|---|---|---|---|---|
| 0 | – | – | – | – | 3/3 | 100 % (correct abstention) |
| 1 | 3/3 | – | – | – | – | 100 % |
| 2 | 3/3 | – | – | – | – | 100 % |
| 3 | 1/3 | 2/3 | – | – | – | 33 % |
| 4 | 1/3 | 2/3 | – | – | – | 33 % |
| 5 | 1/3 | 2/3 | – | – | – | 33 % |
| 6 | – | 3/3 | – | – | – | 0 % |

## Findings

- **No hallucination**: with only irrelevant text, the system abstained on every question.
- **Robust to noise**: off-topic documents did not affect accuracy (levels 1 and 2).
- **Not robust to false information**: once wrong documents are present, most answers mix
  correct and incorrect points (partial). The relevance grader checks whether a chunk is
  on topic, not whether it is true, so false chunks reach the answer.
- **Contradictions are passed to the user**: with contradicting sources, the system reports
  that the sources disagree rather than deciding which one to trust.

Three failure modes follow: aggregation without filtering, no authority ranking between
sources, and conflict deferral. A next version would need source credibility: trust scores
per document, contradiction detection among retrieved chunks, and answers that name the
source they rely on.
