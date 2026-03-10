from __future__ import annotations

import torch

from ciept.audit.losses import single_pass_intervention
from ciept.eval.metrics import mean_reciprocal_rank, recall_at_1
from ciept.train.losses import combined_training_loss, confidence_weighted_listmle
from ciept.transport.reranker import CapacityCalibratedPartialTransportReranker
from ciept.transport.types import RerankerInputs


def build_toy_batch() -> dict:
    return {
        "user_nodes": torch.tensor([[1.0, 0.0], [0.8, 0.2]], dtype=torch.float32),
        "pos_item_nodes": torch.tensor([[1.0, 0.0], [0.7, 0.3]], dtype=torch.float32),
        "neg_item_nodes": torch.tensor(
            [
                [[0.0, 1.0], [0.2, 0.8]],
                [[0.3, 0.7], [0.1, 0.9]],
            ],
            dtype=torch.float32,
        ),
        "source_mass": torch.tensor([0.6, 0.4], dtype=torch.float32),
        "pos_target_capacity": torch.tensor([0.5, 0.5], dtype=torch.float32),
        "neg_target_capacity": torch.tensor(
            [
                [0.5, 0.5],
                [0.5, 0.5],
            ],
            dtype=torch.float32,
        ),
        "mass_budget": 0.8,
        "pos_nuisance_mask": torch.tensor([0.0, 1.0], dtype=torch.float32),
        "sample_weight": torch.tensor([1.0], dtype=torch.float32),
    }


def _run_reranker(
    reranker: CapacityCalibratedPartialTransportReranker,
    user_nodes: torch.Tensor,
    item_nodes: torch.Tensor,
    source_mass: torch.Tensor,
    target_capacity: torch.Tensor,
    mass_budget: float,
):
    return reranker(
        RerankerInputs(
            user_nodes=user_nodes,
            item_nodes=item_nodes,
            source_mass=source_mass,
            target_capacity=target_capacity,
            mass_budget=mass_budget,
        )
    )


def train_step(
    reranker: CapacityCalibratedPartialTransportReranker,
    batch: dict,
    tau: float = 0.5,
    lambda_intervention: float = 0.5,
    listmle_tau: float = 0.2,
) -> dict:
    if batch["neg_item_nodes"].shape[0] == 0:
        raise ValueError("neg_item_nodes must not be empty")
    if batch["sample_weight"].item() <= 0:
        raise ValueError("sample_weight must be positive")

    score_scale = torch.nn.Parameter(torch.tensor(1.0, dtype=torch.float32))
    score_bias = torch.nn.Parameter(torch.tensor(0.0, dtype=torch.float32))

    pos_outputs = _run_reranker(
        reranker,
        batch["user_nodes"],
        batch["pos_item_nodes"],
        batch["source_mass"],
        batch["pos_target_capacity"],
        batch["mass_budget"],
    )
    pos_score = pos_outputs.score * score_scale + score_bias

    neg_scores = []
    for neg_item_nodes, neg_capacity in zip(batch["neg_item_nodes"], batch["neg_target_capacity"]):
        neg_outputs = _run_reranker(
            reranker,
            batch["user_nodes"],
            neg_item_nodes,
            batch["source_mass"],
            neg_capacity,
            batch["mass_budget"],
        )
        neg_scores.append(neg_outputs.score * score_scale + score_bias)

    neg_scores_tensor = torch.stack(neg_scores).unsqueeze(0)
    ranking_loss = confidence_weighted_listmle(
        pos_score.unsqueeze(0),
        neg_scores_tensor,
        batch["sample_weight"],
        tau=listmle_tau,
    )

    intervention = single_pass_intervention(
        score_full=pos_score,
        plan=pos_outputs.plan,
        q_cap=batch["pos_target_capacity"],
        item_nodes=batch["pos_item_nodes"],
        user_nodes=batch["user_nodes"],
        nuisance_mask=batch["pos_nuisance_mask"],
        tau=tau,
    )
    total_loss = combined_training_loss(
        ranking_loss,
        intervention.loss_total,
        lambda_intervention=lambda_intervention,
    )
    if not torch.isfinite(total_loss):
        raise ValueError("Total loss contains NaN or Inf")
    total_loss.backward()

    return {
        "ranking_loss": ranking_loss,
        "intervention_loss": intervention.loss_total,
        "total_loss": total_loss,
        "pos_score": pos_score.detach(),
        "neg_scores": neg_scores_tensor.detach(),
    }


def eval_step(
    reranker: CapacityCalibratedPartialTransportReranker,
    batch: dict,
) -> dict:
    pos_outputs = _run_reranker(
        reranker,
        batch["user_nodes"],
        batch["pos_item_nodes"],
        batch["source_mass"],
        batch["pos_target_capacity"],
        batch["mass_budget"],
    )
    neg_scores = []
    for neg_item_nodes, neg_capacity in zip(batch["neg_item_nodes"], batch["neg_target_capacity"]):
        neg_outputs = _run_reranker(
            reranker,
            batch["user_nodes"],
            neg_item_nodes,
            batch["source_mass"],
            neg_capacity,
            batch["mass_budget"],
        )
        neg_scores.append(neg_outputs.score.detach())

    neg_scores_tensor = torch.stack(neg_scores)
    return {
        "pos_score": pos_outputs.score.detach(),
        "neg_scores": neg_scores_tensor,
        "recall_at_1": recall_at_1(pos_outputs.score.detach(), neg_scores_tensor),
        "mrr": mean_reciprocal_rank(pos_outputs.score.detach(), neg_scores_tensor),
    }
