from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.audit.audit_dataset import build_audit_dataset
from ciept.audit.vlm_io import export_vlm_requests


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")


def test_build_audit_dataset_writes_examples_and_manifest(tmp_path):
    stress_path = tmp_path / "stress.jsonl"
    output_dir = tmp_path / "audit"
    write_jsonl(
        stress_path,
        [
            {
                "example_id": "ex-1",
                "label": 1,
                "perturbation_family": "positive_nuisance",
                "strength": 0.1,
                "perturbed_text_nodes": [{"node_id": "t1", "content": "running shoes", "source": "title"}],
                "perturbed_vision_nodes": [{"node_id": "v1", "content": "plain background", "source": "image_region"}],
                "text_mask": [True],
                "vision_mask": [False],
            }
        ],
    )

    build_audit_dataset(stress_path, output_dir)

    assert (output_dir / "audit_examples.jsonl").exists()
    assert (output_dir / "manifest.json").exists()


def test_export_vlm_requests_writes_request_records(tmp_path):
    audit_examples = tmp_path / "audit_examples.jsonl"
    requests_path = tmp_path / "vlm_requests.jsonl"
    write_jsonl(
        audit_examples,
        [
            {
                "audit_id": "audit-1",
                "source_example_id": "ex-1",
                "label": 1,
                "perturbation_family": "positive_nuisance",
                "strength": 0.1,
                "text_nodes": [{"node_id": "t1", "content": "running shoes", "source": "title"}],
                "vision_nodes": [{"node_id": "v1", "content": "plain background", "source": "image_region"}],
                "nuisance_mask": {"text_mask": [True], "vision_mask": [False]},
                "review_status": "pending",
            }
        ],
    )

    export_vlm_requests(audit_examples, requests_path, prompt_version="v1")

    assert requests_path.exists()
