from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.data.protocol import (
    build_missing_modality_report,
    global_temporal_split,
    iterative_k_core,
)


def test_iterative_k_core_filters_until_stable():
    interactions = [
        {"user_id": "u1", "item_id": "i1", "timestamp": 1},
        {"user_id": "u1", "item_id": "i2", "timestamp": 2},
        {"user_id": "u2", "item_id": "i1", "timestamp": 3},
        {"user_id": "u3", "item_id": "i2", "timestamp": 4},
    ]

    filtered = iterative_k_core(interactions, min_user_degree=2, min_item_degree=2)

    assert filtered == []


def test_global_temporal_split_uses_absolute_time_order():
    interactions = [
        {"user_id": f"u{idx}", "item_id": f"i{idx}", "timestamp": timestamp}
        for idx, timestamp in enumerate([9, 1, 7, 3, 5, 11, 13, 15, 17, 19], start=1)
    ]

    train, valid, test = global_temporal_split(interactions)

    assert [row["timestamp"] for row in train] == [1, 3, 5, 7, 9, 11, 13, 15]
    assert [row["timestamp"] for row in valid] == [17]
    assert [row["timestamp"] for row in test] == [19]


def test_missing_modality_report_preserves_partial_items():
    items = [
        {"item_id": "i1", "has_text": "1", "has_image": "0", "has_ocr": "1"},
        {"item_id": "i2", "has_text": "1", "has_image": "1", "has_ocr": "0"},
    ]

    report = build_missing_modality_report(items)

    assert report["total_items"] == 2
    assert report["items_with_missing_modalities"] == 2
    assert report["missing_counts"]["image"] == 1
    assert report["missing_counts"]["ocr"] == 1
