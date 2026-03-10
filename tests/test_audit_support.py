from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.audit.support import normalized_support, support_to_logits


def test_normalized_support_uses_capacity_prior():
    plan = torch.tensor(
        [[0.2, 0.1], [0.1, 0.2]],
        dtype=torch.float32,
    )
    q_cap = torch.tensor([0.2, 0.6], dtype=torch.float32)

    outputs = normalized_support(plan, q_cap, eps=1e-6)

    assert outputs.raw_support.shape == (2,)
    assert outputs.normalized_support[0] > outputs.normalized_support[1]


def test_support_to_logits_returns_finite_values():
    norm_support = torch.tensor([0.2, 0.8], dtype=torch.float32)
    logits = support_to_logits(norm_support, eps=1e-6)

    assert torch.isfinite(logits).all()
