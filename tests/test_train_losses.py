from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.train.losses import confidence_weighted_listmle


def test_confidence_weighted_listmle_prefers_high_positive_score():
    pos_high = torch.tensor([1.2], dtype=torch.float32)
    pos_low = torch.tensor([0.2], dtype=torch.float32)
    neg_scores = torch.tensor([[0.3, 0.1]], dtype=torch.float32)
    weight = torch.tensor([1.0], dtype=torch.float32)

    loss_high = confidence_weighted_listmle(pos_high, neg_scores, weight, tau=0.2)
    loss_low = confidence_weighted_listmle(pos_low, neg_scores, weight, tau=0.2)

    assert loss_high < loss_low
