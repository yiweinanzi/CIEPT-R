from __future__ import annotations

import json
from pathlib import Path

from ciept.experiments.types import ExperimentResult


def prepare_run_directory(results_root: Path, experiment_name: str, run_id: str) -> Path:
    run_dir = Path(results_root) / experiment_name / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_experiment_outputs(run_dir: Path, result: ExperimentResult) -> None:
    metrics_path = run_dir / "metrics.json"
    summary_path = run_dir / "summary.md"

    metrics_payload = {
        "experiment_name": result.experiment_name,
        "run_id": result.run_id,
        "metrics": result.metrics,
        "notes": result.notes,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2, sort_keys=True), encoding="utf-8")
    summary_path.write_text(
        "\n".join(
            [
                f"# {result.experiment_name}",
                "",
                f"- run_id: {result.run_id}",
                "- mode: toy/placeholder",
                "",
                "## Metrics",
                *[f"- {key}: {value}" for key, value in result.metrics.items()],
                "",
                "## Notes",
                *[f"- {note}" for note in result.notes],
            ]
        ),
        encoding="utf-8",
    )
