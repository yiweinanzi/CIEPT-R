from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ciept.data.stress_rules import (
    apply_negative_preserving_lure,
    apply_positive_preserving_nuisance,
)
from ciept.data.stress_types import PerturbationConfig, PerturbationExample, PerturbationRecord


def load_examples(input_jsonl: Path) -> list[PerturbationExample]:
    examples: list[PerturbationExample] = []
    for line in input_jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        required = {"example_id", "label", "text_nodes", "vision_nodes"}
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"Missing required fields: {sorted(missing)}")
        examples.append(
            PerturbationExample(
                example_id=payload["example_id"],
                label=int(payload["label"]),
                text_nodes=list(payload["text_nodes"]),
                vision_nodes=list(payload["vision_nodes"]),
            )
        )
    return examples


def _record_key(record: PerturbationRecord, single_strength: bool) -> str:
    if single_strength:
        return record.example_id
    return f"{record.example_id}__{record.perturbation_family}__{record.strength}"


def generate_conflict_stress_dataset(
    input_jsonl: Path,
    output_dir: Path,
    strengths: list[float] | None = None,
) -> dict:
    if strengths is None:
        strengths = [0.1, 0.3, 0.5]
    if any(strength not in {0.1, 0.3, 0.5} for strength in strengths):
        raise ValueError("strengths must be chosen from 0.1, 0.3, 0.5")

    examples = load_examples(Path(input_jsonl))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records: list[PerturbationRecord] = []
    skipped = 0
    rule_counts = {"positive_nuisance": 0, "negative_lure": 0}
    single_strength = len(strengths) == 1

    for example in examples:
        if not example.text_nodes and not example.vision_nodes:
            skipped += 1
            continue

        family = "positive_nuisance" if example.label > 0 else "negative_lure"
        for strength in strengths:
            config = PerturbationConfig(strength=strength, family=family)
            if family == "positive_nuisance":
                record = apply_positive_preserving_nuisance(example, config)
            else:
                record = apply_negative_preserving_lure(example, config)
            records.append(record)
            rule_counts[family] += 1

    examples_path = output_dir / "examples.jsonl"
    examples_path.write_text(
        "\n".join(json.dumps(asdict(record), ensure_ascii=True) for record in records),
        encoding="utf-8",
    )

    nuisance_mask = {
        _record_key(record, single_strength): {
            "text_mask": record.text_mask,
            "vision_mask": record.vision_mask,
            "perturbation_family": record.perturbation_family,
            "strength": record.strength,
            "mask_source": "rule",
        }
        for record in records
    }
    (output_dir / "nuisance_mask.json").write_text(
        json.dumps(nuisance_mask, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    summary = {
        "input_examples": len(examples),
        "generated_records": len(records),
        "skipped_examples": skipped,
        "strengths": strengths,
        "rule_counts": rule_counts,
        "output_dir": str(output_dir),
    }
    (output_dir / "protocol_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    review_lines = []
    for record in records:
        review_lines.append(
            json.dumps(
                {
                    "example_id": record.example_id,
                    "label": record.label,
                    "perturbation_family": record.perturbation_family,
                    "strength": record.strength,
                    "changed_fields": record.changed_fields,
                    "review_status": "pending",
                },
                ensure_ascii=True,
            )
        )
    (output_dir / "review_queue.jsonl").write_text("\n".join(review_lines), encoding="utf-8")
    return summary
