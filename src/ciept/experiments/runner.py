from __future__ import annotations

from pathlib import Path

from ciept.experiments.io import prepare_run_directory, write_experiment_outputs
from ciept.experiments import ablation, efficiency, faithfulness, main_results, robustness, usage
from ciept.experiments.types import ExperimentResult

EXPERIMENTS = {
    "main_results": main_results.run,
    "robustness": robustness.run,
    "faithfulness": faithfulness.run,
    "ablation": ablation.run,
    "usage": usage.run,
    "efficiency": efficiency.run,
}


def run_experiment(experiment_name: str, results_root: Path, run_id: str) -> ExperimentResult:
    fn = EXPERIMENTS.get(experiment_name)
    if fn is None:
        raise ValueError(f"Unknown experiment: {experiment_name}")
    result = fn(run_id)

    if not result.metrics:
        raise ValueError("Experiment returned empty metrics")

    run_dir = prepare_run_directory(results_root, experiment_name, run_id)
    write_experiment_outputs(run_dir, result)
    return result
