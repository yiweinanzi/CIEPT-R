from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.graph.adapters import to_tensor_views
from ciept.graph.builders import build_item_evidence_graph
from ciept.graph.types import EvidenceNode, NodeModality


def test_to_tensor_views_exports_node_and_topology_tensors():
    graph = build_item_evidence_graph(
        item_id="item-1",
        text_nodes=[
            EvidenceNode(
                node_id="t1",
                modality=NodeModality.TEXT,
                source="title",
                content="running shoes",
                position=0,
                span=(0, 13),
                bbox=None,
                metadata={},
            )
        ],
        text_distances=[[0.0]],
        vision_nodes=[
            EvidenceNode(
                node_id="v1",
                modality=NodeModality.VISION,
                source="image_region",
                content="foreground product",
                position=None,
                span=None,
                bbox=(0.0, 0.0, 1.0, 1.0),
                metadata={},
            )
        ],
        vision_distances=[[0.0]],
    )

    views = to_tensor_views(graph)

    assert isinstance(views["topology"], torch.Tensor)
    assert views["topology"].shape == (2, 2)
    assert views["modality_ids"].tolist() == [0, 1]
    assert views["node_ids"] == ["t1", "v1"]
