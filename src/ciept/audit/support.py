from __future__ import annotations

import torch

from ciept.audit.types import SupportOutputs


def support_to_logits(norm_support: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    if eps <= 0:
        raise ValueError("eps must be positive")
    clipped = norm_support.clamp(eps, 1.0 - eps)
    logits = torch.log(clipped) - torch.log(1.0 - clipped)
    if not torch.isfinite(logits).all():
        raise ValueError("Support logits contain NaN or Inf")
    return logits


def normalized_support(plan: torch.Tensor, q_cap: torch.Tensor, eps: float = 1e-6) -> SupportOutputs:
    if plan.ndim != 2:
        raise ValueError("plan must be rank-2")
    if q_cap.ndim != 1:
        raise ValueError("q_cap must be rank-1")
    if plan.shape[1] != q_cap.shape[0]:
        raise ValueError("plan columns must match q_cap length")
    if eps <= 0:
        raise ValueError("eps must be positive")

    raw_support = plan.sum(dim=0)
    norm_support = (raw_support / (q_cap + eps)).clamp(eps, 1.0 - eps)
    logits = support_to_logits(norm_support, eps=eps)
    if not torch.isfinite(norm_support).all():
        raise ValueError("Normalized support contains NaN or Inf")
    return SupportOutputs(
        raw_support=raw_support,
        normalized_support=norm_support,
        logits=logits,
    )
