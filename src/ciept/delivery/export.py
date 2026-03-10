from __future__ import annotations

import json
from pathlib import Path

from ciept.delivery.manifest import build_manifest, build_results_index, build_task_snapshot
from ciept.delivery.review import build_implementation_review, build_required_assets


def build_delivery_bundle(project_root: Path, output_dir: Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(project_root)
    results_index = build_results_index(project_root)
    task_snapshot = build_task_snapshot(project_root)

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "results_index.json").write_text(
        json.dumps(results_index, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "task_snapshot.json").write_text(
        json.dumps(task_snapshot, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "reproducibility_checklist.md").write_text(
        "\n".join(
            [
                "# Reproducibility Checklist",
                "",
                "- Install dependencies from `pyproject.toml`",
                "- Run `python -m pytest -v`",
                "- Run `bash scripts/check.sh`",
                "- Run `python -m ciept.train.cli --mode train`",
                "- Run `python -m ciept.train.cli --mode eval`",
                "- Run `python -m ciept.data.stress_cli --input-jsonl ... --output-dir ...`",
                "- Run `python -m ciept.audit.audit_cli build ...`",
                "- Run experiment dispatch through `ciept.experiments.runner.run_experiment(...)`",
                "",
                "## Deferred External Assets",
                "- Real datasets not downloaded",
                "- Real VLM not connected",
                "- External baselines not integrated",
            ]
        ),
        encoding="utf-8",
    )
    (output_dir / "entrypoints.md").write_text(
        "\n".join(
            [
                "# Entrypoints",
                "",
                "- Data: `python -m ciept.data.cli`",
                "- Stress protocol: `python -m ciept.data.stress_cli`",
                "- Audit protocol: `python -m ciept.audit.audit_cli build|export-vlm|merge-vlm|init-adjudication`",
                "- Train/eval: `python -m ciept.train.cli --mode train|eval`",
                "- Delivery: `python -m ciept.delivery.cli --output-dir deliverables/current`",
            ]
        ),
        encoding="utf-8",
    )
    (output_dir / "required_assets.md").write_text(build_required_assets(project_root), encoding="utf-8")
    (output_dir / "implementation_review.md").write_text(
        build_implementation_review(project_root),
        encoding="utf-8",
    )
