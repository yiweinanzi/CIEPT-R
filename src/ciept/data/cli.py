from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from ciept.data.protocol import (
    build_missing_modality_report,
    global_temporal_split,
    iterative_k_core,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare dataset splits for CIEPT-R")
    parser.add_argument("--interactions", required=True, help="Path to interactions CSV")
    parser.add_argument("--items", required=True, help="Path to item metadata CSV")
    parser.add_argument("--output-dir", required=True, help="Directory for processed outputs")
    parser.add_argument("--min-user-degree", type=int, default=5, help="Minimum user degree")
    parser.add_argument("--min-item-degree", type=int, default=5, help="Minimum item degree")
    return parser


def read_csv_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = ["user_id", "item_id", "timestamp"]

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = build_parser().parse_args()

    interactions = read_csv_rows(Path(args.interactions))
    items = read_csv_rows(Path(args.items))

    filtered = iterative_k_core(
        interactions,
        min_user_degree=args.min_user_degree,
        min_item_degree=args.min_item_degree,
    )
    train, valid, test = global_temporal_split(filtered)

    kept_item_ids = {row["item_id"] for row in filtered}
    filtered_items = [item for item in items if item["item_id"] in kept_item_ids]
    missing_modality = build_missing_modality_report(filtered_items)

    output_dir = Path(args.output_dir)
    write_csv_rows(output_dir / "train.csv", train)
    write_csv_rows(output_dir / "valid.csv", valid)
    write_csv_rows(output_dir / "test.csv", test)

    summary = {
        "protocol": {
            "split_strategy": "global_temporal_80_10_10",
            "k_core": {
                "min_user_degree": args.min_user_degree,
                "min_item_degree": args.min_item_degree,
            },
            "setting": "transductive",
            "cold_start_policy": "report_separately",
            "missing_modality_policy": "retain_items_with_explicit_mask",
        },
        "counts": {
            "interactions_before_k_core": len(interactions),
            "interactions_after_k_core": len(filtered),
            "items_after_interaction_filter": len(filtered_items),
        },
        "split_counts": {
            "train": len(train),
            "valid": len(valid),
            "test": len(test),
        },
        "missing_modality": missing_modality,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "protocol_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(summary["split_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
