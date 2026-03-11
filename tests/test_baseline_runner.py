from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.baselines.runner import BaselineRunRequest, run_baseline


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_presplit_dataset(source_dir: Path) -> None:
    source_dir.mkdir(parents=True)
    _write_csv(
        source_dir / "train.csv",
        [
            {"user_id": "u1", "item_id": "i1", "rating": 1.0, "timestamp": 10},
            {"user_id": "u1", "item_id": "i2", "rating": 1.0, "timestamp": 11},
            {"user_id": "u2", "item_id": "i2", "rating": 1.0, "timestamp": 12},
        ],
    )
    _write_csv(
        source_dir / "valid.csv",
        [{"user_id": "u2", "item_id": "i1", "rating": 1.0, "timestamp": 20}],
    )
    _write_csv(
        source_dir / "test.csv",
        [{"user_id": "u3", "item_id": "i2", "rating": 1.0, "timestamp": 30}],
    )
    _write_csv(
        source_dir / "items.csv",
        [
            {"item_id": "i1", "title": "item one", "has_image": "true"},
            {"item_id": "i2", "title": "item two", "has_image": "false"},
        ],
    )


def _make_request(tmp_path: Path, baseline_name: str) -> BaselineRunRequest:
    baselines_dir = tmp_path / "baselines"
    baselines_dir.mkdir(parents=True, exist_ok=True)

    archive_map = {
        "LightGCN": "LightGCN-master.zip",
        "VBPR": "VBPR-PyTorch-main.zip",
        "BM3": "BM3-master.zip",
        "I3-MRec": "I3-MRec-main.zip",
        "Training-free Graph-based Imputation": "Graph-Missing-Modalities-TKDE-master.zip",
        "Guider": "Guider-main.zip",
        "MAGNET": "MAGNET-main.zip",
        "SMORE": "SMORE-main.zip",
        "DiffMM": "DiffMM-main.zip",
        "MixRec": "MixRec-main.zip",
        "CLEAR": "CLEAR-replication-main.zip",
    }
    archive_name = archive_map[baseline_name]
    archive_path = baselines_dir / archive_name
    if baseline_name in {"LightGCN", "CLEAR", "MixRec"}:
        archive_path.write_text("", encoding="utf-8")
    else:
        root_name = archive_name.removesuffix(".zip")
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr(f"{root_name}/README.md", "demo")

    dataset_dir = tmp_path / "processed" / "amazon-beauty"
    _write_presplit_dataset(dataset_dir)
    return BaselineRunRequest(
        baseline_name=baseline_name,
        dataset_name="amazon-beauty",
        source_dir=dataset_dir,
        baselines_dir=baselines_dir,
        results_root=tmp_path / "results",
        run_id=f"{baseline_name.lower().replace(' ', '-')}-smoke",
    )


def test_run_baseline_writes_standardized_outputs_for_recbole_baseline(tmp_path):
    request = _make_request(tmp_path, "LightGCN")
    observed: dict[str, object] = {}

    def fake_recbole(record, prepared, run_dir):
        observed["mode"] = record["integration_mode"]
        observed["dataset_format"] = prepared.dataset_format
        observed["benchmark_filename"] = prepared.metadata["benchmark_filename"]
        observed["prepared_dir"] = str(prepared.output_dir)
        return {"metrics": {"Recall@10": 0.42, "NDCG@10": 0.31}, "notes": ["fake recbole executor"]}

    result = run_baseline(request, executors={"recbole": fake_recbole})
    payload = json.loads((result.run_dir / "metrics.json").read_text(encoding="utf-8"))

    assert payload["baseline_name"] == "LightGCN"
    assert payload["metrics"]["Recall@10"] == 0.42
    assert observed["mode"] == "recbole"
    assert observed["dataset_format"] == "recbole"
    assert observed["benchmark_filename"] == ["train", "valid", "test"]
    assert Path(observed["prepared_dir"]).exists()


def test_run_baseline_writes_standardized_outputs_for_vbpr_baseline(tmp_path):
    request = _make_request(tmp_path, "VBPR")
    observed: dict[str, object] = {}

    def fake_vbpr(record, prepared, run_dir):
        observed["mode"] = record["integration_mode"]
        observed["dataset_format"] = prepared.dataset_format
        observed["has_visual_features"] = (prepared.output_dir / "visual_features.npy").exists()
        return {"metrics": {"AUC": 0.61}, "notes": ["fake vbpr executor"]}

    result = run_baseline(request, executors={"vbpr_python": fake_vbpr})
    payload = json.loads((result.run_dir / "metrics.json").read_text(encoding="utf-8"))

    assert payload["baseline_name"] == "VBPR"
    assert payload["metrics"]["AUC"] == 0.61
    assert observed["mode"] == "vbpr_python"
    assert observed["dataset_format"] == "vbpr"
    assert observed["has_visual_features"] is True


def test_run_baseline_writes_standardized_outputs_for_mmrec_baseline(tmp_path):
    request = _make_request(tmp_path, "BM3")
    observed: dict[str, object] = {}

    def fake_mmrec(record, prepared, run_dir):
        observed["mode"] = record["integration_mode"]
        observed["dataset_format"] = prepared.dataset_format
        observed["inter_file"] = prepared.metadata["inter_file_name"]
        return {"metrics": {"Recall@20": 0.2}, "notes": ["fake mmrec executor"]}

    result = run_baseline(request, executors={"mmrec": fake_mmrec})
    payload = json.loads((result.run_dir / "metrics.json").read_text(encoding="utf-8"))

    assert payload["baseline_name"] == "BM3"
    assert observed["mode"] == "mmrec"
    assert observed["dataset_format"] == "mmrec"
    assert observed["inter_file"] == "amazon-beauty.inter"


