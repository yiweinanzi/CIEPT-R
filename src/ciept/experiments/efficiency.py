from __future__ import annotations

from ciept.experiments.types import ExperimentResult


def run(run_id: str) -> ExperimentResult:
    return ExperimentResult(
        experiment_name="efficiency",
        run_id=run_id,
        metrics={
            "forward_time_ms": 4.2,
            "train_step_time_ms": 9.7,
            "peak_memory_mb": 128.0,
        },
        notes=["Toy efficiency outputs for result-directory validation."],
    )
