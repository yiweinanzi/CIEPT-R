from pathlib import Path
import json
import os
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.data.stress_pipeline import generate_conflict_stress_dataset


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")


def test_pipeline_writes_examples_masks_summary_and_review_queue(tmp_path):
    input_path = tmp_path / "examples.jsonl"
    output_dir = tmp_path / "out"
    write_jsonl(
        input_path,
        [
            {
                "example_id": "ex-1",
                "label": 1,
                "text_nodes": [{"node_id": "t1", "content": "running shoes", "source": "title"}],
                "vision_nodes": [{"node_id": "v1", "content": "plain background", "source": "image_region"}],
            }
        ],
    )

    generate_conflict_stress_dataset(input_path, output_dir)

    assert (output_dir / "examples.jsonl").exists()
    assert (output_dir / "nuisance_mask.json").exists()
    assert (output_dir / "protocol_summary.json").exists()
    assert (output_dir / "review_queue.jsonl").exists()


def test_strength_levels_change_number_of_perturbed_nodes(tmp_path):
    input_path = tmp_path / "examples.jsonl"
    low_dir = tmp_path / "low"
    high_dir = tmp_path / "high"
    write_jsonl(
        input_path,
        [
            {
                "example_id": "ex-1",
                "label": 1,
                "text_nodes": [
                    {"node_id": "t1", "content": "node-1", "source": "title"},
                    {"node_id": "t2", "content": "node-2", "source": "title"},
                    {"node_id": "t3", "content": "node-3", "source": "title"},
                    {"node_id": "t4", "content": "node-4", "source": "title"},
                ],
                "vision_nodes": [],
            }
        ],
    )

    generate_conflict_stress_dataset(input_path, low_dir, strengths=[0.1])
    generate_conflict_stress_dataset(input_path, high_dir, strengths=[0.5])

    low_masks = json.loads((low_dir / "nuisance_mask.json").read_text())
    high_masks = json.loads((high_dir / "nuisance_mask.json").read_text())

    assert sum(low_masks["ex-1"]["text_mask"]) < sum(high_masks["ex-1"]["text_mask"])


def test_stress_cli_runs(tmp_path):
    input_path = tmp_path / "examples.jsonl"
    output_dir = tmp_path / "cli_out"
    write_jsonl(
        input_path,
        [
            {
                "example_id": "ex-1",
                "label": 0,
                "text_nodes": [{"node_id": "t1", "content": "dress shoe", "source": "title"}],
                "vision_nodes": [{"node_id": "v1", "content": "plain image", "source": "image_region"}],
            }
        ],
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ciept.data.stress_cli",
            "--input-jsonl",
            str(input_path),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "protocol_summary.json" in result.stdout
