from __future__ import annotations

import json
import subprocess
from pathlib import Path


def get_git_commit(project_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def build_results_index(project_root: Path) -> list[dict]:
    results_root = project_root / "results"
    if not results_root.exists():
        return []

    entries: list[dict] = []
    for metrics_path in sorted(results_root.glob("*/*/metrics.json")):
        run_dir = metrics_path.parent
        entries.append(
            {
                "experiment_name": run_dir.parent.name,
                "run_id": run_dir.name,
                "metrics_json": str(metrics_path),
                "summary_md": str(run_dir / "summary.md"),
            }
        )
    return entries


def build_task_snapshot(project_root: Path) -> dict:
    task_path = project_root / "continue" / "task.json"
    if not task_path.exists():
        raise ValueError("continue/task.json is required")
    return json.loads(task_path.read_text(encoding="utf-8"))


def build_manifest(project_root: Path) -> dict:
    task_snapshot = build_task_snapshot(project_root)
    return {
        "git_commit": get_git_commit(project_root),
        "current_focus": task_snapshot["current_focus"],
        "completed_tasks": [task["id"] for task in task_snapshot["tasks"] if task["status"] == "done"],
        "entrypoints": {
            "data_cli": "python -m ciept.data.cli",
            "train_cli": "python -m ciept.train.cli",
            "audit_cli": "python -m ciept.audit.audit_cli",
        },
        "environment": {
            "python": "3.10",
            "torch_expected": True,
        },
    }
