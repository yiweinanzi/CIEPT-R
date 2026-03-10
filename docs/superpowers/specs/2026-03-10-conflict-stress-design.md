# Conflict Stress Test Protocol Design

## Context

The repository now has:

- a data protocol and preprocessing layout
- graph structures
- heuristic priors
- a toy transport sanity solver
- a torch reranker
- an intervention layer
- a toy train/eval entrypoint

What it still lacks is the offline perturbation protocol required by the project notes for conflict stress testing. `T009` fills that gap by producing reproducible positive-preserving nuisance and negative-preserving lure examples, along with masks and metadata that later tasks can reuse.

## Goal

Create an offline perturbation pipeline that writes structured conflict-stress artifacts to `data/interim/` and records nuisance/lure masks, protocol metadata, and review queues.

## Scope

### In scope

- dataclass-based perturbation schemas
- single-example positive-preserving nuisance rules
- single-example negative-preserving lure rules
- a pipeline that runs the rules over JSONL input
- writing outputs under `data/interim/conflict_stress/`
- protocol summary and review-queue generation

### Out of scope

- real dataset downloads
- pixel-level image manipulation
- VLM auditing
- human review tooling
- benchmark-scale runs

## Design Decisions

### 1. Protocol-first, not helper-function-only

The perturbation layer should not stop at in-memory transforms. It should define a reproducible offline protocol with on-disk outputs so later tasks can consume the same artifacts.

### 2. Strength is node-level coverage, not raw token count

Strength values `0.1`, `0.3`, and `0.5` should be interpreted as the proportion of perturbable evidence units that are modified. This aligns the protocol with the repository’s node-based graph abstractions.

### 3. Positive-preserving nuisance and negative-preserving lure remain separate families

The two perturbation families should remain distinct in both logic and metadata:

- `positive_nuisance`
- `negative_lure`

This makes later evaluation and review more explicit.

### 4. Masks should be node-level and JSON-friendly

The protocol should emit masks in JSON-friendly structures instead of binary tensors or custom blobs. Later tasks can convert them into tensors when needed.

### 5. Review queues must be generated with the same run

Because the project notes require later human review, the pipeline should produce a lightweight `review_queue.jsonl` immediately rather than relying on downstream reconstruction.

## Proposed Module Layout

- `src/ciept/data/stress_types.py`
  - `PerturbationConfig`
  - `PerturbationExample`
  - `PerturbationRecord`

- `src/ciept/data/stress_rules.py`
  - `apply_positive_preserving_nuisance()`
  - `apply_negative_preserving_lure()`

- `src/ciept/data/stress_pipeline.py`
  - `load_examples()`
  - `generate_conflict_stress_dataset()`
  - `write_conflict_stress_outputs()`

- `src/ciept/data/stress_cli.py`
  - CLI wrapper for offline protocol generation

## Input Schema

Each source example should minimally contain:

- `example_id`
- `label`
- `text_nodes`
- `vision_nodes`

Each node should contain at least:

- `node_id`
- `content`
- `source`
- optional metadata

## Perturbation Families

### Positive-preserving nuisance

Purpose:

- keep the example label positive
- inject clearly non-decisive distracting evidence

Examples:

- marketing phrase insertion
- OCR-style noisy snippet insertion
- background/banner/logo region insertion

### Negative-preserving lure

Purpose:

- keep the example label negative
- inject superficially attractive but non-decisive cues

Examples:

- user-style keyword insertion
- similar-but-non-decisive attribute insertion
- background style/texture/color lure regions

## Strength Semantics

For a given example:

- compute how many nodes are perturbable
- choose approximately `ceil(count * strength)` nodes or slots to modify
- use strengths from the fixed set `{0.1, 0.3, 0.5}`

If no perturbable nodes exist, the example may be skipped, but the skip must be reported in the summary.

## Output Files

Under `data/interim/conflict_stress/<run_name>/`:

- `examples.jsonl`
  - perturbed examples with original and perturbed node lists

- `nuisance_mask.json`
  - node-level masks keyed by example id

- `protocol_summary.json`
  - run metadata, counts, strengths, rule usage, skipped examples

- `review_queue.jsonl`
  - lightweight human-review queue with changed fields and pending status

## Validation Rules

The pipeline should fail fast for:

- missing required fields
- invalid strength values
- mismatched node/mask lengths

It should tolerate empty text or vision node lists, as long as shapes remain internally consistent.

## Testing Strategy

Tests will verify:

- nuisance perturbations preserve labels and mark changed nodes
- lure perturbations preserve labels and add lure-marked nodes
- strength changes how many nodes are modified
- the pipeline writes all expected files
- the review queue is populated

Tests will not verify:

- real image perturbation quality
- human-review outcomes
- VLM quality
- large-scale throughput

## Follow-on Integration

This design gives later tasks:

- offline perturbation artifacts
- reproducible nuisance/lure metadata
- masks that can feed evaluation and audit code
- a clear handoff point for human and VLM review
