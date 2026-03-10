from __future__ import annotations

import torch


def binary_gumbel_ste(logits: torch.Tensor, tau: float = 1.0) -> torch.Tensor:
    if tau <= 0:
        raise ValueError("tau must be positive")

    uniform = torch.rand_like(logits).clamp(1e-6, 1.0 - 1e-6)
    logistic_noise = torch.log(uniform) - torch.log(1.0 - uniform)
    soft = torch.sigmoid((logits + logistic_noise) / tau)
    hard = (soft > 0.5).to(soft.dtype)
    gate = hard - soft.detach() + soft

    if not torch.isfinite(gate).all():
        raise ValueError("Gate contains NaN or Inf")
    return gate
