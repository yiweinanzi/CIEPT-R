from __future__ import annotations

from ciept.experiments.types import ExperimentResult


def run(run_id: str) -> ExperimentResult:
    return ExperimentResult(
        experiment_name="main_results",
        run_id=run_id,
        metrics={
            "clean_ndcg_at_20": 0.42,
            "high_conflict_ndcg_at_20": 0.35,
            "missing_modality_ndcg_at_20": 0.31,
            "long_tail_ndcg_at_20": 0.28,
        },
        notes=["Toy placeholder results for protocol validation."],
    )
