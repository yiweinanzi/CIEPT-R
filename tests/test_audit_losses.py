from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.audit.losses import leakage_ratio, single_pass_intervention


def test_leakage_ratio_uses_relative_support():
    norm_support = torch.tensor([0.2, 0.8], dtype=torch.float32)
    nuisance_mask = torch.tensor([1.0, 0.0], dtype=torch.float32)

    ratio = leakage_ratio(norm_support, nuisance_mask, eps=1e-6)

    assert abs(ratio.item() - 0.2) < 1e-6


def test_nuisance_case_produces_higher_leakage_loss_than_clean_case():
    score_full = torch.tensor(0.8, dtype=torch.float32)
    plan = torch.tensor([[0.3, 0.1], [0.2, 0.0]], dtype=torch.float32)
    q_cap = torch.tensor([0.4, 0.6], dtype=torch.float32)
    user_nodes = torch.tensor([[1.0, 0.0], [1.0, 0.0]], dtype=torch.float32)
    item_nodes = torch.tensor([[1.0, 0.0], [0.0, 1.0]], dtype=torch.float32)
    nuisance_heavy = torch.tensor([1.0, 0.0], dtype=torch.float32)
    nuisance_clean = torch.tensor([0.0, 0.0], dtype=torch.float32)

    out_heavy = single_pass_intervention(
        score_full=score_full,
        plan=plan,
        q_cap=q_cap,
        item_nodes=item_nodes,
        user_nodes=user_nodes,
        nuisance_mask=nuisance_heavy,
        tau=0.5,
    )
    out_clean = single_pass_intervention(
        score_full=score_full,
        plan=plan,
        q_cap=q_cap,
        item_nodes=item_nodes,
        user_nodes=user_nodes,
        nuisance_mask=nuisance_clean,
        tau=0.5,
    )

    assert out_heavy.loss_leakage > out_clean.loss_leakage
    assert out_heavy.gate.shape == q_cap.shape
    assert out_heavy.score_selected.ndim == 0
    assert out_heavy.score_removed.ndim == 0
