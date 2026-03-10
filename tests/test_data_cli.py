from pathlib import Path
import csv
import json
import os
import subprocess
import sys


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_cli_writes_split_files_and_missing_modality_report(tmp_path):
    interactions_path = tmp_path / "interactions.csv"
    items_path = tmp_path / "items.csv"
    output_dir = tmp_path / "processed"

    write_csv(
        interactions_path,
        [
            {"user_id": "u1", "item_id": "i1", "timestamp": "1"},
            {"user_id": "u1", "item_id": "i2", "timestamp": "2"},
            {"user_id": "u1", "item_id": "i3", "timestamp": "3"},
            {"user_id": "u2", "item_id": "i1", "timestamp": "4"},
            {"user_id": "u2", "item_id": "i2", "timestamp": "5"},
            {"user_id": "u2", "item_id": "i3", "timestamp": "6"},
            {"user_id": "u3", "item_id": "i1", "timestamp": "7"},
            {"user_id": "u3", "item_id": "i2", "timestamp": "8"},
            {"user_id": "u3", "item_id": "i3", "timestamp": "9"},
            {"user_id": "u4", "item_id": "i1", "timestamp": "10"}
        ],
        ["user_id", "item_id", "timestamp"],
    )
    write_csv(
        items_path,
        [
            {"item_id": "i1", "has_text": "1", "has_image": "1", "has_ocr": "1"},
            {"item_id": "i2", "has_text": "1", "has_image": "0", "has_ocr": "1"},
            {"item_id": "i3", "has_text": "1", "has_image": "1", "has_ocr": "0"},
        ],
        ["item_id", "has_text", "has_image", "has_ocr"],
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ciept.data.cli",
            "--interactions",
            str(interactions_path),
            "--items",
            str(items_path),
            "--output-dir",
            str(output_dir),
            "--min-user-degree",
            "2",
            "--min-item-degree",
            "2"
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "train.csv").exists()
    assert (output_dir / "valid.csv").exists()
    assert (output_dir / "test.csv").exists()
    assert (output_dir / "protocol_summary.json").exists()

    summary = json.loads((output_dir / "protocol_summary.json").read_text())

    assert summary["split_counts"] == {"train": 7, "valid": 1, "test": 1}
    assert summary["protocol"]["split_strategy"] == "global_temporal_80_10_10"
    assert summary["protocol"]["setting"] == "transductive"
    assert summary["protocol"]["cold_start_policy"] == "report_separately"
    assert summary["missing_modality"]["items_with_missing_modalities"] == 2
