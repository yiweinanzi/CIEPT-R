# Evidence Graph And Block-Diagonal Topology Design

## Context

`T003` is the first structure-focused task after repository bootstrap and data protocol setup. The repository now has a stable Python package, offline split protocol, and persistent workflow state. The next step is to define item-side evidence graph interfaces that later tasks can use for reliability priors, partial transport, and audited intervention.

The goal of this task is not to implement parsing or transport computation. The goal is to lock down clean, testable interfaces for evidence nodes, block-diagonal topologies, and cache records.

## Goal

Create a `ciept.graph` package that:

- defines stable dataclass-based graph interfaces
- builds strict block-diagonal topology matrices for text and vision evidence
- serializes cache records in JSON-friendly structures
- stays independent from `torch` at this stage

## Scope

### In scope

- graph-facing enums and dataclasses
- block-diagonal topology builder
- item evidence graph assembler
- cache record serialization and deserialization
- tests for structural correctness and invalid input handling

### Out of scope

- raw item parsing from Amazon metadata
- embedding generation
- reliability, capacity prior, or nuisance mask logic
- tensor conversion implementation
- transport solver integration

## Design Decisions

### 1. Dataclass-first boundary

The public boundary will use `dataclass` objects and standard-library containers instead of `torch.Tensor`. This keeps `T003` focused on interface clarity and avoids prematurely locking the graph layer to tensor shape, device, or dtype decisions.

Later tasks may add tensor adapters, but `T003` should remain framework-light.

### 2. OCR stays text-side for now

`NodeModality` will initially support only:

- `text`
- `vision`

OCR-derived evidence stays in the text-side branch for now. This preserves the paper’s key text-vs-vision topology boundary without creating a third modality before the downstream transport interfaces are ready.

### 3. Strict block-diagonal topology

The item topology matrix is assembled from:

- a normalized text-text submatrix
- a normalized vision-vision submatrix
- a fixed cross-block penalty for text-vision and vision-text entries

Cross-modal entries do not represent geometry. They exist only as a hard structural penalty.

### 4. Builder responsibilities stay narrow

`build_item_evidence_graph()` will only combine already-formed nodes and already-available within-modality distance matrices. Parsing titles, metadata, OCR, image regions, or learned features is explicitly deferred.

### 5. Cache records stay JSON-friendly

Cache records should round-trip to ordinary dictionaries so they can later be written as JSON, JSONL, or lightweight metadata files. No binary serialization is required in `T003`.

## Proposed Module Layout

- `src/ciept/graph/types.py`
  - `NodeModality`
  - `EvidenceNode`
  - `TopologyMatrix`
  - `EvidenceGraph`
  - `ItemTopologyCacheRecord`

- `src/ciept/graph/builders.py`
  - `build_block_diagonal_topology()`
  - `build_item_evidence_graph()`

- `src/ciept/graph/cache.py`
  - `cache_record_to_dict()`
  - `cache_record_from_dict()`

- `src/ciept/graph/adapters.py`
  - placeholder tensor-adapter hooks for later tasks

## Data Structures

### `EvidenceNode`

Fields:

- `node_id: str`
- `modality: NodeModality`
- `source: str`
- `content: str`
- `position: int | None`
- `span: tuple[int, int] | None`
- `bbox: tuple[float, float, float, float] | None`
- `metadata: dict[str, str]`

Conventions:

- text nodes primarily use `position` and `span`
- vision nodes primarily use `bbox`
- `metadata` is lightweight and string-keyed

### `TopologyMatrix`

Fields:

- `node_ids: list[str]`
- `values: list[list[float]]`
- `block_labels: list[str]`
- `cross_block_penalty: float`

Semantics:

- text-text entries store normalized text distances
- vision-vision entries store normalized visual distances
- cross-block entries are fixed to the configured penalty

### `EvidenceGraph`

Fields:

- `item_id: str`
- `text_nodes: list[EvidenceNode]`
- `vision_nodes: list[EvidenceNode]`
- `all_nodes: list[EvidenceNode]`
- `topology: TopologyMatrix`

### `ItemTopologyCacheRecord`

Fields:

- `item_id: str`
- `node_count: int`
- `modalities: dict[str, int]`
- `topology: TopologyMatrix`
- `node_payloads: list[EvidenceNode]`

## Validation Rules

The builder layer should fail fast with `ValueError` when:

- a modality-specific distance matrix is not square
- a modality-specific distance matrix size does not match node count
- duplicate `node_id` values are provided
- a distance matrix contains rows with inconsistent lengths

The builder should not silently repair malformed inputs.

## Testing Strategy

Tests will cover:

- dataclass construction and invariants
- strict block-diagonal assembly
- duplicate-node and size-mismatch failures
- cache record round-trip to dictionary form

Tests will not cover:

- raw parsing
- feature encoding
- tensor conversion
- reliability or transport logic

## Follow-on Integration

This design supports later tasks by providing:

- stable evidence-node and topology interfaces for `T004`
- a cache record shape that can later hold reliability and capacity payloads
- an adapter boundary where `torch` conversion can be added without rewriting the graph model
