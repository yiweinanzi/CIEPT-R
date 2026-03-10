from pathlib import Path
import sys

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.transport.reranker import CapacityCalibratedPartialTransportReranker
from ciept.transport.types import RerankerInputs


def test_reranker_rejects_feature_dimension_mismatch():
    reranker = CapacityCalibratedPartialTransportReranker()
    inputs = RerankerInputs(
        user_nodes=torch.randn(2, 3),
        item_nodes=torch.randn(2, 4),
        source_mass=torch.tensor([0.5, 0.5], dtype=torch.float32),
        target_capacity=torch.tensor([0.5, 0.5], dtype=torch.float32),
        mass_budget=0.6,
    )

    with pytest.raises(ValueError, match="feature dimension"):
        reranker(inputs)


def test_reranker_rejects_non_positive_mass_budget():
    reranker = CapacityCalibratedPartialTransportReranker()
    inputs = RerankerInputs(
        user_nodes=torch.randn(2, 3),
        item_nodes=torch.randn(2, 3),
        source_mass=torch.tensor([0.5, 0.5], dtype=torch.float32),
        target_capacity=torch.tensor([0.5, 0.5], dtype=torch.float32),
        mass_budget=0.0,
    )

    with pytest.raises(ValueError, match="Mass budget"):
        reranker(inputs)
