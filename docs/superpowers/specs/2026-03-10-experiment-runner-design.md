# Experiment Runner And Result Template Design

## Context

The repository now has:

- data protocol and conflict-stress artifacts
- graph, priors, reranker, and intervention layers
- toy train/eval entrypoints
- reusable metrics
- audit dataset and adjudication protocol

What it still lacks is a unified experiment runner that can call these components, write structured outputs, and create stable result directories. `T012` provides that orchestration layer.

## Goal

Create a unified experiment runner that dispatches named experiments, writes `metrics.json` and `summary.md` under `results/`, and establishes stable result schemas for later real experiments.

## Scope

### In scope

- an experiment dispatcher
- per-experiment modules for:
  - main results
  - robustness
  - faithfulness
  - ablation
  - usage
  - efficiency
- result directory layout
- JSON and Markdown outputs

### Out of scope

- real benchmark execution
- significance testing
- figure generation
- multi-seed aggregation

## Design Decisions

### 1. Use a dispatcher, not one giant experiment script

The repository should use a central runner that dispatches to experiment modules by name. This matches the project document’s experiment structure and avoids a large conditional script.

### 2. Result directories must be stable and append-only

Each run should write to:

`results/<experiment_name>/<run_id>/`

This preserves past runs and avoids accidental overwrite.

### 3. Every experiment must write both machine-readable and human-readable outputs

Each experiment should produce:

- `metrics.json`
- `summary.md`

This gives later tooling a stable parse target while keeping the run human-inspectable.

### 4. Toy values are acceptable if clearly labeled

At this stage, experiment modules may emit toy or placeholder values, but the summary must clearly state that the run is not a real benchmark. The goal is to lock down protocol and output format, not to fake scientific results.

## Proposed Module Layout

- `src/ciept/experiments/types.py`
  - `ExperimentContext`
  - `ExperimentResult`

- `src/ciept/experiments/io.py`
  - run directory creation
  - write `metrics.json`
  - write `summary.md`

- `src/ciept/experiments/runner.py`
  - `run_experiment()`
  - dispatcher map

- `src/ciept/experiments/main_results.py`
- `src/ciept/experiments/robustness.py`
- `src/ciept/experiments/faithfulness.py`
- `src/ciept/experiments/ablation.py`
- `src/ciept/experiments/usage.py`
- `src/ciept/experiments/efficiency.py`

## Result Format

### `metrics.json`

Must contain:

- `experiment_name`
- `run_id`
- `metrics`
- `notes`

### `summary.md`

Must contain:

- experiment name
- run id
- whether the run is toy/placeholder
- metric summary
- limitations / caveats

## Experiment Minimum Outputs

### `main_results`

At minimum:

- `clean_ndcg_at_20`
- `high_conflict_ndcg_at_20`
- `missing_modality_ndcg_at_20`
- `long_tail_ndcg_at_20`

### `robustness`

At minimum:

- `retention_at_0_1`
- `retention_at_0_3`
- `retention_at_0_5`

### `faithfulness`

At minimum:

- `support_precision`
- `support_recall`
- `support_f1`
- `leakage_ratio`
- `sufficiency_gap`
- `comprehensiveness_gap`

### `ablation`

At minimum:

- `full_model_score`
- `wo_capacity_prior_score`
- `wo_intervention_loss_score`

### `usage`

At minimum:

- `image_shuffle_drop_rate`
- `random_caption_drop_rate`
- `missing_modality_drop`
- `transported_mass_ratio`

### `efficiency`

At minimum:

- `forward_time_ms`
- `train_step_time_ms`
- `peak_memory_mb`

## Validation Rules

The runner should fail fast for:

- unknown experiment names
- empty metric dictionaries
- output write failures

It should not silently overwrite an existing run directory.

## Testing Strategy

Tests will verify:

- dispatcher routing
- output directory layout
- `metrics.json` creation
- `summary.md` creation
- unknown experiment failure

Tests will not verify:

- real benchmark quality
- significance testing
- plotting

## Follow-on Integration

This design gives the final stage:

- a stable experiment orchestration layer
- predictable result directories
- a clear handoff for paper-facing exports and final delivery
