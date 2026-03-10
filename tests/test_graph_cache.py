from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.graph.cache import cache_record_from_dict, cache_record_to_dict
from ciept.graph.types import (
    EvidenceNode,
    ItemTopologyCacheRecord,
    NodeModality,
    TopologyMatrix,
)


def test_cache_record_round_trips_through_dict():
    record = ItemTopologyCacheRecord(
        item_id="item-1",
        node_count=2,
        modalities={"text": 1, "vision": 1},
        topology=TopologyMatrix(
            node_ids=["t1", "v1"],
            values=[[0.0, 10000.0], [10000.0, 0.0]],
            block_labels=["text", "vision"],
            cross_block_penalty=10000.0,
        ),
        node_payloads=[
            EvidenceNode(
                node_id="t1",
                modality=NodeModality.TEXT,
                source="title",
                content="lightweight jacket",
                position=0,
                span=(0, 18),
                bbox=None,
                metadata={"field": "title"},
            ),
            EvidenceNode(
                node_id="v1",
                modality=NodeModality.VISION,
                source="image_region",
                content="front_view",
                position=None,
                span=None,
                bbox=(0.0, 0.0, 1.0, 1.0),
                metadata={"region": "hero"},
            ),
        ],
    )

    payload = cache_record_to_dict(record)
    restored = cache_record_from_dict(payload)

    assert restored.item_id == record.item_id
    assert restored.node_count == 2
    assert restored.modalities == {"text": 1, "vision": 1}
    assert restored.topology.values == [[0.0, 10000.0], [10000.0, 0.0]]
    assert [node.node_id for node in restored.node_payloads] == ["t1", "v1"]
