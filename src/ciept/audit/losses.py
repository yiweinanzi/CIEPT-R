from __future__ import annotations

import torch
import torch.nn.functional as F

from ciept.audit.gating import binary_gumbel_ste
from ciept.audit.support import normalized_support
from ciept.audit.types import InterventionOutputs


def leakage_ratio(norm_support: torch.Tensor, nuisance_mask: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    if norm_support.shape != nuisance_mask.shape:
        raise ValueError("norm_support and nuisance_mask must share shape")
    if eps <= 0:
        raise ValueError("eps must be positive")

    return (norm_support * nuisance_mask).sum() / (norm_support.sum() + eps)


def lightweight_scorer(
    user_nodes: torch.Tensor,
    item_nodes: torch.Tensor,
    gate: torch.Tensor,
    eps: float = 1e-6,
) -> torch.Tensor:
    if user_nodes.ndim != 2 or item_nodes.ndim != 2:
        raise ValueError("user_nodes and item_nodes must be rank-2")
    if item_nodes.shape[0] != gate.shape[0]:
        raise ValueError("gate length must match item_nodes rows")

    user_repr = user_nodes.mean(dim=0)
    masked_item = item_nodes * gate.unsqueeze(-1)
    item_repr = masked_item.sum(dim=0) / (gate.sum() + eps)
    return F.cosine_similarity(user_repr.unsqueeze(0), item_repr.unsqueeze(0)).reshape(())


def single_pass_intervention(
    score_full: torch.Tensor,
    plan: torch.Tensor,
    q_cap: torch.Tensor,
    item_nodes: torch.Tensor,
    user_nodes: torch.Tensor,
    nuisance_mask: torch.Tensor,
    tau: float,
    margin: float = 0.1,
    alpha: float = 0.5,
    beta: float = 0.5,
    eps: float = 1e-6,
) -> InterventionOutputs:
    if tau <= 0:
        raise ValueError("tau must be positive")
    if item_nodes.shape[0] != q_cap.shape[0] or nuisance_mask.shape[0] != q_cap.shape[0]:
        raise ValueError("item_nodes, q_cap, and nuisance_mask must align")

    support = normalized_support(plan, q_cap, eps=eps)
    gate = binary_gumbel_ste(support.logits, tau=tau)
    score_selected = lightweight_scorer(user_nodes, item_nodes, gate, eps=eps)
    score_removed = lightweight_scorer(user_nodes, item_nodes, 1.0 - gate, eps=eps)

    detached_full = score_full.detach()
    loss_sufficiency = (detached_full - score_selected).abs()
    loss_comprehensiveness = torch.relu(
        torch.tensor(margin, device=score_full.device, dtype=score_full.dtype)
        - (detached_full - score_removed)
    )
    loss_leakage = leakage_ratio(support.normalized_support, nuisance_mask, eps=eps)
    loss_total = loss_sufficiency + alpha * loss_comprehensiveness + beta * loss_leakage

    return InterventionOutputs(
        gate=gate,
        score_selected=score_selected,
        score_removed=score_removed,
        loss_sufficiency=loss_sufficiency,
        loss_comprehensiveness=loss_comprehensiveness,
        loss_leakage=loss_leakage,
        loss_total=loss_total,
    )
