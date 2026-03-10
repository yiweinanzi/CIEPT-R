# Reliability Prior And Capacity Prior Design

## Context

`T003` established the graph-facing boundary for item evidence nodes, block-diagonal topology, and cache serialization. `T004` builds directly on top of that boundary and introduces the first runnable prior layer that later transport code can consume.

The purpose of `T004` is to create a lightweight but executable prior system for:

- per-node signal scoring
- reliability aggregation
- capacity prior computation
- nuisance-mask generation

This layer should remain heuristic and interpretable. It is not the place for learned heads or transport integration.

## Goal

Create a `ciept.priors` package that:

- computes corroboration, stability, and vulnerability scores for each node
- aggregates them into reliability scores
- converts reliability scores into a normalized capacity prior
- derives nuisance masks with explicit-label priority and heuristic fallback

## Scope

### In scope

- dataclass-based signal and prior result types
- heuristic signal computation from `EvidenceNode.metadata`
- reliability aggregation with stable defaults
- `q_cap` normalization with safe fallback behavior
- nuisance-mask inference with source tracking
- toy tests showing basic clean-vs-nuisance separation

### Out of scope

- learned reliability heads
- dataset-scale evaluation or AUROC reporting
- transport coupling
- `torch`-based implementations
- full audit protocol

## Design Decisions

### 1. Split signals before aggregation

The prior layer will compute three separate interpretable signals:

- `corroboration`
- `stability`
- `vulnerability`

These are not merged in the heuristics stage. They are combined later through a small aggregation function so later tasks can replace one signal family without rewriting the rest of the module.

### 2. Metadata-first heuristics

If metadata contains explicit numeric or boolean hints, those hints take priority. Examples include:

- `support_count`
- `cross_modal_match`
- `corroborated`
- `stability`
- `consistency`
- `region_role`
- `noise_risk`
- `is_low_relevance_region`

If metadata is missing or malformed, the code falls back to conservative default values and simple string-based heuristics.

### 3. Explicit nuisance labels override heuristics

If a node carries an explicit `is_nuisance` label, that label wins. If not, the nuisance layer applies heuristic inference.

The user requested a heuristic policy that leans toward catching more suspicious nodes, so the fallback should be slightly aggressive rather than overly conservative.

### 4. Nuisance decisions track provenance

Each nuisance decision should record whether it came from:

- `explicit`
- `heuristic`

This helps keep the future audit story honest and avoids conflating inferred nuisance labels with externally curated ones.

### 5. Capacity prior remains interpretable

The prior follows the project’s paper direction:

`q_j ∝ reliability_j * a_j`

For `T004`, the base capacity `a_j` defaults to `1.0`, while still allowing per-node overrides later via metadata. If all reliability scores collapse to zero, normalization falls back to an epsilon-safe distribution instead of producing NaNs.

## Proposed Module Layout

- `src/ciept/priors/types.py`
  - `NodeSignalScores`
  - `ReliabilityProfile`
  - `CapacityPrior`
  - `NuisanceDecision`
  - `NuisanceMask`

- `src/ciept/priors/heuristics.py`
  - `corroboration_score()`
  - `stability_score()`
  - `vulnerability_score()`
  - helper functions for metadata parsing

- `src/ciept/priors/aggregate.py`
  - `aggregate_reliability()`
  - `build_capacity_prior()`

- `src/ciept/priors/nuisance.py`
  - `infer_nuisance_mask()`
  - explicit-label precedence
  - heuristic fallback with provenance tracking

## Heuristic Rules

### Corroboration

Higher when:

- metadata says the node is corroborated
- support counts are present and non-trivial
- a text node references visual corroboration
- a vision node references text corroboration
- the source is a structurally important field such as `title` or `key_attribute`

### Stability

Higher when:

- metadata provides explicit stability-like signals
- text comes from structured fields
- vision regions are marked as foreground or product-centric

Lower when:

- text resembles a short slogan or generic filler
- vision nodes come from background, banner, or decorative regions

### Vulnerability

Higher when:

- text contains hype, generic marketing, or OCR-like noise fragments
- vision nodes are from background, banner, logo, or text-overlay regions
- metadata indicates low relevance or saliency leakage risk

## Reliability Aggregation

Use a simple weighted formula:

`reliability = clamp(w_c * corroboration + w_s * stability - w_v * vulnerability, eps, 1.0)`

Default weights:

- `w_c = 0.4`
- `w_s = 0.4`
- `w_v = 0.3`

The goal is interpretability, not sophistication.

## Nuisance Mask Policy

Priority order:

1. explicit `is_nuisance`
2. heuristic fallback

Heuristic fallback should label a node as nuisance when one or more high-risk patterns appear, including:

- marketing-heavy or exaggerated text
- OCR fragments that look noisy or decorative
- background, banner, logo, decor, or text-overlay regions
- high vulnerability paired with low corroboration

## Validation Rules

The prior layer should fail fast only for truly invalid structural inputs, such as an empty node list when building a full profile.

Malformed metadata should not crash the run. Instead:

- booleans fall back to default false
- numbers fall back to default neutral values
- missing fields fall back to heuristic defaults

## Testing Strategy

Tests will cover:

- heuristic score directionality
- reliability aggregation
- capacity prior normalization
- nuisance explicit-vs-heuristic precedence
- toy clean-vs-nuisance separation

Tests will not cover:

- large-scale statistical quality
- training dynamics
- transport interactions

## Follow-on Integration

This design gives `T005` and later tasks:

- node-wise reliability values
- normalized capacity priors
- nuisance masks with provenance
- a clean bridge between graph structure and transport semantics
