from __future__ import annotations

import math


def _rank_of_positive(pos_score: float, neg_scores: list[float]) -> int:
    scores = [float(pos_score)] + [float(score) for score in neg_scores]
    sorted_indices = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)
    return sorted_indices.index(0) + 1


def recall_at_k(pos_score: float, neg_scores: list[float], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    rank = _rank_of_positive(pos_score, neg_scores)
    return 1.0 if rank <= k else 0.0


def mrr_at_k(pos_score: float, neg_scores: list[float], k: int | None = None) -> float:
    rank = _rank_of_positive(pos_score, neg_scores)
    if k is not None and k <= 0:
        raise ValueError("k must be positive")
    if k is not None and rank > k:
        return 0.0
    return 1.0 / rank


def ndcg_at_k(relevances: list[int], scores: list[float], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    if len(relevances) != len(scores):
        raise ValueError("relevances and scores must have the same length")

    ranked = sorted(zip(scores, relevances), key=lambda pair: pair[0], reverse=True)[:k]
    dcg = 0.0
    for idx, (_, rel) in enumerate(ranked, start=1):
        dcg += (2**rel - 1) / math.log2(idx + 1)

    ideal = sorted(relevances, reverse=True)[:k]
    idcg = 0.0
    for idx, rel in enumerate(ideal, start=1):
        idcg += (2**rel - 1) / math.log2(idx + 1)
    if idcg == 0.0:
        return 0.0
    return dcg / idcg
