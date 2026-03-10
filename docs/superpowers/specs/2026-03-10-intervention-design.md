# Normalized Support And Intervention Design

## Context

`T006` introduced a torch-based reranker skeleton that produces a transport plan, transported mass, and target usage. That gives the repository a model-facing transport entrypoint, but not yet an intervention or faithfulness layer.

`T007` bridges that gap. It should introduce the first trainable-style intervention module that:

- converts transport support into normalized support
- maps normalized support into logits
- builds a binary straight-through gate
- measures leakage through a ratio, not an absolute sum

This task should remain focused on module boundaries and loss computation, not on full training orchestration.

## Goal

Create a `ciept.audit` package that implements capacity-normalized support, straight-through binary gating, and a single-pass intervention loss with leakage-ratio diagnostics.

## Scope

### In scope

- normalized support from item-side transport mass
- support-to-logit conversion
- binary Gumbel/straight-through gating
- leakage ratio computation
- a lightweight intervention scorer
- a combined single-pass intervention loss

### Out of scope

- full training loop integration
- temperature scheduling logic beyond a passed-in `tau`
- VLM audit protocols
- dataset-scale faithfulness evaluation

## Design Decisions

### 1. Capacity normalization happens before everything else

Support should be derived from item-side transport mass:

`raw_support = plan.sum(dim=0)`

Then normalized by the target capacity prior:

`norm_support = raw_support / (q_cap + eps)`

Only after that step should the support enter logit or gate computation. This is a key scientific constraint from the project specification.

### 2. Logits should come from normalized support, not raw support

The gating path should use:

`logits = log(norm_support) - log(1 - norm_support)`

This keeps the module aligned with the intended intervention semantics and avoids treating transport mass as if it were already a calibrated probability.

### 3. Use a straight-through binary gate

The task should introduce a differentiable approximation to binary evidence selection. A minimal binary Gumbel/STE gate is enough:

- add stochastic noise
- compute a soft gate
- use a hard threshold in forward mode
- preserve gradients through the soft gate

This allows `T008` to reuse the module in training-oriented code.

### 4. Leakage must stay ratio-based

`Leakage Ratio` should be implemented as:

`(norm_support * nuisance_mask).sum() / (norm_support.sum() + eps)`

This prevents the metric from being gamed by shrinking total transported mass and is explicitly required by the project notes.

### 5. Intervention scoring stays lightweight

The intervention module should not call the full reranker recursively. Instead, it should compute a small differentiable score from masked item nodes and a user representation. This keeps the module independent and easy to test.

## Proposed Module Layout

- `src/ciept/audit/types.py`
  - `SupportOutputs`
  - `InterventionOutputs`

- `src/ciept/audit/support.py`
  - `normalized_support()`
  - `support_to_logits()`

- `src/ciept/audit/gating.py`
  - `binary_gumbel_ste()`

- `src/ciept/audit/losses.py`
  - `leakage_ratio()`
  - `lightweight_scorer()`
  - `single_pass_intervention()`

## Data Structures

### `SupportOutputs`

Fields:

- `raw_support: torch.Tensor`
- `normalized_support: torch.Tensor`
- `logits: torch.Tensor`

### `InterventionOutputs`

Fields:

- `gate: torch.Tensor`
- `score_selected: torch.Tensor`
- `score_removed: torch.Tensor`
- `loss_sufficiency: torch.Tensor`
- `loss_comprehensiveness: torch.Tensor`
- `loss_leakage: torch.Tensor`
- `loss_total: torch.Tensor`

## Computation Flow

1. compute item-side raw support from `plan.sum(dim=0)`
2. normalize by `q_cap`
3. clamp into `(eps, 1 - eps)`
4. convert to logits
5. sample a straight-through binary gate with temperature `tau`
6. compute:
   - selected-only score
   - selected-removed score
7. compute:
   - sufficiency loss
   - comprehensiveness loss
   - leakage-ratio loss
8. combine into one scalar objective

## Lightweight Scorer

The scorer should remain simple and differentiable:

- aggregate `user_nodes` into a user representation
- mask `item_nodes` with the intervention gate
- average active item evidence
- score with cosine similarity or a similarly simple differentiable comparator

This scorer is intentionally provisional and should not be confused with the final ranking objective.

## Validation Rules

The module should fail fast for:

- plan and `q_cap` length mismatch
- nuisance-mask and item-node length mismatch
- non-positive `tau`
- non-finite outputs

It should use `eps` clamping to avoid invalid `log()` operations, but it should not silently hide structural input errors.

## Testing Strategy

Tests will verify:

- support is normalized by `q_cap`
- logits remain finite
- the gate stays within `[0, 1]`
- leakage uses a ratio
- single-pass intervention returns the expected outputs
- nuisance-heavy toy inputs produce larger leakage loss than clean toy inputs

Tests will not verify:

- training convergence
- schedule quality for `tau`
- large-batch performance
- full paper-level faithfulness claims

## Follow-on Integration

This design gives `T008`:

- a reusable intervention loss path
- a normalized-support representation
- a ratio-based leakage metric
- a clean bridge between transport outputs and ranking/training objectives