def test_run_baseline_writes_standardized_outputs_for_i3mrec_baseline(tmp_path):
    request = _make_request(tmp_path, "I3-MRec")
    observed: dict[str, object] = {}

    def fake_i3mrec(record, prepared, run_dir):
        observed["mode"] = record["integration_mode"]
        observed["dataset_format"] = prepared.dataset_format
        observed["inter_file"] = prepared.metadata["inter_file_name"]
        return {"metrics": {"Recall@20": 0.11}, "notes": ["fake i3mrec executor"]}

    result = run_baseline(request, executors={"i3mrec": fake_i3mrec})
    payload = json.loads((result.run_dir / "metrics.json").read_text(encoding="utf-8"))

    assert payload["baseline_name"] == "I3-MRec"
    assert observed["mode"] == "i3mrec"
    assert observed["dataset_format"] == "i3mrec"
    assert observed["inter_file"] == "amazon-beauty.inter"


def test_run_baseline_writes_standardized_outputs_for_graph_imputation_baseline(tmp_path):
    request = _make_request(tmp_path, "Training-free Graph-based Imputation")
    observed: dict[str, object] = {}

    def fake_graph(record, prepared, run_dir):
        observed["mode"] = record["integration_mode"]
        observed["dataset_format"] = prepared.dataset_format
        observed["train_indexed"] = (prepared.output_dir / "train_indexed.tsv").exists()
        return {"metrics": {"imputed_items": 2.0}, "notes": ["fake graph executor"]}

    result = run_baseline(request, executors={"graph_imputation": fake_graph})
    payload = json.loads((result.run_dir / "metrics.json").read_text(encoding="utf-8"))

    assert payload["baseline_name"] == "Training-free Graph-based Imputation"
    assert observed["mode"] == "graph_imputation"
    assert observed["dataset_format"] == "graph_imputation"
    assert observed["train_indexed"] is True


def test_run_baseline_rejects_asset_mismatch_baselines(tmp_path):
    request = _make_request(tmp_path, "CLEAR")

    with pytest.raises(ValueError, match="asset_mismatch"):
        run_baseline(request)


def test_run_baseline_writes_standardized_outputs_for_guided_mmrec_baseline(tmp_path):
    request = _make_request(tmp_path, "Guider")
    observed: dict[str, object] = {}

    def fake_guided(record, prepared, run_dir):
        observed["mode"] = record["integration_mode"]
        observed["dataset_format"] = prepared.dataset_format
        observed["inter_file"] = prepared.metadata["inter_file_name"]
        return {"metrics": {"Recall@20": 0.3}, "notes": ["fake guider executor"]}

    result = run_baseline(request, executors={"guided_mmrec": fake_guided})
    payload = json.loads((result.run_dir / "metrics.json").read_text(encoding="utf-8"))

    assert payload["baseline_name"] == "Guider"
    assert observed["mode"] == "guided_mmrec"
    assert observed["dataset_format"] == "mmrec"
    assert observed["inter_file"] == "amazon-beauty.inter"


def test_run_baseline_writes_standardized_outputs_for_candidate_mmrec_baselines(tmp_path):
    for baseline_name in ["SMORE"]:
        request = _make_request(tmp_path / baseline_name, baseline_name)
        observed: dict[str, object] = {}

        def fake_mmrec(record, prepared, run_dir):
            observed["baseline"] = record["name"]
            observed["mode"] = record["integration_mode"]
            observed["dataset_format"] = prepared.dataset_format
            return {"metrics": {"Recall@20": 0.4}, "notes": ["fake candidate mmrec executor"]}

        result = run_baseline(request, executors={"mmrec": fake_mmrec})
        payload = json.loads((result.run_dir / "metrics.json").read_text(encoding="utf-8"))

        assert payload["baseline_name"] == baseline_name
        assert observed["baseline"] == baseline_name
        assert observed["mode"] == "mmrec"
        assert observed["dataset_format"] == "mmrec"


def test_run_baseline_writes_standardized_outputs_for_diffmm_baseline(tmp_path):
    request = _make_request(tmp_path, "DiffMM")
    observed: dict[str, object] = {}

    def fake_diffmm(record, prepared, run_dir):
        observed["mode"] = record["integration_mode"]
        observed["dataset_format"] = prepared.dataset_format
        observed["train_matrix_file"] = prepared.metadata["train_matrix_file"]
        return {"metrics": {"Recall@20": 0.22}, "notes": ["fake diffmm executor"]}

    result = run_baseline(request, executors={"diffmm": fake_diffmm})
    payload = json.loads((result.run_dir / "metrics.json").read_text(encoding="utf-8"))

    assert payload["baseline_name"] == "DiffMM"
    assert observed["mode"] == "diffmm"
    assert observed["dataset_format"] == "diffmm"
    assert observed["train_matrix_file"] == "trnMat.pkl"


def test_run_baseline_rejects_runtime_mismatch_baselines(tmp_path):
    request = _make_request(tmp_path, "MixRec")

    with pytest.raises(ValueError, match="runtime_mismatch"):
        run_baseline(request)


def test_run_baseline_rejects_asset_incomplete_baselines(tmp_path):
    request = _make_request(tmp_path, "MAGNET")

    with pytest.raises(ValueError, match="asset_incomplete"):
        run_baseline(request)
