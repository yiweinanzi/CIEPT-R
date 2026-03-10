# Graph Topology Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `T003` by adding dataclass-based evidence graph interfaces, strict block-diagonal topology builders, and JSON-friendly cache serialization.

**Architecture:** Add a focused `ciept.graph` package split by responsibility: types, builders, cache, and adapter placeholders. Keep the public interface standard-library-only so later tensor logic can attach through adapters without contaminating the graph boundary.

**Tech Stack:** Python 3.10, dataclasses, enum, json-friendly dict serialization, pytest

---

## Chunk 1: Graph Types And Builders

### Task 1: Add failing tests for graph types and block-diagonal topology behavior

**Files:**
- Create: `tests/test_graph_types.py`
- Create: `tests/test_graph_builders.py`
- Reference: `docs/superpowers/specs/2026-03-10-graph-topology-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.graph.types import EvidenceNode, NodeModality


def test_evidence_node_keeps_text_and_vision_specific_fields():
    text_node = EvidenceNode(...)
    vision_node = EvidenceNode(...)
    assert text_node.modality is NodeModality.TEXT
    assert vision_node.modality is NodeModality.VISION
```

```python
from ciept.graph.builders import build_block_diagonal_topology


def test_block_diagonal_topology_uses_cross_block_penalty():
    topology = build_block_diagonal_topology(...)
    assert topology.values[0][2] == 1e4
```

```python
def test_builder_rejects_duplicate_node_ids():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_types.py tests/test_graph_builders.py -v`
Expected: FAIL because `ciept.graph` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/graph/__init__.py`
- `src/ciept/graph/types.py`
- `src/ciept/graph/builders.py`
- `src/ciept/graph/adapters.py`

Implementation requirements:

- `NodeModality` supports `TEXT` and `VISION`
- `EvidenceNode`, `TopologyMatrix`, `EvidenceGraph`, and `ItemTopologyCacheRecord` are dataclasses
- `build_block_diagonal_topology()` validates matrix shapes and assembles a strict block-diagonal matrix
- `build_item_evidence_graph()` validates unique node ids and returns an `EvidenceGraph`
- `adapters.py` contains placeholder hooks only and does not import `torch`

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_graph_types.py tests/test_graph_builders.py -v`
Expected: PASS

- [ ] **Step 5: Leave changes uncommitted for the single-task final commit**

Record progress locally, but do not create a commit yet. `T003` should be committed once after final verification.

## Chunk 2: Cache Serialization And Task Completion

### Task 2: Add failing tests for cache round-trip and persistent task state

**Files:**
- Create: `tests/test_graph_cache.py`
- Modify: `tests/test_persistence.py`
- Modify: `continue/task.json`
- Modify: `continue/progress.md`
- Modify: `README.md`
- Reference: `docs/superpowers/specs/2026-03-10-graph-topology-design.md`

- [ ] **Step 1: Write the failing test**

```python
from ciept.graph.cache import cache_record_from_dict, cache_record_to_dict


def test_cache_record_round_trips_through_dict():
    record = ...
    payload = cache_record_to_dict(record)
    restored = cache_record_from_dict(payload)
    assert restored.item_id == record.item_id
```

```python
def test_t003_marked_done_and_t004_selected_next():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_graph_cache.py tests/test_persistence.py::test_t003_marked_done_and_t004_selected_next -v`
Expected: FAIL because cache helpers and the completed `T003` state do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create:

- `src/ciept/graph/cache.py`

Update:

- `README.md` with graph module layout
- `continue/task.json` to mark `T003` done and `T004` current
- `continue/progress.md` with a verification-backed `T003` entry

Implementation requirements:

- cache helpers serialize dataclasses into JSON-friendly dictionaries
- round-trip preserves topology payloads and node ordering
- README only gets minimal graph-layer notes

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`
Expected: PASS with all repository tests green.

- [ ] **Step 5: Commit**

```bash
git add README.md continue/task.json continue/progress.md docs/superpowers/plans/2026-03-10-graph-topology.md src/ciept/graph/__init__.py src/ciept/graph/types.py src/ciept/graph/builders.py src/ciept/graph/cache.py src/ciept/graph/adapters.py tests/test_graph_types.py tests/test_graph_builders.py tests/test_graph_cache.py tests/test_persistence.py
git commit -m "feat: complete graph topology task T003"
```
