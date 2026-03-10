from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.graph.builders import build_block_diagonal_topology, build_item_evidence_graph
from ciept.graph.types import EvidenceNode, NodeModality


def make_text_node(node_id: str, position: int) -> EvidenceNode:
    return EvidenceNode(
        node_id=node_id,
        modality=NodeModality.TEXT,
        source="title",
        content=f"text-{node_id}",
        position=position,
        span=(position, position + 1),
        bbox=None,
        metadata={},
    )


def make_vision_node(node_id: str) -> EvidenceNode:
    return EvidenceNode(
        node_id=node_id,
        modality=NodeModality.VISION,
        source="image_region",
        content=f"vision-{node_id}",
        position=None,
        span=None,
        bbox=(0.0, 0.0, 1.0, 1.0),
        metadata={},
    )


def test_block_diagonal_topology_uses_cross_block_penalty():
    topology = build_block_diagonal_topology(
        text_nodes=[make_text_node("t1", 0), make_text_node("t2", 1)],
        text_distances=[[0.0, 2.0], [2.0, 0.0]],
        vision_nodes=[make_vision_node("v1")],
        vision_distances=[[0.0]],
        cross_block_penalty=1e4,
    )

    assert topology.node_ids == ["t1", "t2", "v1"]
    assert topology.values[0][2] == 1e4
    assert topology.values[2][0] == 1e4
    assert topology.values[0][1] == 1.0
    assert topology.values[2][2] == 0.0


def test_builder_rejects_duplicate_node_ids():
    text_node = make_text_node("dup", 0)
    vision_node = make_vision_node("dup")

    with pytest.raises(ValueError, match="Duplicate node_id"):
        build_item_evidence_graph(
            item_id="item-1",
            text_nodes=[text_node],
            text_distances=[[0.0]],
            vision_nodes=[vision_node],
            vision_distances=[[0.0]],
        )


def test_builder_rejects_invalid_distance_shape():
    with pytest.raises(ValueError, match="square"):
        build_block_diagonal_topology(
            text_nodes=[make_text_node("t1", 0), make_text_node("t2", 1)],
            text_distances=[[0.0], [1.0, 0.0]],
            vision_nodes=[],
            vision_distances=[],
            cross_block_penalty=1e4,
        )
