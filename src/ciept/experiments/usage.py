from __future__ import annotations

from ciept.experiments.types import ExperimentResult


def run(run_id: str) -> ExperimentResult:
    return ExperimentResult(
        experiment_name="usage",
        run_id=run_id,
        metrics={
            "image_shuffle_drop_rate": 0.22,
            "random_caption_drop_rate": 0.17,
            "missing_modality_drop": 0.29,
            "transported_mass_ratio": 0.74,
        },
        notes=["Toy usage-diagnosis outputs for schema validation."],
    )
