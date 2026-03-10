# Toy Partial Transport Sanity Check Design

## Context

`T004` added heuristic reliability priors, capacity priors, and nuisance masks. The next step is to verify that the repository can express the intended partial-transport semantics before building a larger reranker or training loop.

`T005` is intentionally a toy numerical task. Its purpose is to prove three core ideas on small hand-crafted examples:

- transported mass is capped by an explicit mass budget
- target-side uptake is capped by the capacity prior
- leftover source mass has explicit reject semantics

This task should be numerically meaningful without pretending to be the final solver.

## Goal

Create a `ciept.transport` package that runs a NumPy-based miniature partial-transport solver and validates the repository’s core transport semantics on deterministic toy problems.

## Scope

### In scope

- a small transport problem dataclass
- a NumPy-based partial-transport mini-solver
- a transport result dataclass
- sanity-check helpers for transport semantics
- tests for mass-budget binding, capacity binding, and reject semantics

### Out of scope

- Gromov regularization
- batching
- gradients or backpropagation
- learned feature costs
- production-scale transport optimization

## Design Decisions

### 1. NumPy instead of pure Python lists

The solver should use NumPy arrays to express matrix operations clearly and keep the numerical logic close to what later tensor-backed implementations will look like.

### 2. Partial projection structure, not a greedy matcher

The solver should not be a simple low-cost greedy assignment. It should look like a small entropic partial-transport routine:

1. transform cost into a kernel
2. initialize a dense plan
3. alternate row, column, and total-mass projections
4. stop after convergence or iteration cap

This keeps the toy solver conceptually aligned with the later full transport module.

### 3. Reject semantics are explicit, not accidental

`rejected_mass` should be a first-class output:

`rejected_mass = sum(source_mass) - transported_mass`

The code should treat this as meaningful leftover mass, not as an optimization failure.

### 4. Capacity priors are enforced as hard uptake limits

`q_cap` should act as a column-wise upper bound on target absorption. Even when a node has the best cost, it should not receive more than its capacity.

### 5. Toy cases should prove semantics, not optimality theory

Tests are there to show that the implementation respects the intended semantics on clear examples. They do not need to prove formal optimality or match a research-grade solver.

## Proposed Module Layout

- `src/ciept/transport/types.py`
  - `TransportProblem`
  - `TransportResult`

- `src/ciept/transport/toy_solver.py`
  - `solve_partial_transport()`
  - validation helpers

- `src/ciept/transport/sanity.py`
  - lightweight semantic checks over solver outputs

## Data Structures

### `TransportProblem`

Fields:

- `cost: np.ndarray`
- `source_mass: np.ndarray`
- `target_capacity: np.ndarray`
- `mass_budget: float`
- `epsilon: float`
- `max_iters: int`
- `tolerance: float`

Validation:

- `cost` shape must match `(len(source_mass), len(target_capacity))`
- `source_mass` and `target_capacity` must be non-negative
- `mass_budget` must be positive
- `epsilon` must be positive

### `TransportResult`

Fields:

- `plan: np.ndarray`
- `transported_mass: float`
- `rejected_mass: float`
- `source_leftover: np.ndarray`
- `target_usage: np.ndarray`
- `target_slack: np.ndarray`
- `iterations: int`

## Solver Outline

1. validate the problem
2. compute kernel `K = exp(-cost / epsilon)`
3. initialize `T = K / K.sum() * mass_budget`
4. iterate:
   - project rows so row sums do not exceed `source_mass`
   - project columns so column sums do not exceed `target_capacity`
   - rescale total mass to `mass_budget` if needed
5. stop when the plan changes less than `tolerance` or `max_iters` is reached
6. report transported mass, leftovers, and slack

This routine is intentionally modest. It should be robust on toy problems, not exhaustive.

## Toy Cases

### 1. `mass_budget_binding`

Setup:

- source mass totals more than `mass_budget`
- capacities and costs would otherwise allow more transport

Expected behavior:

- transported mass equals `mass_budget`
- rejected mass is positive

### 2. `target_capacity_binding`

Setup:

- one target has the best cost but a small capacity
- another target is worse but has room

Expected behavior:

- first target saturates near its capacity
- remaining mass spills into the other target or remains rejected

### 3. `reject_over_bad_match`

Setup:

- part of the source has only very expensive matches
- total source mass exceeds what should be confidently transported

Expected behavior:

- low-cost matches are preferred
- bad-match mass remains untransported as reject mass

## Validation Rules

The solver should fail fast for:

- shape mismatches
- negative masses or capacities
- non-positive `mass_budget`
- non-positive `epsilon`
- NaN or Inf in the resulting plan

## Testing Strategy

Tests will verify:

- output shapes
- row sums respect source limits
- column sums respect target capacities
- transported mass respects the budget
- rejected mass matches the leftover source mass
- the three toy semantics above hold

Tests will not verify:

- global optimality
- gradients
- large-scale runtime behavior

## Follow-on Integration

This design gives `T006` a clean stepping stone:

- a transport result shape
- checked semantics for budget, capacity, and rejection
- a numerically meaningful toy baseline to compare future solver changes against
