from pathlib import Path
import json
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.experiments.runner import run_experiment


def test_run_experiment_writes_metrics_and_summary(tmp_path):
    result = run_experiment("main_results", results_root=tmp_path, run_id="test-run")

    run_dir = tmp_path / "main_results" / "test-run"
    assert result.experiment_name == "main_results"
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "summary.md").exists()

    payload = json.loads((run_dir / "metrics.json").read_text())
    assert payload["experiment_name"] == "main_results"


def test_unknown_experiment_name_raises(tmp_path):
    with pytest.raises(ValueError, match="Unknown experiment"):
        run_experiment("unknown_experiment", results_root=tmp_path, run_id="bad-run")
