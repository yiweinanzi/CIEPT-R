# VLM Audit Dataset And Adjudication Design

## Context

`T009` established an offline conflict-stress pipeline that writes structured perturbation artifacts, nuisance masks, protocol summaries, and review queues under `data/interim/`.

The next step is to derive an audit dataset protocol that later VLMs and human reviewers can use. The task should not bind the repository to any specific VLM API, but it should make external VLM predictions pluggable and traceable.

## Goal

Create an audit-dataset pipeline that:

- samples structured audit examples from stress artifacts
- exports VLM request payloads
- merges external VLM predictions back into annotated audit records
- initializes human adjudication queues
- tracks coverage and missing-data statistics in a manifest

## Scope

### In scope

- audit dataset schemas
- audit example export
- VLM request export
- VLM prediction merge protocol
- adjudication queue initialization
- manifest tracking for coverage and missing predictions

### Out of scope

- calling a real VLM API
- human annotation UI
- final Cohen’s kappa implementation
- large-scale sample generation

## Design Decisions

### 1. Audit examples are first-class records

The repository should not treat audit examples as temporary views over stress artifacts. They should be materialized as their own JSONL file with stable `audit_id` values so predictions and adjudication records can reference them cleanly.

### 2. VLM integration is file-based and provider-agnostic

Instead of binding to any one provider, the repository should export `vlm_requests.jsonl` and accept `vlm_predictions.jsonl` back. This keeps the protocol stable even if the chosen VLM changes later.

### 3. VLM predictions never overwrite source artifacts

Merged predictions should produce a derived file such as `audit_examples_annotated.jsonl`. Original audit examples stay immutable.

### 4. Human adjudication stays separate from VLM predictions

Human review records should live in their own queue file and should not overwrite the raw VLM prediction object. This keeps provenance clear and preserves room for multi-annotator workflows.

### 5. Manifest is the control plane

The pipeline should maintain a `manifest.json` that records:

- sample counts
- prediction coverage
- missing predictions
- adjudication queue size
- run metadata

This gives later evaluation code a stable summary source.

## Proposed Module Layout

- `src/ciept/audit/audit_types.py`
  - `AuditExample`
  - `AuditPrediction`
  - `AuditAdjudication`
  - `AuditDatasetManifest`

- `src/ciept/audit/audit_dataset.py`
  - build audit examples from stress artifacts
  - write `audit_examples.jsonl`
  - write `manifest.json`

- `src/ciept/audit/vlm_io.py`
  - export `vlm_requests.jsonl`
  - read `vlm_predictions.jsonl`
  - merge predictions into `audit_examples_annotated.jsonl`

- `src/ciept/audit/adjudication.py`
  - initialize `adjudication_queue.jsonl`
  - write placeholder adjudication records

- `src/ciept/audit/audit_cli.py`
  - `build`
  - `merge-vlm`
  - `init-adjudication`

## File Formats

### `audit_examples.jsonl`

Each record should contain:

- `audit_id`
- `source_example_id`
- `label`
- `perturbation_family`
- `strength`
- `text_nodes`
- `vision_nodes`
- `nuisance_mask`
- `review_status`

### `vlm_requests.jsonl`

Each record should contain:

- `audit_id`
- `prompt_version`
- `instruction`
- `evidence_payload`

### `vlm_predictions.jsonl`

Each record should contain:

- `audit_id`
- `predicted_minimal_evidence`
- `predicted_nuisance_nodes`
- `confidence`
- `raw_response`

### `audit_examples_annotated.jsonl`

Each record should contain the original audit example plus:

- `vlm_prediction`
- `annotation_source`

### `adjudication_queue.jsonl`

Each record should contain:

- `audit_id`
- `source_example_id`
- `label`
- `vlm_prediction`
- `adjudicator_a`
- `adjudicator_b`
- `final_label`
- `status`

## Merge Rules

### VLM merge

- match by `audit_id`
- do not mutate original `audit_examples.jsonl`
- record missing predictions in `manifest.json`
- record unknown prediction ids separately in the manifest

### Adjudication initialization

- create queue entries from annotated audit examples
- default adjudicator fields to empty strings
- set `status = "pending"`

## Validation Rules

The pipeline should fail fast for:

- duplicate `audit_id`
- missing required fields in source audit examples
- empty adjudication input

It should not fail the whole run for partial VLM prediction coverage. Instead, it should record missing or unknown ids in the manifest.

## Testing Strategy

Tests will verify:

- audit examples can be built from stress artifacts
- VLM request export is generated
- VLM prediction merge produces annotated audit records
- adjudication queue initialization works
- manifest tracks coverage, missing predictions, and queue counts

Tests will not verify:

- real VLM outputs
- real human annotation
- final agreement statistics

## Follow-on Integration

This design gives later tasks:

- a stable audit dataset protocol
- a file-based VLM integration path
- a clean place to add agreement metrics and usage-diagnosis evaluation
