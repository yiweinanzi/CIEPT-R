# CIEPT-R Bootstrap Repository

This repository bootstraps the engineering workspace for the AAAI-oriented CIEPT-R project described in `aaai项目.md`.

## Current Scope

The current milestone is intentionally narrow:

- create a Python research repository skeleton
- persist agent workflow and task state under `continue/`
- provide a minimal config loader, data protocol, and CLI tools
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

- `T003`: evidence graph and topology cache interfaces
- `T004`: reliability prior, capacity prior, and nuisance mask interfaces
- `T005`: toy partial transport sanity check

## Graph Layer

`T003` introduces a lightweight `src/ciept/graph/` package with:

- dataclass-based node and topology types
- strict block-diagonal topology builders for text and vision evidence
- JSON-friendly cache serialization helpers
- adapter placeholders for later tensor-backed tasks

The graph layer intentionally does not parse raw items or import `torch` yet.
