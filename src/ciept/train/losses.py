from __future__ import annotations

import torch


def confidence_weighted_listmle(
    pos_score: torch.Tensor,
    neg_scores: torch.Tensor,
    weight: torch.Tensor,
    tau: float = 0.2,
) -> torch.Tensor:
    if tau <= 0:
        raise ValueError("tau must be positive")

    pos = pos_score.reshape(-1, 1)
    if neg_scores.ndim == 1:
        neg = neg_scores.reshape(pos.shape[0], -1)
    else:
        neg = neg_scores
    logits = torch.cat([pos, neg], dim=1) / tau
    log_prob = logits[:, 0] - torch.logsumexp(logits, dim=1)
    return -(weight.reshape(-1) * log_prob).mean()


def combined_training_loss(
    ranking_loss: torch.Tensor,
    intervention_loss: torch.Tensor,
    lambda_intervention: float,
) -> torch.Tensor:
    return ranking_loss + lambda_intervention * intervention_loss
