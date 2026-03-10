# Research Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap the AAAI CIEPT-R repository into a runnable Python research skeleton with persistent agent state and one completed initialization task.

**Architecture:** Keep the first milestone narrow: a small `ciept` Python package, one YAML-backed config loader, one CLI entrypoint, one verification script, and a persistent `continue/` workflow. The repository should validate its own bootstrap without pretending the research pipeline already exists.

**Tech Stack:** Python 3.10, setuptools via `pyproject.toml`, PyYAML, pytest, argparse, bash

---

## Chunk 1: Repository Bootstrap And Persistent Workflow

### Task 1: Add repository metadata and persistent state files

**Files:**
- Create: `README.md`
- Create: `continue/AGENT.MD`
- Create: `continue/progress.md`
- Create: `continue/task.json`
- Modify: `.gitignore`
- Reference: `docs/superpowers/specs/2026-03-10-research-bootstrap-design.md`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import json


def test_continue_task_file_exists_and_has_bootstrap_task():
    task_file = Path("continue/task.json")
    assert task_file.exists()

    data = json.loads(task_file.read_text())
    assert data["project"] == "CIEPT-R"
    assert any(task["id"] == "T001" for task in data["tasks"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_persistence.py::test_continue_task_file_exists_and_has_bootstrap_task -v`
Expected: FAIL because `continue/task.json` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create the persistent workflow files with:

- `continue/AGENT.MD` describing the one-task-per-session workflow
- `continue/progress.md` with an initial bootstrap log template
- `continue/task.json` containing `T001` through `T005`
- `README.md` summarizing scope, structure, and bootstrap workflow

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_persistence.py::test_continue_task_file_exists_and_has_bootstrap_task -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T001` is one task and should be committed once after final verification.

## Chunk 2: Python Package, CLI, And Verification

### Task 2: Add failing tests for config loading and CLI execution

**Files:**
- Create: `tests/test_config.py`
- Create: `tests/test_cli.py`
- Reference: `docs/superpowers/specs/2026-03-10-research-bootstrap-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.config import load_config


def test_load_config_reads_project_name():
    config = load_config("configs/base.yaml")
    assert config["project"]["name"] == "CIEPT-R"
```

```python
import subprocess
import sys


def test_cli_prints_project_summary():
    result = subprocess.run(
        [sys.executable, "-m", "ciept.cli", "--config", "configs/base.yaml"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "CIEPT-R" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py tests/test_cli.py -v`
Expected: FAIL because the package and config loader do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `pyproject.toml` with package metadata and dev dependencies
- `configs/base.yaml` with project name, seed, and directory settings
- `src/ciept/__init__.py`
- `src/ciept/config.py`
- `src/ciept/cli.py`
- `scripts/check.sh`

Implementation details:

- `load_config(path)` reads YAML and returns a dictionary
- `python -m ciept.cli --config ...` prints a short bootstrap summary
- `scripts/check.sh` runs `python -m pytest`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T001` is one task and should be committed once after final verification.

### Task 3: Finalize bootstrap status and verification

**Files:**
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Reference: `docs/superpowers/specs/2026-03-10-research-bootstrap-design.md`
- Reference: `docs/superpowers/plans/2026-03-10-research-bootstrap.md`

- [ ] **Step 1: Write the failing test**

```python
import json
from pathlib import Path


def test_bootstrap_task_marked_done_after_verification():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T001")
    assert task["status"] == "done"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_persistence.py::test_bootstrap_task_marked_done_after_verification -v`
Expected: FAIL because `T001` should still be pending before implementation is verified.

- [ ] **Step 3: Write minimal implementation**

After successful verification:

- update `continue/task.json` so `T001` becomes `done`
- set `current_focus` to `T002`
- append a timestamped entry to `continue/progress.md`

- [ ] **Step 4: Run test to verify it passes**

Run: `bash scripts/check.sh`
Expected: PASS with all bootstrap tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md pyproject.toml configs/base.yaml src/ciept/__init__.py src/ciept/config.py src/ciept/cli.py scripts/check.sh tests/test_persistence.py tests/test_config.py tests/test_cli.py continue/AGENT.MD continue/progress.md continue/task.json docs/superpowers/plans/2026-03-10-research-bootstrap.md
git commit -m "feat: complete bootstrap task T001"
```
