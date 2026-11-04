"""Ranking metrics over explicit graded judgments; no model or service calls."""
import math


def score_ranking(ranked_ids, grades, k=10):
    """Score against a judged pool, not an exhaustively judged corpus.

    Grades: 0 irrelevant, 1 supporting context, 2 direct answer evidence.
    A grade-2 passage may answer one part of a multi-part question.
    Unjudged results are errors, never implicit zeroes. Missing result slots
    contribute zero gain and precision always uses k as its denominator.
    """
    if type(k) is not int or k < 1:
        raise ValueError('k must be a positive integer')
    ranked_ids = list(ranked_ids)
    if len(set(ranked_ids)) != len(ranked_ids):
        raise ValueError('Duplicate chunk in ranking')
    if any(type(grade) is not int or grade not in (0, 1, 2) for grade in grades.values()):
        raise ValueError('Grades must be integers in {0, 1, 2}')
    top = ranked_ids[:k]
    missing = set(top) - grades.keys()
    if missing:
        raise ValueError(f'Unjudged chunks in top {k}: {sorted(missing)}')
    ranked_grades = [grades[chunk_id] for chunk_id in top]

    def dcg(values):
        return sum((2**grade - 1) / math.log2(rank + 1)
                   for rank, grade in enumerate(values, 1))

    def reciprocal_rank(threshold):
        return next((1 / rank for rank, grade in enumerate(ranked_grades, 1)
                     if grade >= threshold), 0.0)

    ideal = dcg(sorted(grades.values(), reverse=True)[:k])
    relevant = sum(grade >= 1 for grade in grades.values())
    found = sum(grade >= 1 for grade in ranked_grades)
    return {
        'returned_at_k': len(top),
        'relevant_in_pool': relevant,
        'direct_in_pool': sum(grade == 2 for grade in grades.values()),
        'ndcg_at_k': dcg(ranked_grades) / ideal if ideal else None,
        'mrr_at_k': reciprocal_rank(1),
        'direct_mrr_at_k': reciprocal_rank(2),
        'precision_at_k': found / k,
        'pooled_recall_at_k': found / relevant if relevant else None,
    }
