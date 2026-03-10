from __future__ import annotations

from ciept.graph.types import (
    EvidenceNode,
    ItemTopologyCacheRecord,
    NodeModality,
    TopologyMatrix,
)


def _node_to_dict(node: EvidenceNode) -> dict:
    return {
        "node_id": node.node_id,
        "modality": node.modality.value,
        "source": node.source,
        "content": node.content,
        "position": node.position,
        "span": list(node.span) if node.span is not None else None,
        "bbox": list(node.bbox) if node.bbox is not None else None,
        "metadata": dict(node.metadata),
    }


def _node_from_dict(payload: dict) -> EvidenceNode:
    span = payload.get("span")
    bbox = payload.get("bbox")
    return EvidenceNode(
        node_id=payload["node_id"],
        modality=NodeModality(payload["modality"]),
        source=payload["source"],
        content=payload["content"],
        position=payload.get("position"),
        span=tuple(span) if span is not None else None,
        bbox=tuple(bbox) if bbox is not None else None,
        metadata=dict(payload.get("metadata", {})),
    )


def cache_record_to_dict(record: ItemTopologyCacheRecord) -> dict:
    return {
        "item_id": record.item_id,
        "node_count": record.node_count,
        "modalities": dict(record.modalities),
        "topology": {
            "node_ids": list(record.topology.node_ids),
            "values": [list(row) for row in record.topology.values],
            "block_labels": list(record.topology.block_labels),
            "cross_block_penalty": record.topology.cross_block_penalty,
        },
        "node_payloads": [_node_to_dict(node) for node in record.node_payloads],
    }


def cache_record_from_dict(payload: dict) -> ItemTopologyCacheRecord:
    topology = payload["topology"]
    return ItemTopologyCacheRecord(
        item_id=payload["item_id"],
        node_count=payload["node_count"],
        modalities=dict(payload["modalities"]),
        topology=TopologyMatrix(
            node_ids=list(topology["node_ids"]),
            values=[list(row) for row in topology["values"]],
            block_labels=list(topology["block_labels"]),
            cross_block_penalty=float(topology["cross_block_penalty"]),
        ),
        node_payloads=[_node_from_dict(node) for node in payload["node_payloads"]],
    )
