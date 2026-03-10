from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class SupportOutputs:
    raw_support: torch.Tensor
    normalized_support: torch.Tensor
    logits: torch.Tensor


@dataclass(frozen=True)
class InterventionOutputs:
    gate: torch.Tensor
    score_selected: torch.Tensor
    score_removed: torch.Tensor
    loss_sufficiency: torch.Tensor
    loss_comprehensiveness: torch.Tensor
    loss_leakage: torch.Tensor
    loss_total: torch.Tensor
