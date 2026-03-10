# Conflict Stress Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T009` by adding an offline conflict-stress pipeline that generates positive-preserving nuisance and negative-preserving lure artifacts under `data/interim/`.

**Architecture:** Extend `ciept.data` with protocol types, perturbation rules, and an offline pipeline that reads JSONL examples, applies node-level perturbations at fixed strengths, and writes structured outputs plus review queues. Keep the implementation JSON-friendly and protocol-driven, not image-processing-heavy.

**Tech Stack:** Python 3.10, dataclasses, json, pathlib, pytest

---

## Chunk 1: Perturbation Rules And Schemas

### Task 1: Add failing tests for nuisance/lure rule behavior

**Files:**
- Create: `tests/test_conflict_stress_rules.py`
- Reference: `docs/superpowers/specs/2026-03-10-conflict-stress-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.data.stress_rules import apply_positive_preserving_nuisance, apply_negative_preserving_lure


def test_positive_nuisance_preserves_label_and_marks_changed_nodes():
    ...
```

```python
def test_negative_lure_preserves_label_and_adds_lure_nodes():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_conflict_stress_rules.py -v`
Expected: FAIL because stress-test modules do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/data/stress_types.py`
- `src/ciept/data/stress_rules.py`

Implementation requirements:

- define perturbation dataclasses
- implement fixed-strength perturbation selection
- preserve original labels
- emit node-level nuisance/lure masks and changed-field metadata

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_conflict_stress_rules.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T009` should be committed once after final verification.

## Chunk 2: Offline Pipeline, CLI, And Task Completion

### Task 2: Add failing tests for pipeline outputs, CLI execution, and task-completion state

**Files:**
- Create: `tests/test_conflict_stress_pipeline.py`
- Modify: `tests/test_persistence.py`
- Modify: `README.md`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Reference: `docs/superpowers/specs/2026-03-10-conflict-stress-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.data.stress_pipeline import generate_conflict_stress_dataset


def test_pipeline_writes_examples_masks_summary_and_review_queue():
    ...
```

```python
def test_strength_levels_change_number_of_perturbed_nodes():
    ...
```

```python
def test_t009_marked_done_and_t010_selected_next():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_conflict_stress_pipeline.py tests/test_persistence.py::test_t009_marked_done_and_t010_selected_next -v`
Expected: FAIL because pipeline/CLI and the completed `T009` state do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/data/stress_pipeline.py`
- `src/ciept/data/stress_cli.py`

Update:

- `README.md` with conflict-stress protocol notes
- `continue/task.json` to mark `T009` done and `T010` current
- `continue/progress.md` with a verification-backed `T009` entry

Implementation requirements:

- load JSONL examples
- write `examples.jsonl`, `nuisance_mask.json`, `protocol_summary.json`, and `review_queue.jsonl`
- support strengths `0.1`, `0.3`, and `0.5`
- allow overwrite while recording run metadata

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-conflict-stress.md src/ciept/data/stress_types.py src/ciept/data/stress_rules.py src/ciept/data/stress_pipeline.py src/ciept/data/stress_cli.py tests/test_conflict_stress_rules.py tests/test_conflict_stress_pipeline.py tests/test_persistence.py
git commit -m "feat: complete conflict stress task T009"
```
