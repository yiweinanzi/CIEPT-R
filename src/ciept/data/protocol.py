from __future__ import annotations

from collections import Counter


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _as_int(value: object) -> int:
    return int(str(value))


def iterative_k_core(
    interactions: list[dict],
    min_user_degree: int = 5,
    min_item_degree: int = 5,
) -> list[dict]:
    filtered = list(interactions)

    while True:
        user_counts = Counter(row["user_id"] for row in filtered)
        item_counts = Counter(row["item_id"] for row in filtered)

        next_filtered = [
            row
            for row in filtered
            if user_counts[row["user_id"]] >= min_user_degree
            and item_counts[row["item_id"]] >= min_item_degree
        ]

        if len(next_filtered) == len(filtered):
            return next_filtered

        filtered = next_filtered


def global_temporal_split(
    interactions: list[dict],
    train_ratio: float = 0.8,
    valid_ratio: float = 0.1,
) -> tuple[list[dict], list[dict], list[dict]]:
    ordered = sorted(interactions, key=lambda row: _as_int(row["timestamp"]))
    total = len(ordered)
    train_end = int(total * train_ratio)
    valid_end = int(total * (train_ratio + valid_ratio))

    train = ordered[:train_end]
    valid = ordered[train_end:valid_end]
    test = ordered[valid_end:]
    return train, valid, test


def build_missing_modality_report(items: list[dict]) -> dict:
    missing_counts = {
        "text": 0,
        "image": 0,
        "ocr": 0,
    }

    for item in items:
        if not _as_bool(item.get("has_text", False)):
            missing_counts["text"] += 1
        if not _as_bool(item.get("has_image", False)):
            missing_counts["image"] += 1
        if not _as_bool(item.get("has_ocr", False)):
            missing_counts["ocr"] += 1

    total_items = len(items)
    items_with_missing_modalities = sum(
        1
        for item in items
        if not _as_bool(item.get("has_text", False))
        or not _as_bool(item.get("has_image", False))
        or not _as_bool(item.get("has_ocr", False))
    )

    return {
        "total_items": total_items,
        "items_with_missing_modalities": items_with_missing_modalities,
        "missing_counts": missing_counts,
    }
