# Data Protocol And Temporal Split Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T002` by defining the repository data layout and adding a reproducible preprocessing path for iterative k-core filtering, global temporal splitting, and missing-modality reporting.

**Architecture:** Keep `T002` focused on protocol, not full preprocessing breadth. Add a small `ciept.data` package with pure-Python CSV utilities, a deterministic split pipeline, and one CLI entrypoint that writes train/valid/test files plus a summary report. Represent missing modalities explicitly in item metadata instead of silently dropping items.

**Tech Stack:** Python 3.10, csv, json, argparse, pathlib, pytest

---

## Chunk 1: Data Layout And Protocol Tests

### Task 1: Add failing tests for data protocol behavior

**Files:**
- Create: `tests/test_data_protocol.py`
- Create: `tests/test_data_cli.py`
- Reference: `aaai项目.md`
- Reference: `continue/task.json`

- [ ] **Step 1: Write the failing test**

```python
from ciept.data.protocol import global_temporal_split, iterative_k_core


def test_iterative_k_core_filters_until_all_nodes_meet_threshold():
    interactions = [
        {"user_id": "u1", "item_id": "i1", "timestamp": 1},
        {"user_id": "u1", "item_id": "i2", "timestamp": 2},
        {"user_id": "u2", "item_id": "i1", "timestamp": 3},
        {"user_id": "u2", "item_id": "i2", "timestamp": 4},
        {"user_id": "u3", "item_id": "i1", "timestamp": 5},
    ]
    filtered = iterative_k_core(interactions, min_user_degree=2, min_item_degree=2)
    assert len(filtered) == 4
```

```python
def test_global_temporal_split_uses_absolute_time_order():
    interactions = [{"timestamp": ts} for ts in [9, 1, 7, 3, 5, 11, 13, 15, 17, 19]]
    train, valid, test = global_temporal_split(interactions)
    assert [row["timestamp"] for row in train] == [1, 3, 5, 7, 9, 11, 13, 15]
    assert [row["timestamp"] for row in valid] == [17]
    assert [row["timestamp"] for row in test] == [19]
```

```python
def test_cli_writes_split_files_and_missing_modality_report(tmp_path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_data_protocol.py tests/test_data_cli.py -v`
Expected: FAIL because `ciept.data` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/data/__init__.py`
- `src/ciept/data/protocol.py`
- `src/ciept/data/cli.py`
- `data/README.md`
- placeholder directories under `data/raw/`, `data/interim/`, `data/processed/`

Implementation requirements:

- `iterative_k_core()` removes low-degree users/items until stable
- `global_temporal_split()` sorts by absolute timestamp and slices 80/10/10
- missing modalities are reported from explicit `has_text` / `has_image` / `has_ocr` flags
- CLI writes `train.csv`, `valid.csv`, `test.csv`, and `protocol_summary.json`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_data_protocol.py tests/test_data_cli.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T002` should be committed once after final verification.

## Chunk 2: Documentation, State, And Verification

### Task 2: Update repository documentation and persistent task state

**Files:**
- Modify: `README.md`
- Modify: `configs/base.yaml`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Modify: `scripts/check.sh`

- [ ] **Step 1: Write the failing test**

```python
import json
from pathlib import Path


def test_t002_marked_done_and_t003_selected_next():
    data = json.loads(Path("continue/task.json").read_text())
    task = next(task for task in data["tasks"] if task["id"] == "T002")
    assert task["status"] == "done"
    assert data["current_focus"] == "T003"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_persistence.py::test_t002_marked_done_and_t003_selected_next -v`
Expected: FAIL because `T002` starts as `pending`.

- [ ] **Step 3: Write minimal implementation**

- update `README.md` with data protocol guidance
- extend `configs/base.yaml` with data paths and dataset defaults
- mark `T002` as `done` and `T003` as current focus in `continue/task.json`
- append a verification-backed `T002` entry to `continue/progress.md`
- ensure `scripts/check.sh` still runs the complete test suite

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md configs/base.yaml data continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-data-protocol-temporal-split.md scripts/check.sh src/ciept/data tests/test_data_protocol.py tests/test_data_cli.py tests/test_persistence.py
git commit -m "feat: complete data protocol task T002"
```
