# CIEPT-R Bootstrap Repository

This repository bootstraps the engineering workspace for the AAAI-oriented CIEPT-R project described in `aaai项目.md`.

## Current Scope

The current milestone is intentionally narrow:

- create a Python research repository skeleton
- persist agent workflow and task state under `continue/`
- provide a minimal config loader and CLI
- make bootstrap verification reproducible

This repository does **not** yet implement dataset preprocessing, partial transport, training, or audited evaluation.

## Repository Layout

- `aaai项目.md`: original research framing
- `configs/`: project configuration files
- `continue/`: persistent agent instructions, tasks, and progress logs
- `docs/superpowers/`: design and implementation plans
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

## Planned Next Tasks

- `T002`: data directory conventions and dataset sanity checks
- `T003`: evidence graph and topology cache interfaces
- `T004`: toy partial transport sanity check
- `T005`: training and evaluation entrypoints
