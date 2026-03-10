# AAAI Research Bootstrap Design

## Context

This repository starts from `aaai项目.md`, but the immediate goal is not to build the full research pipeline. The first milestone is a stable research-engineering skeleton with persistent agent state so future sessions can resume from disk without losing project context.

## Goal

Create a lightweight Python research repository for the CIEPT-R project with:

- a minimal runnable package and CLI
- configuration loading
- a test and verification entrypoint
- persistent workflow state under `continue/`

## Scope

### In scope

- repository bootstrap for Python-based experiments
- `continue/AGENT.MD`, `continue/task.json`, `continue/progress.md`
- a small `src/ciept/` package
- base configuration in `configs/`
- basic tests and a single verification script
- documentation describing how to continue the work

### Out of scope

- real dataset integration
- OT solver implementation
- training loop
- evaluation pipeline beyond bootstrap validation

## Repository Structure

The repository will use this top-level layout:

- `README.md`: project intent, current scope, next milestones
- `aaai项目.md`: original research notes kept as the source concept
- `configs/`: experiment and environment configuration
- `src/ciept/`: Python package for future graph, transport, audit, and training code
- `scripts/`: shell utilities for verification
- `tests/`: pytest coverage for bootstrap behavior
- `continue/`: persistent execution instructions, task state, and progress log
- `docs/superpowers/`: design and implementation planning artifacts

## Persistent Workflow Design

### `continue/AGENT.MD`

Defines the mandatory workflow for every future agent session:

1. read `continue/task.json`
2. select exactly one ready task
3. verify requirements before implementation
4. implement and validate the task
5. update `continue/progress.md`
6. update `continue/task.json`
7. commit the task as one coherent unit

It also defines blocked-task behavior so unfinished work is never marked complete.

### `continue/task.json`

Acts as the source of truth for task state. Each task stores:

- `id`
- `title`
- `status`
- `priority`
- `depends_on`
- `summary`
- `acceptance_criteria`
- `artifacts`
- `notes`

Status values are fixed to `pending`, `in_progress`, `blocked`, and `done`.

### `continue/progress.md`

Stores short session logs with:

- timestamp
- task id and objective
- implemented changes
- verification commands and results
- risks or next actions

## Initial Delivery: Task T001

The first implementation task is `T001: 工程初始化与配置校验`.

### Acceptance criteria

- a Python package exists under `src/ciept/`
- a CLI can load and print a base config
- a config file exists in `configs/base.yaml`
- pytest-based checks exist and pass
- `scripts/check.sh` runs the project verification
- persistent workflow files in `continue/` are present and updated

## Validation Strategy

The bootstrap is complete only if verification is reproducible from commands recorded in the repository. The initial validation surface is intentionally small:

- `pytest`
- `bash scripts/check.sh`

## Follow-on Tasks

After bootstrap, the next tasks should focus on:

1. data directory conventions and dataset sanity checks
2. evidence graph and topology cache interfaces
3. toy partial transport numeric sanity checks
4. training and evaluation entrypoints
