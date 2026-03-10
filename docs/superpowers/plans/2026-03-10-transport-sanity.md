# Transport Sanity Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T005` by adding a NumPy-based miniature partial-transport solver and deterministic sanity checks for mass budget, capacity priors, and reject semantics.

**Architecture:** Add a small `ciept.transport` package with typed transport problems, a partial-projection mini-solver, and semantic validation helpers. Keep the implementation explicitly toy-scale and numerically robust, but structurally close to later transport code.

**Tech Stack:** Python 3.10, NumPy, dataclasses, pytest

---

## Chunk 1: Transport Solver And Core Constraints

### Task 1: Add failing tests for solver constraints and budget behavior

**Files:**
- Create: `tests/test_transport_solver.py`
- Reference: `docs/superpowers/specs/2026-03-10-transport-sanity-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.transport.toy_solver import solve_partial_transport
from ciept.transport.types import TransportProblem


def test_solver_respects_mass_budget_and_constraints():
    ...
```

```python
def test_solver_rejects_invalid_problem_shapes():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_transport_solver.py -v`
Expected: FAIL because `ciept.transport` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/transport/__init__.py`
- `src/ciept/transport/types.py`
- `src/ciept/transport/toy_solver.py`

Implementation requirements:

- `TransportProblem` and `TransportResult` are dataclasses
- solver validates shape, sign, and scalar constraints
- solver uses NumPy kernel initialization plus iterative row/column/total-mass projections
- result exposes plan, transported mass, rejected mass, source leftovers, target usage, and slack

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_transport_solver.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T005` should be committed once after final verification.

## Chunk 2: Semantic Sanity Checks And Task Completion

### Task 2: Add failing tests for toy semantics and persistent task state

**Files:**
- Create: `tests/test_transport_sanity.py`
- Modify: `tests/test_persistence.py`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Modify: `README.md`
- Reference: `docs/superpowers/specs/2026-03-10-transport-sanity-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.transport.sanity import check_reject_semantics


def test_target_capacity_binding_saturates_small_capacity_target():
    ...
```

```python
def test_reject_over_bad_match_prefers_low_cost_alignment():
    ...
```

```python
def test_t005_marked_done_and_t006_selected_next():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_transport_sanity.py tests/test_persistence.py::test_t005_marked_done_and_t006_selected_next -v`
Expected: FAIL because sanity helpers and the completed `T005` state do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/transport/sanity.py`

Update:

- `README.md` with transport sanity-layer notes
- `continue/task.json` to mark `T005` done and `T006` current
- `continue/progress.md` with a verification-backed `T005` entry

Implementation requirements:

- semantic helpers expose readable checks over solver outputs
- toy cases show budget binding, capacity binding, and reject-over-bad-match behavior
- README stays minimal and does not oversell the toy solver as production transport

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-transport-sanity.md src/ciept/transport/__init__.py src/ciept/transport/types.py src/ciept/transport/toy_solver.py src/ciept/transport/sanity.py tests/test_transport_solver.py tests/test_transport_sanity.py tests/test_persistence.py
git commit -m "feat: complete transport sanity task T005"
```
