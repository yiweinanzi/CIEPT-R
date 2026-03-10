# Training Entrypoint Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T008` by adding a minimal but real train/eval loop that connects reranking, intervention loss, and confidence-weighted ListMLE on toy batches.

**Architecture:** Add focused training and evaluation modules instead of a large trainer framework. Keep the code executable end-to-end with toy tensors, but narrow enough that it remains a bridge to later experiment infrastructure rather than an overbuilt training system.

**Tech Stack:** Python 3.10, PyTorch, dataclasses, pytest

---

## Chunk 1: Ranking Loss And Train/Eval Engine

### Task 1: Add failing tests for ranking loss, train step, and eval step

**Files:**
- Create: `tests/test_train_losses.py`
- Create: `tests/test_train_engine.py`
- Reference: `docs/superpowers/specs/2026-03-10-training-entrypoint-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.train.losses import confidence_weighted_listmle


def test_confidence_weighted_listmle_prefers_high_positive_score():
    ...
```

```python
from ciept.train.engine import train_step, eval_step


def test_train_step_returns_losses_and_allows_backward():
    ...
```

```python
def test_eval_step_returns_recall_and_mrr():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_train_losses.py tests/test_train_engine.py -v`
Expected: FAIL because training modules do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/train/__init__.py`
- `src/ciept/train/losses.py`
- `src/ciept/train/engine.py`
- `src/ciept/eval/__init__.py`
- `src/ciept/eval/metrics.py`

Implementation requirements:

- implement `confidence_weighted_listmle()`
- implement a toy batch generator or inline toy batch helpers
- `train_step()` runs positive and negative reranker passes, intervention loss, and one backward pass
- `eval_step()` returns toy `Recall@1` and `MRR`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_train_losses.py tests/test_train_engine.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T008` should be committed once after final verification.

## Chunk 2: CLI, State, And Completion

### Task 2: Add failing tests for train/eval CLI and task-completion state

**Files:**
- Create: `tests/test_train_cli.py`
- Modify: `tests/test_persistence.py`
- Modify: `README.md`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Reference: `docs/superpowers/specs/2026-03-10-training-entrypoint-design.md`

- [ ] **Step 1: Write the failing test**

```python
def test_train_cli_runs_train_mode():
    ...
```

```python
def test_train_cli_runs_eval_mode():
    ...
```

```python
def test_t008_marked_done_and_t009_selected_next():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_train_cli.py tests/test_persistence.py::test_t008_marked_done_and_t009_selected_next -v`
Expected: FAIL because CLI and the completed `T008` state do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/train/cli.py`

Update:

- `README.md` with train/eval entrypoint notes
- `continue/task.json` to mark `T008` done and `T009` current
- `continue/progress.md` with a verification-backed `T008` entry

Implementation requirements:

- `--mode train` runs one toy train step and prints loss summary
- `--mode eval` runs one toy eval step and prints metrics summary
- invalid modes fail cleanly

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-training-entrypoint.md src/ciept/train/__init__.py src/ciept/train/losses.py src/ciept/train/engine.py src/ciept/train/cli.py src/ciept/eval/__init__.py src/ciept/eval/metrics.py tests/test_train_losses.py tests/test_train_engine.py tests/test_train_cli.py tests/test_persistence.py
git commit -m "feat: complete training entrypoint task T008"
```
