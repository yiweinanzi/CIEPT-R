from __future__ import annotations

from ciept.experiments.types import ExperimentResult


def run(run_id: str) -> ExperimentResult:
    return ExperimentResult(
        experiment_name="ablation",
        run_id=run_id,
        metrics={
            "full_model_score": 0.41,
            "wo_capacity_prior_score": 0.34,
            "wo_intervention_loss_score": 0.36,
        },
        notes=["Toy ablation outputs that preserve the expected comparison schema."],
    )
