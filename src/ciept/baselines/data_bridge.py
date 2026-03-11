from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


REQUIRED_SPLITS = ("train", "valid", "test")
REQUIRED_INTERACTION_COLUMNS = ("user_id", "item_id")
REQUIRED_ITEM_COLUMNS = ("item_id",)


@dataclass(frozen=True)
class RecboleDatasetBridge:
    dataset_name: str
    source_dir: Path
    output_dir: Path
    benchmark_filename: list[str]
    manifest_path: Path
    item_file: Path | None


def _read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header: {path.name}")
        rows = list(reader)
    return list(reader.fieldnames), rows


def _validate_columns(path: Path, fieldnames: list[str], required: tuple[str, ...]) -> None:
    missing = [column for column in required if column not in fieldnames]
    if missing:
        raise ValueError(f"Missing required columns in {path.name}: {', '.join(missing)}")


def _is_float_like(value: str) -> bool:
    if value == "":
        return True
    try:
        float(value)
    except ValueError:
        return False
    return True


def _infer_atomic_type(column: str, values: list[str]) -> str:
    if column in {"user_id", "item_id"}:
        return "token"
    if column in {"rating", "timestamp"}:
        return "float"
    if values and all(_is_float_like(value) for value in values):
        return "float"
    return "token"


def _sanitize_value(value: object) -> str:
    return str(value).replace("\t", " ").replace("\n", " ").strip()


def _write_atomic_file(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    header = "\t".join(
        f"{field}:{_infer_atomic_type(field, [_sanitize_value(row.get(field, '')) for row in rows])}"
        for field in fieldnames
    )
    lines = [header]
    for row in rows:
        lines.append("\t".join(_sanitize_value(row.get(field, "")) for field in fieldnames))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def bridge_presplit_dataset_to_recbole(
    dataset_name: str,
    source_dir: Path,
    output_dir: Path,
) -> RecboleDatasetBridge:
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written_files: dict[str, str] = {}
    for split in REQUIRED_SPLITS:
        source_file = source_dir / f"{split}.csv"
        if not source_file.exists():
            raise ValueError(f"Missing required split file: {source_file.name}")
        fieldnames, rows = _read_csv_rows(source_file)
        _validate_columns(source_file, fieldnames, REQUIRED_INTERACTION_COLUMNS)
        target_file = output_dir / f"{dataset_name}.{split}.inter"
        _write_atomic_file(target_file, fieldnames, rows)
        written_files[split] = str(target_file)

    item_file: Path | None = None
    source_items = source_dir / "items.csv"
    if source_items.exists():
        item_fieldnames, item_rows = _read_csv_rows(source_items)
        _validate_columns(source_items, item_fieldnames, REQUIRED_ITEM_COLUMNS)
        item_file = output_dir / f"{dataset_name}.item"
        _write_atomic_file(item_file, item_fieldnames, item_rows)
        written_files["item"] = str(item_file)

    manifest_path = output_dir / "bridge_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "dataset_name": dataset_name,
                "source_dir": str(source_dir),
                "output_dir": str(output_dir),
                "benchmark_filename": list(REQUIRED_SPLITS),
                "written_files": written_files,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return RecboleDatasetBridge(
        dataset_name=dataset_name,
        source_dir=source_dir,
        output_dir=output_dir,
        benchmark_filename=list(REQUIRED_SPLITS),
        manifest_path=manifest_path,
        item_file=item_file,
    )
