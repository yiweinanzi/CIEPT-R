# RecBole Data Bridge And Unified Baseline Runner Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `B002` by bridging presplit datasets into RecBole benchmark files and adding a unified baseline runner.

**Architecture:** Add baseline-scoped bridge and runner modules under `src/ciept/baselines/`. The bridge reformats offline split CSVs into RecBole atomic files, and the runner dispatches using baseline registry metadata while keeping RecBole isolated from the core research stack.

**Tech Stack:** Python 3.10, pathlib, csv, json, dataclasses, PyYAML, pytest

---

## Chunk 1: Presplit Dataset Bridge

### Task 1: Add failing tests for the RecBole benchmark bridge

**Files:**
- Create: `tests/test_baseline_bridge.py`
- Reference: `docs/superpowers/specs/2026-03-11-baseline-runner-design.md`

- [ ] **Step 1: Write the failing test**

Add tests that:

- create `train.csv`, `valid.csv`, `test.csv`, and `items.csv`
- call the bridge
- assert benchmark files and manifest are written with atomic headers

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_baseline_bridge.py -v`
Expected: FAIL because the bridge module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/baselines/data_bridge.py`

Implementation requirements:

- validate required split files and columns
- emit `train/valid/test` benchmark `.inter` files
- emit optional `.item`
- write a bridge manifest describing source and output paths

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_baseline_bridge.py -v`
Expected: PASS

## Chunk 2: Unified Baseline Runner

### Task 2: Add failing tests for runner dispatch and standardized outputs

**Files:**
- Create: `tests/test_baseline_runner.py`
- Modify: `src/ciept/baselines/__init__.py`
- Modify: `src/ciept/baselines/recbole_adapter.py`
- Reference: `docs/superpowers/specs/2026-03-11-baseline-runner-design.md`

- [ ] **Step 1: Write the failing test**

Add tests that:

- inject a fake RecBole executor into the unified runner
- assert `results/baselines/<baseline>/<run_id>/metrics.json` and `summary.md` are written
- assert non-recbole baselines fail with a clear `NotImplementedError`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_baseline_runner.py -v`
Expected: FAIL because the runner module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/baselines/runner.py`

Update:

- `src/ciept/baselines/recbole_adapter.py`
- `src/ciept/baselines/__init__.py`

Implementation requirements:

- add a recbole benchmark config helper
- define request/result contracts
- dispatch on registry integration mode
- write standardized baseline outputs

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_baseline_bridge.py tests/test_baseline_runner.py -v`
Expected: PASS

## Chunk 3: Task-State Update And Verification

### Task 3: Update persistent state for `B002`

**Files:**
- Modify: `continue/task.json`
- Modify: `continue/progress.md`

- [ ] **Step 1: Write the failing test**

Extend persistence coverage to assert that `B002` is marked done and `B003` becomes the next focus once implementation is verified.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_persistence.py::test_b002_recbole_bridge_task_marked_done -v`
Expected: FAIL because task state has not been updated yet.

- [ ] **Step 3: Write minimal implementation**

Update task state and progress log after fresh verification only.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS
