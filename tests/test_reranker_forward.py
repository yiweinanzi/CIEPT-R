from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.transport.reranker import CapacityCalibratedPartialTransportReranker
from ciept.transport.types import RerankerInputs


def make_inputs(mass_budget: float = 0.8, target_capacity: torch.Tensor | None = None) -> RerankerInputs:
    user_nodes = torch.tensor(
        [[0.0, 0.0], [1.0, 1.0]],
        dtype=torch.float32,
    )
    item_nodes = torch.tensor(
        [[0.1, 0.1], [1.5, 1.5]],
        dtype=torch.float32,
    )
    source_mass = torch.tensor([0.6, 0.5], dtype=torch.float32)
    if target_capacity is None:
        target_capacity = torch.tensor([0.5, 0.6], dtype=torch.float32)

    return RerankerInputs(
        user_nodes=user_nodes,
        item_nodes=item_nodes,
        source_mass=source_mass,
        target_capacity=target_capacity,
        mass_budget=mass_budget,
    )


def test_reranker_forward_returns_score_plan_and_usage():
    reranker = CapacityCalibratedPartialTransportReranker(epsilon=0.1, max_iters=200, penalty_strength=0.5)
    outputs = reranker(make_inputs())

    assert outputs.plan.shape == (2, 2)
    assert outputs.score.ndim == 0
    assert outputs.transported_mass.ndim == 0
    assert outputs.target_usage.shape == (2,)


def test_smaller_mass_budget_reduces_transported_mass():
    reranker = CapacityCalibratedPartialTransportReranker(epsilon=0.1, max_iters=200, penalty_strength=0.5)

    high_budget = reranker(make_inputs(mass_budget=0.8))
    low_budget = reranker(make_inputs(mass_budget=0.4))

    assert high_budget.transported_mass > low_budget.transported_mass


def test_smaller_target_capacity_caps_target_usage():
    reranker = CapacityCalibratedPartialTransportReranker(epsilon=0.1, max_iters=200, penalty_strength=0.5)

    high_capacity = reranker(make_inputs(target_capacity=torch.tensor([0.5, 0.6], dtype=torch.float32)))
    low_capacity = reranker(make_inputs(target_capacity=torch.tensor([0.2, 0.6], dtype=torch.float32)))

    assert low_capacity.target_usage[0] < high_capacity.target_usage[0]
    assert low_capacity.target_usage[0] <= 0.2 + 1e-4
