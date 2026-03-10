from __future__ import annotations

from ciept.experiments.types import ExperimentResult


def run(run_id: str) -> ExperimentResult:
    return ExperimentResult(
        experiment_name="faithfulness",
        run_id=run_id,
        metrics={
            "support_precision": 0.8,
            "support_recall": 0.75,
            "support_f1": 0.774,
            "leakage_ratio": 0.18,
            "sufficiency_gap": 0.05,
            "comprehensiveness_gap": 0.31,
        },
        notes=["Toy faithfulness outputs wired to the expected result schema."],
    )
