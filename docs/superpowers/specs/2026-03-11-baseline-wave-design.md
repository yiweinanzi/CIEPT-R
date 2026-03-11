# Baseline Integration Wave B003-B011 Design

## Context

`B002` already created a baseline-only data bridge and a unified runner entrypoint, but the repository still lacks concrete baseline-family adapters, mapping conclusions for downloaded candidates, and a truthful tracking layer for missing or mismatched assets.

The next wave spans `B003` through `B011`:

- `B003-B009`: concrete baseline integrations or truthful blocker handling
- `B010`: candidate mapping confirmation
- `B011`: missing-baseline acquisition tracking

The user explicitly asked to continue with the recommended approach and not pause for additional design approval. This design therefore records the chosen approach directly.

## Goal

Extend `src/ciept/baselines/` into a metadata-driven baseline integration layer that:

- prepares presplit datasets for real baseline families
- standardizes per-baseline run outputs
- confirms candidate-to-paper mappings
- truthfully records missing or incompatible assets

## Approaches Considered

### Approach 1: One-off wrapper per baseline

Write a separate runner, dataset formatter, and parser for every baseline task.

- Pros: straightforward for the first one or two baselines
- Cons: duplicates archive handling, dataset conversion, output writing, and tracking logic

### Approach 2: Family-based adapters with shared registry

Group baselines by execution/runtime shape and implement one adapter family per shape.

- `recbole` family: LightGCN
- `vbpr_python` family: VBPR
- `mmrec` family: BM3 and MGCN
- `i3mrec` family: I3-MRec
- `graph_imputation` family: Training-free Graph-based Imputation
- metadata-only mismatch tracking: CLEAR and candidate mappings

- Pros: keeps code small, matches the actual archive landscape, makes later baseline additions cheaper
- Cons: requires a bit more upfront structure

### Approach 3: Metadata-only command generator

Only emit shell commands and manifests without any dataset-family preparation code.

- Pros: smallest implementation
- Cons: does not really satisfy the “read presplit data” requirement and leaves too much manual work

## Recommendation

Use **Approach 2**.

It matches the actual downloaded resources: BM3 and MGCN clearly share an MMRec-style dataset/runtime contract; VBPR has a self-contained Python package; LightGCN already aligns with the RecBole auxiliary path; and candidate/missing tracking belongs in registry metadata rather than ad-hoc notes.

## Architecture

### 1. Expand baseline registry into a richer source of truth

The registry should record, per baseline:

- archive pattern
- paper mapping
- integration mode
- dataset format family
- execution status (`direct_match`, `mapped_match`, `mapped_candidate`, `missing`, `asset_mismatch`)
- whether the baseline should be considered part of the main comparison set
- tracking notes and next actions

This enables `B010` and `B011` without inventing a second tracking system.

### 2. Add reusable archive and dataset-preparation helpers

Create baseline-only helpers for:

- idempotent archive extraction to a run-local work directory
- numeric remapping of user/item ids for external repos
- MMRec-style `.inter` generation with `x_label`
- deterministic placeholder image/text features for smoke execution when real embeddings are absent
- VBPR-ready interaction/feature packaging

The placeholder-feature fallback is intentional: it enables integration/smoke execution in this bootstrap repository without pretending to reproduce benchmark-grade multimodal features.

### 3. Extend the unified runner with adapter-family dispatch

The runner should dispatch by `integration_mode`:

- `recbole`: use the existing bridge and a RecBole executor
- `vbpr_python`: prepare presplit numeric interactions plus visual features and call a Python-native executor
- `mmrec`: extract repo, prepare MMRec dataset files, and emit/optionally run a reproducible command plan
- `i3mrec`: extract repo, prepare `.inter` plus feature files, and emit/optionally run a reproducible command plan
- `graph_imputation`: extract repo, prepare indexed/modality inputs, and emit a command plan for the imputation entrypoint
- `asset_mismatch`: fail fast with a truthful incompatibility error

All modes still write under `results/baselines/<baseline>/<run_id>/`.

### 4. Treat CLEAR as a blocker, not a fake success

The downloaded `CLEAR-replication-main.zip` is an API recommendation repository, while the project requires the multimodal recommendation baseline:

- project baseline: `CLEAR: Null-Space Projection for Cross-Modal De-Redundancy in Multimodal Recommendation`
- downloaded archive: `CLEAR: Contrastive Learning for API Recommendation`

That mismatch must be represented explicitly as `asset_mismatch`. `B008` should become `blocked`, and `B011` should track acquisition of the correct CLEAR asset.

### 5. Promote confirmed candidate mappings into tracking results

Based on the downloaded READMEs:

- `Guider` maps to `Teach Me How to Denoise`
- `MAGNET` maps to `Modality-Guided Mixture of Graph Experts`
- `DiffMM`, `MixRec`, and `SMORE` remain candidate-only references, not main-table matches

These conclusions should be written into the baseline registry and reflected in the required-assets tracking file.

## File Layout

- `src/ciept/baselines/registry.py`
  - richer baseline metadata and inventory classification
- `src/ciept/baselines/archive.py`
  - archive extraction and root-path helpers
- `src/ciept/baselines/formats.py`
  - MMRec/VBPR/I3-MRec/graph-imputation dataset preparation helpers
- `src/ciept/baselines/runner.py`
  - expanded dispatch for new baseline families
- `src/ciept/baselines/__init__.py`
  - narrow public exports
- `tests/test_baseline_registry.py`
  - richer inventory and mapping assertions
- `tests/test_baseline_formats.py`
  - dataset preparation tests
- `tests/test_baseline_runner.py`
  - runner dispatch/output tests
- `tests/test_persistence.py`
  - `B003-B011` task-state assertions
- `deliverables/current/required_assets.md`
  - missing/mismatched baseline tracking

## Error Handling

- missing archive: inventory marks `missing`, runner raises a clear availability error
- incompatible archive: inventory marks `asset_mismatch`, runner raises a clear incompatibility error
- unsupported integration mode: fail fast
- malformed presplit dataset: dataset formatter raises clear validation errors

## Testing Strategy

Tests should verify:

- registry now distinguishes direct matches, confirmed mappings, candidate-only references, missing assets, and asset mismatches
- MMRec/VBPR/I3-MRec data preparation is deterministic and derived from presplit inputs
- unified runner writes standardized outputs for each adapter family via injected executors
- CLEAR mismatch is surfaced as a blocker instead of being silently accepted
- persistence state reflects completed `B003-B007`, `B009-B011`, and blocked `B008`

Tests should not require:

- benchmark-scale datasets
- full external training runs inside pytest
- modification of the downloaded `baselines/` archives
