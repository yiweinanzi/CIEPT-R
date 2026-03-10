from pathlib import Path
import os
import subprocess
import sys


def test_cli_prints_project_summary():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

    result = subprocess.run(
        [sys.executable, "-m", "ciept.cli", "--config", "configs/base.yaml"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "CIEPT-R" in result.stdout
