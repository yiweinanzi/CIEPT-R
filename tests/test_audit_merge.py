from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.audit.adjudication import init_adjudication_queue
from ciept.audit.vlm_io import merge_vlm_predictions


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")


def test_merge_vlm_predictions_writes_annotated_examples_and_updates_manifest(tmp_path):
    audit_examples = tmp_path / "audit_examples.jsonl"
    predictions = tmp_path / "vlm_predictions.jsonl"
    manifest = tmp_path / "manifest.json"
    annotated = tmp_path / "audit_examples_annotated.jsonl"

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
                "vision_nodes": [],
                "nuisance_mask": {"text_mask": [True], "vision_mask": []},
                "review_status": "pending",
            }
        ],
    )
    write_jsonl(
        predictions,
        [
            {
                "audit_id": "audit-1",
                "predicted_minimal_evidence": ["t1"],
                "predicted_nuisance_nodes": ["t1"],
                "confidence": 0.9,
                "raw_response": "{}",
            }
        ],
    )
    manifest.write_text(json.dumps({"sample_count": 1}), encoding="utf-8")

    merge_vlm_predictions(audit_examples, predictions, manifest, annotated)

    assert annotated.exists()
    merged_manifest = json.loads(manifest.read_text())
    assert merged_manifest["prediction_coverage"] == 1


def test_init_adjudication_queue_writes_pending_records(tmp_path):
    annotated = tmp_path / "annotated.jsonl"
    queue_path = tmp_path / "adjudication_queue.jsonl"
    write_jsonl(
        annotated,
        [
            {
                "audit_id": "audit-1",
                "source_example_id": "ex-1",
                "label": 1,
                "vlm_prediction": {
                    "predicted_minimal_evidence": ["t1"],
                    "predicted_nuisance_nodes": ["t1"],
                    "confidence": 0.9,
                },
            }
        ],
    )

    init_adjudication_queue(annotated, queue_path)

    assert queue_path.exists()
    content = queue_path.read_text(encoding="utf-8")
    assert "pending" in content
