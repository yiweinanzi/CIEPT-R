from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.experiments.runner import run_experiment


def test_main_results_experiment_emits_required_metrics(tmp_path):
    run_experiment("main_results", results_root=tmp_path, run_id="main-run")
    metrics = json.loads((tmp_path / "main_results" / "main-run" / "metrics.json").read_text())

    keys = metrics["metrics"].keys()
    assert "clean_ndcg_at_20" in keys
    assert "high_conflict_ndcg_at_20" in keys


def test_usage_experiment_emits_required_metrics(tmp_path):
    run_experiment("usage", results_root=tmp_path, run_id="usage-run")
    metrics = json.loads((tmp_path / "usage" / "usage-run" / "metrics.json").read_text())

    keys = metrics["metrics"].keys()
    assert "image_shuffle_drop_rate" in keys
    assert "transported_mass_ratio" in keys
