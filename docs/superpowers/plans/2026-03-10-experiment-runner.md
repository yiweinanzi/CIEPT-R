# Experiment Runner Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T012` by adding a dispatcher-based experiment runner that writes stable result directories with `metrics.json` and `summary.md` for each experiment family.

**Architecture:** Add a lightweight `ciept.experiments` package with shared result types, shared I/O helpers, a central dispatcher, and per-experiment toy modules. Each experiment writes the same output structure so future real benchmark runs can reuse the protocol without changing downstream consumers.

**Tech Stack:** Python 3.10, dataclasses, json, pathlib, pytest

---

## Chunk 1: Dispatcher And Core Result I/O

### Task 1: Add failing tests for run directory creation and experiment dispatch

**Files:**
- Create: `tests/test_experiment_runner.py`
- Reference: `docs/superpowers/specs/2026-03-10-experiment-runner-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.experiments.runner import run_experiment


def test_run_experiment_writes_metrics_and_summary(tmp_path):
    ...
```

```python
def test_unknown_experiment_name_raises():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_experiment_runner.py -v`
Expected: FAIL because the experiments package does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/experiments/__init__.py`
- `src/ciept/experiments/types.py`
- `src/ciept/experiments/io.py`
- `src/ciept/experiments/runner.py`

Implementation requirements:

- define result dataclasses
- create unique run directories
- write `metrics.json`
- write `summary.md`
- dispatch named experiments

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_experiment_runner.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T012` should be committed once after final verification.

## Chunk 2: Experiment Modules, State, And Completion

### Task 2: Add failing tests for experiment outputs and task-completion state

**Files:**
- Create: `tests/test_experiment_modules.py`
- Modify: `tests/test_persistence.py`
- Modify: `README.md`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Reference: `docs/superpowers/specs/2026-03-10-experiment-runner-design.md`

- [ ] **Step 1: Write the failing test**

```python
def test_main_results_experiment_emits_required_metrics():
    ...
```

```python
def test_usage_experiment_emits_required_metrics():
    ...
```

```python
def test_t012_marked_done_and_t013_selected_next():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_experiment_modules.py tests/test_persistence.py::test_t012_marked_done_and_t013_selected_next -v`
Expected: FAIL because experiment modules and the completed `T012` state do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/experiments/main_results.py`
- `src/ciept/experiments/robustness.py`
- `src/ciept/experiments/faithfulness.py`
- `src/ciept/experiments/ablation.py`
- `src/ciept/experiments/usage.py`
- `src/ciept/experiments/efficiency.py`

Update:

- `README.md` with experiment-runner notes
- `continue/task.json` to mark `T012` done and `T013` current
- `continue/progress.md` with a verification-backed `T012` entry

Implementation requirements:

- each experiment returns toy metrics with the expected keys
- summaries clearly state that results are toy/placeholder
- dispatcher uses the shared I/O layer for every experiment

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-experiment-runner.md src/ciept/experiments/__init__.py src/ciept/experiments/types.py src/ciept/experiments/io.py src/ciept/experiments/runner.py src/ciept/experiments/main_results.py src/ciept/experiments/robustness.py src/ciept/experiments/faithfulness.py src/ciept/experiments/ablation.py src/ciept/experiments/usage.py src/ciept/experiments/efficiency.py tests/test_experiment_runner.py tests/test_experiment_modules.py tests/test_persistence.py
git commit -m "feat: complete experiment runner task T012"
```
