from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.baselines.data_bridge import bridge_presplit_dataset_to_recbole


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_bridge_presplit_dataset_to_recbole_writes_atomic_benchmark_files(tmp_path):
    source_dir = tmp_path / "processed" / "amazon-beauty"
    source_dir.mkdir(parents=True)
    _write_csv(
        source_dir / "train.csv",
        [
            {"user_id": "u1", "item_id": "i1", "rating": 1.0, "timestamp": 10},
            {"user_id": "u2", "item_id": "i2", "rating": 1.0, "timestamp": 20},
        ],
    )
    _write_csv(
        source_dir / "valid.csv",
        [{"user_id": "u1", "item_id": "i2", "rating": 1.0, "timestamp": 30}],
    )
    _write_csv(
        source_dir / "test.csv",
        [{"user_id": "u2", "item_id": "i1", "rating": 1.0, "timestamp": 40}],
    )
    _write_csv(
        source_dir / "items.csv",
        [
            {"item_id": "i1", "category": "beauty", "has_image": "true"},
            {"item_id": "i2", "category": "beauty", "has_image": "false"},
        ],
    )

    bridge = bridge_presplit_dataset_to_recbole(
        dataset_name="amazon-beauty",
        source_dir=source_dir,
        output_dir=tmp_path / "bridge",
    )

    assert bridge.dataset_name == "amazon-beauty"
    assert bridge.benchmark_filename == ["train", "valid", "test"]
    assert (bridge.output_dir / "amazon-beauty.train.inter").exists()
    assert (bridge.output_dir / "amazon-beauty.valid.inter").exists()
    assert (bridge.output_dir / "amazon-beauty.test.inter").exists()
    assert (bridge.output_dir / "amazon-beauty.item").exists()

    train_lines = (bridge.output_dir / "amazon-beauty.train.inter").read_text(encoding="utf-8").splitlines()
    item_lines = (bridge.output_dir / "amazon-beauty.item").read_text(encoding="utf-8").splitlines()
    manifest = json.loads((bridge.output_dir / "bridge_manifest.json").read_text(encoding="utf-8"))

    assert train_lines[0] == "user_id:token\titem_id:token\trating:float\ttimestamp:float"
    assert item_lines[0] == "item_id:token\tcategory:token\thas_image:token"
    assert manifest["dataset_name"] == "amazon-beauty"
    assert manifest["benchmark_filename"] == ["train", "valid", "test"]


def test_bridge_presplit_dataset_to_recbole_requires_all_split_files(tmp_path):
    source_dir = tmp_path / "processed" / "amazon-beauty"
    source_dir.mkdir(parents=True)
    _write_csv(
        source_dir / "train.csv",
        [{"user_id": "u1", "item_id": "i1"}],
    )
    _write_csv(
        source_dir / "valid.csv",
        [{"user_id": "u1", "item_id": "i2"}],
    )

    with pytest.raises(ValueError, match="Missing required split file: test.csv"):
        bridge_presplit_dataset_to_recbole(
            dataset_name="amazon-beauty",
            source_dir=source_dir,
            output_dir=tmp_path / "bridge",
        )
