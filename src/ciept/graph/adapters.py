"""Tensor-friendly views over graph dataclasses."""

from __future__ import annotations

import torch

from ciept.graph.types import EvidenceGraph, NodeModality


def to_tensor_views(graph: EvidenceGraph) -> dict:
    modality_ids = torch.tensor(
        [0 if node.modality is NodeModality.TEXT else 1 for node in graph.all_nodes],
        dtype=torch.long,
    )
    topology = torch.tensor(graph.topology.values, dtype=torch.float32)
    text_mask = modality_ids == 0
    vision_mask = modality_ids == 1

    return {
        "node_ids": list(graph.topology.node_ids),
        "modality_ids": modality_ids,
        "topology": topology,
        "text_mask": text_mask,
        "vision_mask": vision_mask,
    }
