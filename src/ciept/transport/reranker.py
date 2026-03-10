from __future__ import annotations

import torch
from torch import nn

from ciept.transport.costs import apply_reliability_penalty, compute_feature_cost
from ciept.transport.operators import torch_partial_transport
from ciept.transport.types import RerankerInputs, RerankerOutputs


class CapacityCalibratedPartialTransportReranker(nn.Module):
    def __init__(
        self,
        epsilon: float = 0.05,
        max_iters: int = 200,
        tolerance: float = 1e-9,
        penalty_strength: float = 0.5,
    ) -> None:
        super().__init__()
        self.epsilon = epsilon
        self.max_iters = max_iters
        self.tolerance = tolerance
        self.penalty_strength = penalty_strength

    def forward(self, inputs: RerankerInputs) -> RerankerOutputs:
        if inputs.user_nodes.ndim != 2 or inputs.item_nodes.ndim != 2:
            raise ValueError("user_nodes and item_nodes must be rank-2 tensors")
        if inputs.user_nodes.shape[1] != inputs.item_nodes.shape[1]:
            raise ValueError("user_nodes and item_nodes must share feature dimension")
        if inputs.source_mass.ndim != 1 or inputs.target_capacity.ndim != 1:
            raise ValueError("source_mass and target_capacity must be rank-1 tensors")
        if inputs.source_mass.shape[0] != inputs.user_nodes.shape[0]:
            raise ValueError("source_mass must match user_nodes rows")
        if inputs.target_capacity.shape[0] != inputs.item_nodes.shape[0]:
            raise ValueError("target_capacity must match item_nodes rows")
        if torch.any(inputs.source_mass < 0):
            raise ValueError("Source masses must be non-negative")
        if torch.any(inputs.target_capacity < 0):
            raise ValueError("Target capacities must be non-negative")

        budget = inputs.mass_budget.item() if isinstance(inputs.mass_budget, torch.Tensor) else float(inputs.mass_budget)
        if budget <= 0:
            raise ValueError("Mass budget must be positive")

        feature_cost = compute_feature_cost(inputs.user_nodes, inputs.item_nodes)
        penalized_cost = apply_reliability_penalty(
            feature_cost,
            inputs.target_capacity,
            strength=self.penalty_strength,
        )
        plan = torch_partial_transport(
            penalized_cost,
            inputs.source_mass,
            inputs.target_capacity,
            inputs.mass_budget,
            epsilon=self.epsilon,
            max_iters=self.max_iters,
            tolerance=self.tolerance,
        )

        if not torch.isfinite(plan).all():
            raise ValueError("Transport plan contains NaN or Inf")

        transported_mass = plan.sum()
        target_usage = plan.sum(dim=0)
        score = -(plan * penalized_cost).sum()
        return RerankerOutputs(
            score=score,
            plan=plan,
            transported_mass=transported_mass,
            target_usage=target_usage,
        )
