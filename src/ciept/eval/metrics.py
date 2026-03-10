from __future__ import annotations

import torch


def recall_at_1(pos_score: torch.Tensor, neg_scores: torch.Tensor) -> float:
    best_neg = neg_scores.max().item()
    return 1.0 if pos_score.item() > best_neg else 0.0


def mean_reciprocal_rank(pos_score: torch.Tensor, neg_scores: torch.Tensor) -> float:
    scores = torch.cat([pos_score.reshape(1), neg_scores.reshape(-1)])
    sorted_scores, indices = torch.sort(scores, descending=True)
    rank = (indices == 0).nonzero(as_tuple=False)[0, 0].item() + 1
    return 1.0 / rank
