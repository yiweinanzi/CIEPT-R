# Delivery Bundle And Readiness Review Design

## Context

The repository now has:

- data protocol and stress artifacts
- graph, priors, transport, reranker, and intervention layers
- toy train/eval entrypoints
- reusable metrics
- an audit dataset protocol
- a dispatcher-based experiment runner

The remaining work for this phase is not paper writing. The immediate goal is to package the current engineering state into a reproducible delivery bundle, explicitly list the remaining external assets to download, and assess implementation status against `aaai项目.md`.

## Goal

Create a delivery bundle that:

- exports a reproducible manifest and entrypoint index
- snapshots task status and result directories
- lists required datasets, models, and baselines to download
- records an implementation review against `aaai项目.md`

## Scope

### In scope

- delivery manifest generation
- result indexing
- reproducibility checklist generation
- required-resource inventory generation
- implementation review generation against `aaai项目.md`
- a delivery CLI that writes all artifacts under `deliverables/current/`

### Out of scope

- paper writing
- real data downloads
- baseline model downloads
- release packaging or archive publishing

## Design Decisions

### 1. Delivery should be machine-readable and human-readable

The bundle should contain both JSON and Markdown outputs so it can serve:

- automated session recovery
- human handoff and review

### 2. Resource inventory is part of reproducibility

The user explicitly asked for a list of required datasets, models, and comparison methods to download. That inventory should not live only in chat output. It should be materialized as a file in the delivery bundle.

### 3. Implementation review should reference the project document directly

The review should compare current code coverage to the sections in `aaai项目.md`, not just to internal task labels. This makes the gap analysis auditable and easier to refine later.

### 4. Placeholder boundaries must be explicit

The review should separate:

- code that is implemented
- code that is still intentionally placeholder because it depends on datasets, VLMs, or external baselines
- code placeholders that should still be eliminated locally

This distinction matters for planning the next phase.

## Proposed Module Layout

- `src/ciept/delivery/manifest.py`
  - build delivery manifest
  - build results index
  - snapshot task state

- `src/ciept/delivery/review.py`
  - build implementation review against `aaai项目.md`
  - build required-resource inventory

- `src/ciept/delivery/export.py`
  - orchestrate writing the delivery bundle

- `src/ciept/delivery/cli.py`
  - CLI entrypoint:
    - `python -m ciept.delivery.cli --output-dir deliverables/current`

## Delivery Outputs

Under `deliverables/current/`:

- `manifest.json`
  - commit
  - current focus
  - entrypoints
  - environment summary

- `results_index.json`
  - experiment runs and paths to `metrics.json` / `summary.md`

- `task_snapshot.json`
  - machine-readable copy of current task state

- `reproducibility_checklist.md`
  - human-readable run/verify checklist

- `entrypoints.md`
  - concise list of important commands and modules

- `required_assets.md`
  - datasets, models, and baseline methods to download later

- `implementation_review.md`
  - section-by-section implementation review against `aaai项目.md`

## Resource Inventory Requirements

The required-assets file should at minimum list:

- core datasets
- appendix / cross-domain datasets
- VLM placeholder dependencies
- baseline method families and concrete methods

It should distinguish:

- needed now
- needed later
- intentionally deferred

## Implementation Review Requirements

The implementation review should:

- reference major sections from `aaai项目.md`
- mark each area as:
  - implemented
  - partial
  - placeholder-dependent
  - missing
- call out placeholder code that remains locally
- highlight risks before real data/model integration

## Validation Rules

The delivery generator should fail fast for:

- missing `continue/task.json`
- missing `aaai项目.md`

It should tolerate missing `results/` directories by writing empty indexes instead of crashing.

## Testing Strategy

Tests will verify:

- delivery CLI writes all expected bundle files
- results index works with empty and non-empty `results/`
- resource inventory includes expected sections
- implementation review references project-document sections

Tests will not verify:

- correctness of future downloaded resources
- cross-machine reproducibility
- final scientific completeness

## Follow-on Integration

This design gives the next phase:

- a stable handoff package
- an explicit download to-do list
- a concrete implementation gap report before moving into real data and model integration
