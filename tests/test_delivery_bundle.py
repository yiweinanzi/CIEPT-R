from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.delivery.export import build_delivery_bundle


def test_build_delivery_bundle_writes_manifest_results_and_snapshot(tmp_path):
    output_dir = tmp_path / "bundle"

    build_delivery_bundle(
        project_root=Path(__file__).resolve().parents[1],
        output_dir=output_dir,
    )

    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "results_index.json").exists()
    assert (output_dir / "task_snapshot.json").exists()

    manifest = json.loads((output_dir / "manifest.json").read_text())
    assert "git_commit" in manifest
