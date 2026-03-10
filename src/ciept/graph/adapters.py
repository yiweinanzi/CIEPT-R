"""Adapter hooks for later tensor-backed implementations."""

from __future__ import annotations

from ciept.graph.types import EvidenceGraph


def to_tensor_views(graph: EvidenceGraph) -> dict:
    """Placeholder for future tensor conversion logic."""

    raise NotImplementedError("Tensor adapters are deferred until a later task")
