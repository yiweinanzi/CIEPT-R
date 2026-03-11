# Baseline Integration Wave B003-B011 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the `B003-B011` baseline wave by adding family-based baseline adapters, confirmed mapping metadata, truthful missing-asset tracking, and persistent task updates.

**Architecture:** Build baseline integrations around shared adapter families rather than one-off wrappers. Extend the baseline registry to drive archive handling, dataset formatting, runner dispatch, mapping conclusions, and blocker tracking.

**Tech Stack:** Python 3.10, pathlib, csv, json, zipfile, dataclasses, numpy, pytest

---

## Chunk 1: Registry And Tracking Metadata

### Task 1: Make the registry rich enough for direct matches, confirmed mappings, and mismatches

**Files:**
- Modify: `src/ciept/baselines/registry.py`
- Modify: `tests/test_baseline_registry.py`
- Reference: `docs/superpowers/specs/2026-03-11-baseline-wave-design.md`

- [ ] **Step 1: Write the failing test**

Add assertions for:

- `Guider -> Teach Me How to Denoise`
- `MAGNET -> Modality-Guided Mixture of Graph Experts`
- `CLEAR` being classified as `asset_mismatch`
- `RecGOAT` and `IGDMRec` staying `missing`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_baseline_registry.py -v`
Expected: FAIL because the registry is not yet rich enough.

- [ ] **Step 3: Write minimal implementation**

Extend the registry metadata and inventory builder to emit mapping/tracking fields required for `B008-B011`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_baseline_registry.py -v`
Expected: PASS

## Chunk 2: Dataset Preparation Helpers

### Task 2: Add failing tests for MMRec, VBPR, and I3-MRec data preparation

**Files:**
- Create: `tests/test_baseline_formats.py`
- Create: `src/ciept/baselines/archive.py`
- Create: `src/ciept/baselines/formats.py`

- [ ] **Step 1: Write the failing test**

Add tests that:

- extract a tiny fake archive to a work directory
- convert presplit CSVs into MMRec `.inter` plus feature `.npy` files
- convert presplit CSVs into VBPR-ready numeric interactions and feature matrices
- convert presplit CSVs into I3-MRec `.inter` plus feature files

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_baseline_formats.py -v`
Expected: FAIL because the helpers do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Add archive extraction and dataset-format helpers with deterministic placeholder-feature fallbacks.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_baseline_formats.py -v`
Expected: PASS

## Chunk 3: Family-Based Runner Dispatch

### Task 3: Add failing tests for family-based baseline runner modes

**Files:**
- Modify: `src/ciept/baselines/runner.py`
- Modify: `src/ciept/baselines/__init__.py`
- Modify: `tests/test_baseline_runner.py`

- [ ] **Step 1: Write the failing test**

Add tests that:

- dispatch `LightGCN` through `recbole`
- dispatch `VBPR` through `vbpr_python`
- dispatch `BM3` through `mmrec`
- dispatch `I3-MRec` through `i3mrec`
- dispatch `Training-free Graph-based Imputation` through `graph_imputation`
- reject `CLEAR` with an `asset_mismatch` error

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_baseline_runner.py -v`
Expected: FAIL because the runner only supports `recbole` today.

- [ ] **Step 3: Write minimal implementation**

Expand the runner to prepare family-specific datasets, write standardized outputs, and allow injected executors per integration mode.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_baseline_runner.py -v`
Expected: PASS

## Chunk 4: Persistence And Asset Tracking

### Task 4: Add failing tests for `B003-B011` task states and required-assets tracking

**Files:**
- Modify: `tests/test_persistence.py`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Modify: `deliverables/current/required_assets.md`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Add assertions that:

- `B003-B007`, `B009`, `B010`, and `B011` are `done`
- `B008` is `blocked`
- `current_focus` points at the blocked `B008`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_persistence.py -v`
Expected: FAIL because task states and asset tracking have not been updated yet.

- [ ] **Step 3: Write minimal implementation**

Update task metadata, progress entries, and required-assets tracking after the implementation and verification evidence exist.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS
