# Delivery Bundle Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T013` by generating a reproducible delivery bundle, a required-assets inventory, an implementation review against `aaai项目.md`, and by eliminating the local graph-adapter placeholder.

**Architecture:** Add a dedicated `ciept.delivery` package for manifest/export/review generation, write artifacts into `deliverables/current/`, and finalize the local graph tensor adapter so the repository has one fewer non-external placeholder. Keep external-resource-dependent areas explicitly marked as deferred in the review output instead of pretending they are complete.

**Tech Stack:** Python 3.10, dataclasses, json, pathlib, pytest, torch

---

## Chunk 1: Delivery Bundle Core And Graph Adapter

### Task 1: Add failing tests for tensor views and delivery bundle export

**Files:**
- Create: `tests/test_graph_adapters.py`
- Create: `tests/test_delivery_bundle.py`
- Reference: `docs/superpowers/specs/2026-03-10-delivery-bundle-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.graph.adapters import to_tensor_views


def test_to_tensor_views_exports_node_and_topology_tensors():
    ...
```

```python
from ciept.delivery.export import build_delivery_bundle


def test_build_delivery_bundle_writes_manifest_results_and_snapshot(tmp_path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_adapters.py tests/test_delivery_bundle.py -v`
Expected: FAIL because delivery modules do not exist yet and `graph.adapters` still raises `NotImplementedError`.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/delivery/__init__.py`
- `src/ciept/delivery/manifest.py`
- `src/ciept/delivery/export.py`

Modify:

- `src/ciept/graph/adapters.py`

Implementation requirements:

- `to_tensor_views()` exports graph node ids, modality ids, topology, and masks as tensors or tensor-friendly views
- delivery export writes:
  - `manifest.json`
  - `results_index.json`
  - `task_snapshot.json`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_graph_adapters.py tests/test_delivery_bundle.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T013` should be committed once after final verification.

## Chunk 2: Resource Inventory, Review, CLI, And Completion

### Task 2: Add failing tests for resource inventory, implementation review, CLI, and task-completion state

**Files:**
- Create: `tests/test_delivery_review.py`
- Modify: `tests/test_persistence.py`
- Modify: `README.md`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Reference: `docs/superpowers/specs/2026-03-10-delivery-bundle-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.delivery.review import build_required_assets, build_implementation_review


def test_required_assets_lists_datasets_models_and_baselines():
    ...
```

```python
def test_implementation_review_references_project_sections():
    ...
```

```python
def test_t013_marked_done_after_delivery_bundle_generation():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_delivery_review.py tests/test_persistence.py::test_t013_marked_done_after_delivery_bundle_generation -v`
Expected: FAIL because review/CLI/state updates do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/delivery/review.py`
- `src/ciept/delivery/cli.py`

Update:

- `README.md` with delivery-bundle notes
- `continue/task.json` to mark `T013` done
- `continue/progress.md` with a verification-backed `T013` entry

Implementation requirements:

- delivery CLI writes:
  - `manifest.json`
  - `results_index.json`
  - `task_snapshot.json`
  - `reproducibility_checklist.md`
  - `entrypoints.md`
  - `required_assets.md`
  - `implementation_review.md`
- required-assets output lists datasets, models, and baseline methods
- implementation review references major sections from `aaai项目.md`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-delivery-bundle.md src/ciept/graph/adapters.py src/ciept/delivery/__init__.py src/ciept/delivery/manifest.py src/ciept/delivery/review.py src/ciept/delivery/export.py src/ciept/delivery/cli.py tests/test_graph_adapters.py tests/test_delivery_bundle.py tests/test_delivery_review.py tests/test_persistence.py deliverables/current
git commit -m "feat: complete delivery bundle task T013"
```
