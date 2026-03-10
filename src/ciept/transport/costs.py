from __future__ import annotations

import torch


def compute_feature_cost(user_nodes: torch.Tensor, item_nodes: torch.Tensor) -> torch.Tensor:
    if user_nodes.ndim != 2 or item_nodes.ndim != 2:
        raise ValueError("user_nodes and item_nodes must be rank-2 tensors")
    if user_nodes.shape[1] != item_nodes.shape[1]:
        raise ValueError("user_nodes and item_nodes must share feature dimension")

    diff = user_nodes[:, None, :] - item_nodes[None, :, :]
    return (diff * diff).sum(dim=-1)


def apply_reliability_penalty(
    cost: torch.Tensor,
    target_capacity: torch.Tensor,
    strength: float,
) -> torch.Tensor:
    if target_capacity.ndim != 1:
        raise ValueError("target_capacity must be rank-1")
    if cost.shape[1] != target_capacity.shape[0]:
        raise ValueError("target_capacity length must match cost columns")

    penalty = strength * (1.0 - target_capacity.clamp(0.0, 1.0))
    return cost + penalty.unsqueeze(0)
