# Intervention Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T007` by adding normalized support, straight-through binary gating, leakage-ratio diagnostics, and a single-pass intervention loss.

**Architecture:** Add a focused `ciept.audit` package with small, testable units: support normalization, gate construction, and intervention losses. Keep the module independent from the training loop so later tasks can reuse it without dragging in optimization orchestration.

**Tech Stack:** Python 3.10, PyTorch, dataclasses, pytest

---

## Chunk 1: Support Normalization And Gating

### Task 1: Add failing tests for normalized support, logits, and gate behavior

**Files:**
- Create: `tests/test_audit_support.py`
- Create: `tests/test_audit_gating.py`
- Reference: `docs/superpowers/specs/2026-03-10-intervention-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.audit.support import normalized_support, support_to_logits


def test_normalized_support_uses_capacity_prior():
    ...
```

```python
from ciept.audit.gating import binary_gumbel_ste


def test_binary_gumbel_ste_stays_in_unit_interval():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_audit_support.py tests/test_audit_gating.py -v`
Expected: FAIL because `ciept.audit` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/audit/__init__.py`
- `src/ciept/audit/types.py`
- `src/ciept/audit/support.py`
- `src/ciept/audit/gating.py`

Implementation requirements:

- support is computed from item-side transport mass
- support is normalized by `q_cap` before any logit transform
- logits are finite through clamping
- binary Gumbel/STE gate returns values in `[0, 1]`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_audit_support.py tests/test_audit_gating.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T007` should be committed once after final verification.

## Chunk 2: Intervention Loss, State, And Completion

### Task 2: Add failing tests for leakage ratio, intervention outputs, and task-completion state

**Files:**
- Create: `tests/test_audit_losses.py`
- Modify: `tests/test_persistence.py`
- Modify: `README.md`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Reference: `docs/superpowers/specs/2026-03-10-intervention-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.audit.losses import leakage_ratio, single_pass_intervention


def test_leakage_ratio_uses_relative_support():
    ...
```

```python
def test_nuisance_case_produces_higher_leakage_loss_than_clean_case():
    ...
```

```python
def test_t007_marked_done_and_t008_selected_next():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_audit_losses.py tests/test_persistence.py::test_t007_marked_done_and_t008_selected_next -v`
Expected: FAIL because intervention losses and the completed `T007` state do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/audit/losses.py`

Update:

- `README.md` with intervention-layer notes
- `continue/task.json` to mark `T007` done and `T008` current
- `continue/progress.md` with a verification-backed `T007` entry

Implementation requirements:

- leakage stays ratio-based
- lightweight scorer is differentiable and independent from the reranker module
- `single_pass_intervention()` returns gate, scores, and component losses

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-intervention.md src/ciept/audit/__init__.py src/ciept/audit/types.py src/ciept/audit/support.py src/ciept/audit/gating.py src/ciept/audit/losses.py tests/test_audit_support.py tests/test_audit_gating.py tests/test_audit_losses.py tests/test_persistence.py
git commit -m "feat: complete intervention task T007"
```
