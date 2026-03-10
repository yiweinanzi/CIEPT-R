from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ciept.audit.audit_types import AuditDatasetManifest, AuditExample


def _load_jsonl(path: Path) -> list[dict]:
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def build_audit_dataset(stress_jsonl: Path, output_dir: Path) -> AuditDatasetManifest:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = _load_jsonl(Path(stress_jsonl))
    audit_examples: list[AuditExample] = []
    family_counts: dict[str, int] = {}
    strengths: list[float] = []

    for index, record in enumerate(records, start=1):
        audit = AuditExample(
            audit_id=f"audit-{index}",
            source_example_id=record["example_id"],
            label=int(record["label"]),
            perturbation_family=record["perturbation_family"],
            strength=float(record["strength"]),
            text_nodes=list(record.get("perturbed_text_nodes", [])),
            vision_nodes=list(record.get("perturbed_vision_nodes", [])),
            nuisance_mask={
                "text_mask": list(record.get("text_mask", [])),
                "vision_mask": list(record.get("vision_mask", [])),
            },
            review_status="pending",
        )
        audit_examples.append(audit)
        family_counts[audit.perturbation_family] = family_counts.get(audit.perturbation_family, 0) + 1
        if audit.strength not in strengths:
            strengths.append(audit.strength)

    (output_dir / "audit_examples.jsonl").write_text(
        "\n".join(json.dumps(asdict(example), ensure_ascii=True) for example in audit_examples),
        encoding="utf-8",
    )

    manifest = AuditDatasetManifest(
        sample_count=len(audit_examples),
        strengths=sorted(strengths),
        families=family_counts,
        metadata={"source": str(stress_jsonl)},
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(asdict(manifest), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest
