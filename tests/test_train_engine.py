from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.train.engine import build_toy_batch, eval_step, train_step
from ciept.transport.reranker import CapacityCalibratedPartialTransportReranker


def test_train_step_returns_losses_and_allows_backward():
    reranker = CapacityCalibratedPartialTransportReranker()
    batch = build_toy_batch()

    outputs = train_step(reranker, batch, tau=0.5, lambda_intervention=0.5)

    assert outputs["ranking_loss"].ndim == 0
    assert outputs["intervention_loss"].ndim == 0
    assert outputs["total_loss"].ndim == 0
    assert outputs["total_loss"].requires_grad


def test_eval_step_returns_recall_and_mrr():
    reranker = CapacityCalibratedPartialTransportReranker()
    batch = build_toy_batch()

    metrics = eval_step(reranker, batch)

    assert "recall_at_1" in metrics
    assert "mrr" in metrics
    assert 0.0 <= metrics["recall_at_1"] <= 1.0
    assert 0.0 <= metrics["mrr"] <= 1.0
