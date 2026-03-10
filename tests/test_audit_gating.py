from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.audit.gating import binary_gumbel_ste


def test_binary_gumbel_ste_stays_in_unit_interval():
    torch.manual_seed(0)
    logits = torch.tensor([0.0, 1.0, -1.0], dtype=torch.float32)

    gate = binary_gumbel_ste(logits, tau=0.5)

    assert gate.shape == logits.shape
    assert torch.all(gate >= 0.0)
    assert torch.all(gate <= 1.0)
