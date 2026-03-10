# Audit Dataset Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T010` by adding an audit-dataset pipeline that exports audit examples, VLM request payloads, merges VLM predictions, and initializes adjudication queues.

**Architecture:** Extend `ciept.audit` with protocol-focused modules for audit-example generation, file-based VLM I/O, and adjudication initialization. Keep the implementation provider-agnostic and JSONL-driven so it can support later VLM and human workflows without rework.

**Tech Stack:** Python 3.10, dataclasses, json, pathlib, pytest

---

## Chunk 1: Audit Dataset And VLM Request Export

### Task 1: Add failing tests for audit-example generation and VLM request export

**Files:**
- Create: `tests/test_audit_dataset.py`
- Reference: `docs/superpowers/specs/2026-03-10-audit-dataset-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.audit.audit_dataset import build_audit_dataset


def test_build_audit_dataset_writes_examples_and_manifest():
    ...
```

```python
from ciept.audit.vlm_io import export_vlm_requests


def test_export_vlm_requests_writes_request_records():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_audit_dataset.py -v`
Expected: FAIL because audit-dataset protocol modules do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/audit/audit_types.py`
- `src/ciept/audit/audit_dataset.py`
- `src/ciept/audit/vlm_io.py`

Implementation requirements:

- audit examples are built from stress artifacts with stable `audit_id`
- manifest records dataset counts
- VLM request export is JSONL and provider-agnostic

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_audit_dataset.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T010` should be committed once after final verification.

## Chunk 2: Prediction Merge, Adjudication, And Completion

### Task 2: Add failing tests for VLM merge, adjudication queue, and task-completion state

**Files:**
- Create: `tests/test_audit_merge.py`
- Modify: `tests/test_persistence.py`
- Modify: `README.md`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Reference: `docs/superpowers/specs/2026-03-10-audit-dataset-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.audit.vlm_io import merge_vlm_predictions


def test_merge_vlm_predictions_writes_annotated_examples_and_updates_manifest():
    ...
```

```python
from ciept.audit.adjudication import init_adjudication_queue


def test_init_adjudication_queue_writes_pending_records():
    ...
```

```python
def test_t010_marked_done_and_t011_selected_next():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_audit_merge.py tests/test_persistence.py::test_t010_marked_done_and_t011_selected_next -v`
Expected: FAIL because merge/adjudication modules and the completed `T010` state do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/audit/adjudication.py`
- `src/ciept/audit/audit_cli.py`

Update:

- `README.md` with audit-set protocol notes
- `continue/task.json` to mark `T010` done and `T011` current
- `continue/progress.md` with a verification-backed `T010` entry

Implementation requirements:

- merge is keyed by `audit_id`
- original audit examples remain immutable
- adjudication queue is initialized from annotated audit examples
- CLI supports `build`, `merge-vlm`, and `init-adjudication`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-audit-dataset.md src/ciept/audit/audit_types.py src/ciept/audit/audit_dataset.py src/ciept/audit/vlm_io.py src/ciept/audit/adjudication.py src/ciept/audit/audit_cli.py tests/test_audit_dataset.py tests/test_audit_merge.py tests/test_persistence.py
git commit -m "feat: complete audit dataset task T010"
```
