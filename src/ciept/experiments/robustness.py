from __future__ import annotations

from ciept.experiments.types import ExperimentResult


def run(run_id: str) -> ExperimentResult:
    return ExperimentResult(
        experiment_name="robustness",
        run_id=run_id,
        metrics={
            "retention_at_0_1": 0.92,
            "retention_at_0_3": 0.81,
            "retention_at_0_5": 0.67,
        },
        notes=["Toy robustness retention values over perturbation strengths."],
    )
