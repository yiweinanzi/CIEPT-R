from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.graph.types import EvidenceNode, NodeModality


def test_evidence_node_keeps_text_and_vision_specific_fields():
    text_node = EvidenceNode(
        node_id="t1",
        modality=NodeModality.TEXT,
        source="title",
        content="breathable fabric",
        position=0,
        span=(0, 17),
        bbox=None,
        metadata={"field": "title"},
    )
    vision_node = EvidenceNode(
        node_id="v1",
        modality=NodeModality.VISION,
        source="image_region",
        content="front_upper_body",
        position=None,
        span=None,
        bbox=(0.1, 0.2, 0.4, 0.7),
        metadata={"region": "hero"},
    )

    assert text_node.modality is NodeModality.TEXT
    assert text_node.span == (0, 17)
    assert vision_node.modality is NodeModality.VISION
    assert vision_node.bbox == (0.1, 0.2, 0.4, 0.7)
