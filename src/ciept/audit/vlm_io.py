from __future__ import annotations

import json
from pathlib import Path


def _load_jsonl(path: Path) -> list[dict]:
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def export_vlm_requests(audit_examples_path: Path, output_path: Path, prompt_version: str) -> None:
    audit_examples = _load_jsonl(Path(audit_examples_path))
    requests = []
    for example in audit_examples:
        requests.append(
            {
                "audit_id": example["audit_id"],
                "prompt_version": prompt_version,
                "instruction": "Identify minimal sufficient evidence and nuisance nodes.",
                "evidence_payload": {
                    "text_nodes": example["text_nodes"],
                    "vision_nodes": example["vision_nodes"],
                    "nuisance_mask": example["nuisance_mask"],
                },
            }
        )
    Path(output_path).write_text(
        "\n".join(json.dumps(record, ensure_ascii=True) for record in requests),
        encoding="utf-8",
    )


def merge_vlm_predictions(
    audit_examples_path: Path,
    predictions_path: Path,
    manifest_path: Path,
    output_path: Path,
) -> None:
    examples = _load_jsonl(Path(audit_examples_path))
    predictions = _load_jsonl(Path(predictions_path))
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

    prediction_map = {record["audit_id"]: record for record in predictions}
    example_ids = {record["audit_id"] for record in examples}
    unknown_ids = sum(1 for record in predictions if record["audit_id"] not in example_ids)

    annotated = []
    coverage = 0
    missing = 0
    for example in examples:
        prediction = prediction_map.get(example["audit_id"])
        if prediction is None:
            missing += 1
            annotated.append({**example, "vlm_prediction": None, "annotation_source": None})
            continue
        coverage += 1
        annotated.append({**example, "vlm_prediction": prediction, "annotation_source": "vlm"})

    Path(output_path).write_text(
        "\n".join(json.dumps(record, ensure_ascii=True) for record in annotated),
        encoding="utf-8",
    )

    manifest["prediction_coverage"] = coverage
    manifest["missing_predictions"] = missing
    manifest["unknown_prediction_ids"] = unknown_ids
    Path(manifest_path).write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
