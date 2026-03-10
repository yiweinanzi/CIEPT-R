from __future__ import annotations

import json
from pathlib import Path


def _load_jsonl(path: Path) -> list[dict]:
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def init_adjudication_queue(annotated_examples_path: Path, output_path: Path) -> None:
    examples = _load_jsonl(Path(annotated_examples_path))
    if not examples:
        raise ValueError("Annotated examples must not be empty")

    queue = []
    for example in examples:
        queue.append(
            {
                "audit_id": example["audit_id"],
                "source_example_id": example["source_example_id"],
                "label": example["label"],
                "vlm_prediction": example.get("vlm_prediction", {}),
                "adjudicator_a": "",
                "adjudicator_b": "",
                "final_label": "",
                "status": "pending",
            }
        )

    Path(output_path).write_text(
        "\n".join(json.dumps(record, ensure_ascii=True) for record in queue),
        encoding="utf-8",
    )
