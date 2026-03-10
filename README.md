# CIEPT-R Bootstrap Repository

This repository bootstraps the engineering workspace for the AAAI-oriented CIEPT-R project described in `aaai项目.md`.

## Current Scope

The current milestone is intentionally narrow:

- create a Python research repository skeleton
- persist agent workflow and task state under `continue/`
- provide a minimal config loader, data protocol, priors, transport sanity checks, a torch reranker skeleton, intervention utilities, and conflict-stress protocol tooling
- make bootstrap verification reproducible

This repository does **not** yet implement dataset preprocessing, partial transport, training, or audited evaluation.

## Repository Layout

- `aaai项目.md`: original research framing
- `configs/`: project configuration files
- `continue/`: persistent agent instructions, tasks, and progress logs
- `docs/superpowers/`: design and implementation plans
- `data/`: raw/interim/processed dataset layout and processed artifacts
- `scripts/`: verification scripts
- `src/ciept/`: Python package bootstrap
- `tests/`: bootstrap tests

## Bootstrap Workflow

Future agent sessions should:

1. read `continue/AGENT.MD`
2. inspect `continue/task.json`
3. pick exactly one ready task
4. implement with verification evidence
5. update `continue/progress.md`
6. commit the completed task once

## Data Protocol

`T002` establishes the initial offline data contract:

- source downloads live under `data/raw/`
- temporary preprocessing artifacts live under `data/interim/`
- reproducible split outputs live under `data/processed/`
- temporal splitting is global absolute-time `80/10/10`
- iterative k-core filtering happens before the split
- items with missing modalities are retained and recorded with explicit flags
- main training is transductive; cold-start is reported separately

Example preprocessing entrypoint:

```bash
PYTHONPATH=src python -m ciept.data.cli \
  --interactions data/raw/<dataset>/interactions.csv \
  --items data/raw/<dataset>/items.csv \
  --output-dir data/processed/<dataset> \
  --min-user-degree 5 \
  --min-item-degree 5
```

## Planned Next Tasks

- `T012`: experiment runners and result templates
- `T013`: final delivery artifacts and paper-facing exports

## Graph Layer

`T003` introduces a lightweight `src/ciept/graph/` package with:

- dataclass-based node and topology types
- strict block-diagonal topology builders for text and vision evidence
- JSON-friendly cache serialization helpers
- adapter placeholders for later tensor-backed tasks

The graph layer intentionally does not parse raw items or import `torch` yet.

## Prior Layer

`T004` adds a lightweight `src/ciept/priors/` package with:

- heuristic corroboration, stability, and vulnerability scoring
- interpretable reliability aggregation
- normalized capacity prior construction
- nuisance-mask inference with explicit-label precedence and heuristic fallback

This layer is intentionally metadata-driven and keeps learned heads out of scope.

## Transport Sanity Layer

`T005` adds a NumPy-based `src/ciept/transport/` toy solver for:

- partial mass-budget enforcement
- target-capacity enforcement
- explicit reject-mass reporting

It is intentionally a semantic sanity-check layer, not the final research solver.

## Reranker Layer

`T006` adds a torch-based reranker layer that introduces:

- pairwise feature-cost construction
- capacity-driven reliability penalties
- a torch partial-transport operator
- a scalar score derived from the transport plan

This is intentionally a minimal forward skeleton, not the final research solver.

## Intervention Layer

`T007` adds a lightweight `src/ciept/audit/` package with:

- capacity-normalized support
- support-to-logit conversion
- binary Gumbel/STE gating
- leakage-ratio diagnostics
- a single-pass intervention loss

This layer is intentionally modular and not yet wired into a full training loop.

## Conflict Stress Protocol

`T009` adds an offline conflict-stress pipeline that:

- generates positive-preserving nuisance and negative-preserving lure examples
- writes artifacts under `data/interim/`
- emits nuisance masks, protocol summaries, and review queues

This stays at the structured-node level and does not perform real image processing.

## Audit Dataset Protocol

`T010` adds an audit-set protocol that:

- builds `audit_examples.jsonl` from stress artifacts
- exports `vlm_requests.jsonl`
- merges external `vlm_predictions.jsonl` back into annotated records
- initializes `adjudication_queue.jsonl`

It stays provider-agnostic and file-based, so a concrete VLM can be plugged in later without rewriting the schema.

## Experiment Runner

`T012` adds a dispatcher-based `src/ciept/experiments/` package that:

- routes named experiments to dedicated modules
- writes `metrics.json` and `summary.md` under `results/<experiment>/<run_id>/`
- keeps toy/placeholder runs clearly labeled

It standardizes experiment outputs without pretending the current runs are real benchmark results.

## Metrics Layer

`T011` adds a reusable metrics package for:

- ranking metrics (`Recall@k`, `NDCG@k`, `MRR`)
- faithfulness metrics (`SufficiencyGap`, `ComprehensivenessGap`, `LeakageRatio`, `SupportPrecision/Recall/F1`)
- usage diagnostics (`Image Shuffle Drop`, `Random Caption Drop`, `Missing-Modality Drop`, `Transported Mass Ratio`)

It intentionally stops short of significance testing or experiment-runner orchestration.

## Conflict Stress Protocol

`T009` adds an offline conflict-stress pipeline that:

- generates positive-preserving nuisance and negative-preserving lure examples
- writes artifacts under `data/interim/`
- emits nuisance masks, protocol summaries, and review queues

This stays at the structured-node level and does not perform real image processing.

## Training Entrypoint

`T008` adds a minimal `src/ciept/train/` and `src/ciept/eval/` path that can:

- run one toy train step with `confidence-weighted ListMLE`
- add intervention loss on the positive path
- run one toy eval step with `Recall@1` and `MRR`
- expose both flows through `python -m ciept.train.cli --mode train|eval`

This is intentionally a toy executable path, not a full experiment framework.
