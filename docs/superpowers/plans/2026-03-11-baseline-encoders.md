# Remaining Baselines And Local Encoder/OCR Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the remaining locally available baselines and add local Qwen/PaddleOCR adapters without coupling heavy runtime code into the core research stack.

**Architecture:** Extend the existing baseline family adapters for `Guider`, `MAGNET`, `SMORE`, and `DiffMM`, record `MixRec` as a truthful incompatibility, and add a new `ciept.encoders` package with lazy local-model wrappers for Qwen text/VL embeddings and PaddleOCR.

**Tech Stack:** Python 3.10, pathlib, json, pickle, numpy, pytest, transformers, sentence-transformers, paddleocr

---

## Chunk 1: Remaining Baseline Registry And Runner Support

### Task 1: Add failing tests for post-`B011` baseline statuses and runner coverage

**Files:**
- Modify: `tests/test_baseline_registry.py`
- Modify: `tests/test_baseline_runner.py`
- Reference: `docs/superpowers/specs/2026-03-11-baseline-encoders-design.md`

- [ ] **Step 1: Write the failing test**

Add assertions for:

- `Guider`, `MAGNET`, `SMORE`, `DiffMM` being executable baseline entries
- `MixRec` being classified as a truthful incompatibility

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_baseline_registry.py tests/test_baseline_runner.py -v`
Expected: FAIL because these baselines are not yet modeled correctly.

- [ ] **Step 3: Write minimal implementation**

Extend the registry and runner to support the new baseline families/statuses.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_baseline_registry.py tests/test_baseline_runner.py -v`
Expected: PASS

## Chunk 2: New Baseline Dataset Formatters

### Task 2: Add failing tests for DiffMM formatting and MMRec-family reuse

**Files:**
- Modify: `tests/test_baseline_formats.py`
- Modify: `src/ciept/baselines/formats.py`

- [ ] **Step 1: Write the failing test**

Add tests that:

- prepare `DiffMM` pickled train/test matrices plus features
- verify MMRec-family preparation also covers `Guider`, `MAGNET`, and `SMORE`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_baseline_formats.py -v`
Expected: FAIL because DiffMM formatting does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Add a DiffMM formatter and any metadata required for the new runners.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_baseline_formats.py -v`
Expected: PASS

## Chunk 3: Local Encoder/OCR Package

### Task 3: Add failing tests for local Qwen and PaddleOCR adapters

**Files:**
- Create: `src/ciept/encoders/__init__.py`
- Create: `src/ciept/encoders/registry.py`
- Create: `src/ciept/encoders/text.py`
- Create: `src/ciept/encoders/vision.py`
- Create: `src/ciept/encoders/ocr.py`
- Create: `tests/test_local_encoders.py`
- Create: `configs/models/local_backends.yaml`

- [ ] **Step 1: Write the failing test**

Add tests that:

- validate local model paths
- verify lazy backend construction for text/VL/OCR adapters
- verify calls are routed to mocked `SentenceTransformer`, `transformers`, and `PaddleOCR` backends

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_local_encoders.py -v`
Expected: FAIL because the package does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Implement lazy local-model adapters and config loading.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_local_encoders.py -v`
Expected: PASS

## Chunk 4: Task-State And Documentation Updates

### Task 4: Add failing tests for new task-state transitions

**Files:**
- Modify: `tests/test_persistence.py`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Modify: `README.md`
- Modify: `deliverables/current/required_assets.md`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing test**

Add assertions that:

- new baseline tasks and model/OCR tasks are recorded
- executable remaining baselines are `done`
- `MixRec` and multimodal `CLEAR` remain blocked when appropriate

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_persistence.py -v`
Expected: FAIL because task state has not been extended yet.

- [ ] **Step 3: Write minimal implementation**

Update persistent state, docs, and dependency metadata.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS
