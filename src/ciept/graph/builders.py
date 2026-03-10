from __future__ import annotations

from ciept.graph.types import EvidenceGraph, EvidenceNode, ItemTopologyCacheRecord, TopologyMatrix


def _validate_distance_matrix(
    distances: list[list[float]],
    expected_size: int,
    name: str,
) -> None:
    if expected_size == 0:
        if distances not in ([], ()):
            raise ValueError(f"{name} distance matrix must be empty when no nodes are provided")
        return

    if len(distances) != expected_size:
        raise ValueError(f"{name} distance matrix must match node count")

    for row in distances:
        if len(row) != expected_size:
            raise ValueError(f"{name} distance matrix must be square")


def _normalize_distance_matrix(distances: list[list[float]]) -> list[list[float]]:
    if not distances:
        return []

    max_value = max(max(row) for row in distances)
    if max_value <= 0:
        return [[float(value) for value in row] for row in distances]

    return [[float(value) / float(max_value) for value in row] for row in distances]


def build_block_diagonal_topology(
    text_nodes: list[EvidenceNode],
    text_distances: list[list[float]],
    vision_nodes: list[EvidenceNode],
    vision_distances: list[list[float]],
    cross_block_penalty: float = 1e4,
) -> TopologyMatrix:
    _validate_distance_matrix(text_distances, len(text_nodes), "text")
    _validate_distance_matrix(vision_distances, len(vision_nodes), "vision")

    norm_text = _normalize_distance_matrix(text_distances)
    norm_vision = _normalize_distance_matrix(vision_distances)

    all_nodes = text_nodes + vision_nodes
    node_ids = [node.node_id for node in all_nodes]
    size = len(all_nodes)
    values = [[0.0 for _ in range(size)] for _ in range(size)]

    for row_index, row in enumerate(norm_text):
        for col_index, value in enumerate(row):
            values[row_index][col_index] = value

    text_offset = len(text_nodes)
    for row_index, row in enumerate(norm_vision):
        for col_index, value in enumerate(row):
            values[text_offset + row_index][text_offset + col_index] = value

    for text_index in range(len(text_nodes)):
        for vision_index in range(len(vision_nodes)):
            global_vision_index = text_offset + vision_index
            values[text_index][global_vision_index] = cross_block_penalty
            values[global_vision_index][text_index] = cross_block_penalty

    return TopologyMatrix(
        node_ids=node_ids,
        values=values,
        block_labels=[node.modality.value for node in all_nodes],
        cross_block_penalty=float(cross_block_penalty),
    )


def build_item_evidence_graph(
    item_id: str,
    text_nodes: list[EvidenceNode],
    text_distances: list[list[float]],
    vision_nodes: list[EvidenceNode],
    vision_distances: list[list[float]],
    cross_block_penalty: float = 1e4,
) -> EvidenceGraph:
    all_nodes = text_nodes + vision_nodes
    node_ids = [node.node_id for node in all_nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("Duplicate node_id values are not allowed")

    topology = build_block_diagonal_topology(
        text_nodes=text_nodes,
        text_distances=text_distances,
        vision_nodes=vision_nodes,
        vision_distances=vision_distances,
        cross_block_penalty=cross_block_penalty,
    )

    return EvidenceGraph(
        item_id=item_id,
        text_nodes=list(text_nodes),
        vision_nodes=list(vision_nodes),
        all_nodes=list(all_nodes),
        topology=topology,
    )
