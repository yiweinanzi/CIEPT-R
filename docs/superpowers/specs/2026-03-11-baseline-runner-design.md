# RecBole Data Bridge And Unified Baseline Runner Design

## Context

`B001` finished baseline inventory and a minimal RecBole config bootstrap, but the repository still cannot feed the offline `data/processed/` protocol into RecBole or execute baselines through a shared entrypoint.

The new work for `B002` is to add that bridge without changing the core `src/ciept/` research stack. RecBole remains an auxiliary layer for baseline alignment only.

## Goal

Add a baseline-only data bridge that converts CIEPT presplit artifacts into RecBole benchmark files, plus a unified baseline runner that standardizes run layout and execution dispatch.

## Scope

### In scope

- validating a presplit dataset directory
- writing RecBole benchmark atomic files from existing `train/valid/test` CSV files
- carrying optional item metadata into an atomic `.item` file
- building RecBole config for benchmark-file loading
- a unified runner API for recbole-backed and future external baselines
- standardized baseline result directories and result payloads

### Out of scope

- changing the CIEPT core research modules to depend on RecBole
- downloading datasets or baseline repositories
- integrating each baseline repository in this task
- benchmark-grade metric computation beyond runner/result plumbing

## Design Decisions

### 1. Bridge from offline presplit data instead of re-splitting in RecBole

The source of truth for dataset splitting stays in `src/ciept/data/`. The bridge only reformats already-split artifacts into RecBole atomic files and uses benchmark-file loading so RecBole does not re-split the data.

### 2. Keep bridge output ephemeral and baseline-scoped

The bridge writes a dedicated output directory that contains:

- `<dataset>.train.inter`
- `<dataset>.valid.inter`
- `<dataset>.test.inter`
- optional `<dataset>.item`
- `bridge_manifest.json`

This keeps baseline preparation explicit and avoids mutating the processed dataset source.

### 3. Use a narrow runner contract with injected executors

The unified runner should expose a request/result contract and dispatch by `integration_mode` from the baseline registry:

- `recbole`: prepare bridge output, build config, call a recbole executor
- `external_script`: reserve the standardized output path but raise a clear not-yet-implemented error until `B003+`

The recbole executor is injectable so tests can verify the runner without requiring RecBole to be installed in the environment.

### 4. Reuse the repository's existing result-writing pattern

Baseline runs should write under `results/baselines/<baseline>/<run_id>/` and produce:

- `metrics.json`
- `summary.md`

This mirrors the existing experiment output style and gives later baseline tasks a stable destination.

## Data Contract

The bridge accepts a dataset directory containing:

- required: `train.csv`, `valid.csv`, `test.csv`
- optional: `items.csv`

Required interaction columns:

- `user_id`
- `item_id`

Optional interaction columns that should be preserved when present:

- `rating`
- `timestamp`

If `items.csv` exists, it must include `item_id`. Other columns are emitted as token fields in the `.item` atomic file.

## Testing Strategy

Tests should verify:

- bridge validation fails for missing split files or missing required columns
- bridge output uses benchmark-file-compatible names and RecBole atomic headers
- runner dispatches recbole-backed baselines through a shared result protocol
- runner rejects unsupported baselines with explicit errors

Tests should not require:

- an installed RecBole package
- real model training
- downloaded benchmark datasets
