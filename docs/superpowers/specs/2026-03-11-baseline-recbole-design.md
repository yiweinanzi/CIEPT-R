# Baseline Inventory And RecBole Bootstrap Design

## Context

The core repository code has reached a handoff-ready state, but external baseline integration has not started. The user has now downloaded a set of baseline resources under `baselines/` and wants them brought into the task system one by one, with RecBole considered as an auxiliary framework.

The immediate goal is not to run all baselines. The immediate goal is to:

- inventory what has actually been downloaded
- classify direct matches, mapped candidates, and missing baselines
- introduce a RecBole-oriented adapter layer for later baseline/evaluation work
- add baseline tasks into the persistent task system

## Goal

Create a baseline inventory and RecBole bootstrap layer that records downloaded baselines, maps them to project expectations, and prepares a clean path for future one-by-one baseline integration.

## Scope

### In scope

- baseline registry and inventory classification
- RecBole availability/config adapter
- baseline-related task additions to `continue/task.json`
- README notes on baseline integration strategy

### Out of scope

- running real baseline training
- integrating every baseline repository immediately
- real dataset wiring into RecBole
- changing the core `ciept` method implementation to depend on RecBole

## Design Decisions

### 1. Treat baseline integration as its own task track

Baseline integration should not be stuffed into the existing `T00x` research-implementation tasks. It should become its own sequence of tasks so the repository can track:

- inventory/bootstrap work
- RecBole alignment
- per-baseline integration
- missing-resource follow-up

### 2. Use RecBole as an auxiliary framework, not as the research core

RecBole is helpful for:

- reading presplit datasets
- evaluation protocol alignment
- baseline comparability

RecBole should not absorb the custom graph/prior/transport/intervention stack under `src/ciept/`.

### 3. Separate direct matches from manual mapping candidates

The downloaded baselines do not perfectly align with the paper list. The repository should explicitly distinguish:

- direct matches to planned baselines
- downloaded candidates that need manual mapping
- expected baselines still missing

This prevents accidental overclaiming.

## Proposed Module Layout

- `src/ciept/baselines/registry.py`
  - baseline metadata definitions
  - inventory classification from `baselines/`

- `src/ciept/baselines/recbole_adapter.py`
  - RecBole availability check
  - shared RecBole config construction
  - helper objects for future baseline runners

- `src/ciept/baselines/__init__.py`
  - narrow public surface for inventory/bootstrap work

- `configs/baselines/recbole_base.yaml`
  - stable RecBole-aligned defaults for later tasks

## Baseline Classification Policy

### Direct matches

Current downloaded assets that directly map to planned baselines:

- LightGCN
- VBPR
- BM3
- MGCN
- I3-MRec
- CLEAR
- Graph-Missing-Modalities-TKDE → Training-free Graph-based Imputation

### Mapped candidates

Downloaded assets that are present but need manual mapping or later judgment:

- DiffMM
- Guider
- MAGNET
- MixRec
- SMORE

### Missing

Planned baselines not yet seen locally:

- RecGOAT
- IGDMRec
- Modality-Guided Mixture of Graph Experts
- Teach Me How to Denoise

## RecBole Adapter Role

The RecBole adapter should support:

- availability detection
- shared config generation for presplit data
- storing baseline-oriented config decisions

It should not yet:

- import or wrap every external baseline repository
- run benchmark jobs

## Task-System Changes

Add a baseline task track to `continue/task.json`, beginning with:

- `B001`: Baseline inventory and mapping bootstrap
- `B002`: RecBole auxiliary layer and dataset bridge
- `B003` onward: one task per baseline integration

This task (`B001`) should finish once the inventory, registry, adapter bootstrap, and task additions are in place.

## Validation Rules

The inventory should fail fast for malformed or duplicate baseline records, but tolerate absent baseline archives by marking them as missing instead of crashing.

The RecBole adapter should tolerate RecBole not being installed yet by reporting unavailability rather than throwing import-time failures.

## Testing Strategy

Tests will verify:

- downloaded assets are classified correctly
- missing baselines are still represented in the registry
- RecBole config generation is stable
- baseline task entries are added to the task system

Tests will not verify:

- actual baseline execution
- real dataset integration
- RecBole runtime behavior

## Follow-on Integration

This design gives the next baseline tasks:

- a stable inventory source
- a RecBole-aligned configuration path
- an explicit per-baseline integration queue
