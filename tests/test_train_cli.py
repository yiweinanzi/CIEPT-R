from pathlib import Path
import os
import subprocess
import sys


def run_cli(mode: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    return subprocess.run(
        [sys.executable, "-m", "ciept.train.cli", "--mode", mode],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_train_cli_runs_train_mode():
    result = run_cli("train")

    assert result.returncode == 0
    assert "total_loss" in result.stdout


def test_train_cli_runs_eval_mode():
    result = run_cli("eval")

    assert result.returncode == 0
    assert "recall_at_1" in result.stdout
