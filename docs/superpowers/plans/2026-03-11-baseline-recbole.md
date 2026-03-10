# Baseline Inventory And RecBole Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement baseline inventory and RecBole bootstrap support, and add a baseline task track into the persistent task system.

**Architecture:** Add a small `ciept.baselines` package with a registry and a RecBole adapter. Keep it read-only over downloaded baseline assets and focused on classification/config generation rather than actual baseline execution.

**Tech Stack:** Python 3.10, dataclasses, pathlib, yaml, pytest

---

## Chunk 1: Baseline Registry And RecBole Adapter

### Task 1: Add failing tests for baseline classification and RecBole config generation

**Files:**
- Create: `tests/test_baseline_registry.py`
- Create: `tests/test_recbole_adapter.py`
- Reference: `docs/superpowers/specs/2026-03-11-baseline-recbole-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.baselines.registry import build_baseline_inventory


def test_build_baseline_inventory_classifies_downloaded_and_missing_assets(tmp_path):
    ...
```

```python
from ciept.baselines.recbole_adapter import build_recbole_config


def test_build_recbole_config_uses_presplit_full_sort_defaults(tmp_path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_baseline_registry.py tests/test_recbole_adapter.py -v`
Expected: FAIL because the baselines package does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/baselines/__init__.py`
- `src/ciept/baselines/registry.py`
- `src/ciept/baselines/recbole_adapter.py`
- `configs/baselines/recbole_base.yaml`

Implementation requirements:

- classify direct matches, mapped candidates, and missing baselines
- record source paths and mapping notes
- expose RecBole availability checks
- build stable RecBole config dictionaries for presplit/full-sort evaluation

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_baseline_registry.py tests/test_recbole_adapter.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `B001` should be committed once after final verification.

## Chunk 2: Task-System Integration And Completion

### Task 2: Add failing tests for baseline task track and current baseline focus

**Files:**
- Modify: `tests/test_persistence.py`
- Modify: `README.md`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Reference: `docs/superpowers/specs/2026-03-11-baseline-recbole-design.md`

- [ ] **Step 1: Write the failing test**

```python
def test_b001_baseline_inventory_task_marked_done():
    ...
```

```python
def test_current_focus_moves_to_b002():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_persistence.py::test_b001_baseline_inventory_task_marked_done tests/test_persistence.py::test_current_focus_moves_to_b002 -v`
Expected: FAIL because baseline tasks are not yet registered.

- [ ] **Step 3: Write minimal implementation**

Update:

- `continue/task.json` to add baseline task track `B001+`
- `continue/progress.md` with a baseline bootstrap entry
- `README.md` with baseline/RecBole integration notes

Implementation requirements:

- `B001` is marked `done`
- `current_focus` becomes `B002`
- later baseline tasks are queued but remain pending

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with the full repository test suite green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-11-baseline-recbole.md src/ciept/baselines/__init__.py src/ciept/baselines/registry.py src/ciept/baselines/recbole_adapter.py configs/baselines/recbole_base.yaml tests/test_baseline_registry.py tests/test_recbole_adapter.py tests/test_persistence.py
git commit -m "feat: add baseline inventory and recbole bootstrap"
```
