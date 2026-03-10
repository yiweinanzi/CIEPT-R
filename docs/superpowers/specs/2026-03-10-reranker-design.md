# Capacity-Calibrated Partial Transport Reranker Design

## Context

`T005` established a NumPy-based toy transport sanity layer that already verifies three core transport semantics:

- explicit mass-budget binding
- target-capacity binding
- reject-mass semantics

`T006` is the first step from toy validation into a model-facing forward path. It should not attempt to implement the full research solver yet, but it should introduce a `torch.nn.Module` reranker skeleton that genuinely uses:

- feature costs
- source mass `p`
- target capacity `q_cap`
- global mass budget

This is the bridge between the semantic toy solver and later training-oriented tasks.

## Goal

Create a torch-based `CapacityCalibratedPartialTransportReranker` that performs a minimal but real forward pass over node features, computes a transport plan, and derives a scalar score from that plan.

## Scope

### In scope

- a model-facing reranker input/output interface
- a torch-based feature-cost computation
- a reliability-derived cost penalty path
- a torch partial-transport operator with iterative row/column/mass projection
- a scalar score derived from the transport plan
- tests proving `p`, `q_cap`, and `mass_budget` affect the output

### Out of scope

- Gromov regularization
- learned mass-budget prediction
- intervention losses
- full training loop integration
- batching and large-scale performance claims

## Design Decisions

### 1. Torch forward path, but minimal scope

The reranker should be implemented as a `torch.nn.Module`, because `T006` is about introducing the model boundary, not repeating a NumPy prototype. However, it should still stay narrow and not claim research-grade solver completeness.

### 2. Split responsibilities by concern

The transport layer should be extended using focused files:

- `types.py` for model-facing input/output dataclasses
- `costs.py` for feature cost and reliability penalties
- `operators.py` for the torch transport operator
- `reranker.py` for the model wrapper

This keeps later extensions for `T007/T008` localized and avoids mixing scoring, transport, and cost construction into one file.

### 3. Reuse toy semantics, not toy implementation

The operator should preserve the semantics proven in `T005`, but it should not call the NumPy solver directly. Instead, it should implement the same broad row/column/mass projection pattern with torch tensors so later model code can stay in one tensor world.

### 4. Feature cost stays simple and explicit

The feature-cost function should use a simple distance such as squared Euclidean distance. The goal is not to invent a clever metric; it is to make the reranker’s inputs and outputs structurally real.

### 5. Reliability penalty must enter the actual cost path

`q_cap` must not be an unused input. It should influence the cost matrix directly, for example by adding a penalty term proportional to low capacity:

`cost' = cost + strength * (1 - q_cap)`

This makes it testable that shrinking a target’s capacity changes the resulting plan.

### 6. Score extraction remains placeholder but meaningful

The first reranker score can be defined as:

`score = -(plan * penalized_cost).sum()`

This is not the final research scoring rule, but it gives a clean scalar that genuinely depends on the transport plan.

## Proposed Module Layout

- `src/ciept/transport/types.py`
  - keep `TransportProblem`
  - keep `TransportResult`
  - add `RerankerInputs`
  - add `RerankerOutputs`

- `src/ciept/transport/costs.py`
  - `compute_feature_cost()`
  - `apply_reliability_penalty()`

- `src/ciept/transport/operators.py`
  - `torch_partial_transport()`
  - tensor validation helpers

- `src/ciept/transport/reranker.py`
  - `CapacityCalibratedPartialTransportReranker`

## Data Structures

### `RerankerInputs`

Fields:

- `user_nodes: torch.Tensor`
- `item_nodes: torch.Tensor`
- `source_mass: torch.Tensor`
- `target_capacity: torch.Tensor`
- `mass_budget: torch.Tensor | float`

This task only needs to support minimal forward usage, such as a single sample or a very small batch. Full batch-oriented abstractions can come later.

### `RerankerOutputs`

Fields:

- `score: torch.Tensor`
- `plan: torch.Tensor`
- `transported_mass: torch.Tensor`
- `target_usage: torch.Tensor`

## Forward Path

1. validate shapes and scalar constraints
2. compute feature cost from `user_nodes` and `item_nodes`
3. apply a reliability penalty driven by `target_capacity`
4. run a torch partial-transport operator over the penalized cost
5. compute:
   - `score`
   - `transported_mass`
   - `target_usage`
6. return `RerankerOutputs`

## Operator Outline

The torch operator should follow the same semantic structure as the toy solver:

1. compute `kernel = exp(-cost / eps)`
2. initialize a dense plan
3. iteratively project:
   - rows to respect `source_mass`
   - columns to respect `target_capacity`
   - total mass to respect `mass_budget`

The operator should be numerically safe and stop after convergence or iteration limit.

## Validation Rules

The reranker should fail fast for:

- mismatched node feature dimensions
- mismatched cost-vs-mass shapes
- negative masses or capacities
- non-positive `mass_budget`
- NaN or Inf in the plan

No silent fallback should hide bad tensor states.

## Testing Strategy

Tests will verify:

- forward outputs exist with expected shapes
- shrinking `target_capacity` reduces or caps target usage
- shrinking `mass_budget` reduces transported mass
- `q_cap` affects the plan through both capacity constraint and penalty path
- score depends on the transport plan

Tests will not verify:

- training stability
- gradients
- Gromov behavior
- production-scale throughput

## Environment Note

The current repository environment does not yet have `torch` installed. `T006` therefore includes:

- adding `torch` to the project dependency surface
- installing it in the active environment before running tests

## Follow-on Integration

This design gives `T007` and `T008`:

- a model-facing transport reranker boundary
- a torch-native plan output
- a scalar score path
- a controlled place to add intervention and ranking losses later
