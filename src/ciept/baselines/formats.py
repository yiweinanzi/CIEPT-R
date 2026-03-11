from __future__ import annotations

import csv
import json
import pickle
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import sparse


REQUIRED_SPLITS = ("train", "valid", "test")
REQUIRED_COLUMNS = ("user_id", "item_id")
SPLIT_TO_LABEL = {"train": 0, "valid": 1, "test": 2}


@dataclass(frozen=True)
class PreparedBaselineDataset:
    dataset_name: str
    dataset_format: str
    source_dir: Path
    output_dir: Path
    manifest_path: Path
    metadata: dict[str, object] = field(default_factory=dict)


def _read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header: {path.name}")
        rows = list(reader)
    return list(reader.fieldnames), rows


def _validate_presplit_source(source_dir: Path) -> dict[str, list[dict[str, str]]]:
    source_dir = Path(source_dir)
    split_rows: dict[str, list[dict[str, str]]] = {}
    for split in REQUIRED_SPLITS:
        source_file = source_dir / f"{split}.csv"
        if not source_file.exists():
            raise ValueError(f"Missing required split file: {source_file.name}")
        fieldnames, rows = _read_csv_rows(source_file)
        missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns in {source_file.name}: {', '.join(missing)}")
        split_rows[split] = rows
    return split_rows


def _read_items_rows(source_dir: Path) -> list[dict[str, str]]:
    items_file = Path(source_dir) / "items.csv"
    if not items_file.exists():
        return []
    _, rows = _read_csv_rows(items_file)
    return rows


def _build_id_maps(split_rows: dict[str, list[dict[str, str]]]) -> tuple[dict[str, int], dict[str, int]]:
    user_ids = sorted({row["user_id"] for rows in split_rows.values() for row in rows})
    item_ids = sorted({row["item_id"] for rows in split_rows.values() for row in rows})
    return (
        {user_id: idx for idx, user_id in enumerate(user_ids)},
        {item_id: idx for idx, item_id in enumerate(item_ids)},
    )


def _stable_seed(value: str, salt: str) -> int:
    return sum((index + 1) * ord(char) for index, char in enumerate(f"{salt}:{value}")) % (2**32)


def _deterministic_feature_matrix(item_ids: list[str], dim: int, salt: str) -> np.ndarray:
    matrix = np.zeros((len(item_ids), dim), dtype=np.float32)
    for row_idx, item_id in enumerate(item_ids):
        rng = np.random.default_rng(_stable_seed(item_id, salt))
        matrix[row_idx] = rng.normal(loc=0.0, scale=1.0, size=dim).astype(np.float32)
    return matrix


def _write_manifest(
    output_dir: Path,
    dataset_name: str,
    dataset_format: str,
    metadata: dict[str, object],
) -> Path:
    manifest_path = output_dir / "format_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "dataset_name": dataset_name,
                "dataset_format": dataset_format,
                "output_dir": str(output_dir),
                "metadata": metadata,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return manifest_path


def prepare_mmrec_dataset(
    dataset_name: str,
    source_dir: Path,
    output_dir: Path,
    image_dim: int = 8,
    text_dim: int = 8,
) -> PreparedBaselineDataset:
    split_rows = _validate_presplit_source(source_dir)
    user_map, item_map = _build_id_maps(split_rows)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inter_path = output_dir / f"{dataset_name}.inter"
    lines = ["userID\titemID\tx_label"]
    for split in REQUIRED_SPLITS:
        for row in split_rows[split]:
            lines.append(f"{user_map[row['user_id']]}\t{item_map[row['item_id']]}\t{SPLIT_TO_LABEL[split]}")
    inter_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    item_ids = [item_id for item_id, _ in sorted(item_map.items(), key=lambda item: item[1])]
    np.save(output_dir / "image_feat.npy", _deterministic_feature_matrix(item_ids, image_dim, "image"))
    np.save(output_dir / "text_feat.npy", _deterministic_feature_matrix(item_ids, text_dim, "text"))

    metadata = {
        "inter_file_name": inter_path.name,
        "image_feature_file": "image_feat.npy",
        "text_feature_file": "text_feat.npy",
        "user_count": len(user_map),
        "item_count": len(item_map),
        "items_present": bool(_read_items_rows(source_dir)),
    }
    manifest_path = _write_manifest(output_dir, dataset_name, "mmrec", metadata)
    return PreparedBaselineDataset(
        dataset_name=dataset_name,
        dataset_format="mmrec",
        source_dir=Path(source_dir),
        output_dir=output_dir,
        manifest_path=manifest_path,
        metadata=metadata,
    )


def prepare_vbpr_dataset(
    dataset_name: str,
    source_dir: Path,
    output_dir: Path,
    visual_dim: int = 8,
) -> PreparedBaselineDataset:
    split_rows = _validate_presplit_source(source_dir)
    user_map, item_map = _build_id_maps(split_rows)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    interactions_path = output_dir / "interactions.csv"
    with interactions_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["user_idx", "item_idx", "split"])
        for split in REQUIRED_SPLITS:
            for row in split_rows[split]:
                writer.writerow([user_map[row["user_id"]], item_map[row["item_id"]], split])

    item_ids = [item_id for item_id, _ in sorted(item_map.items(), key=lambda item: item[1])]
    visual_features = _deterministic_feature_matrix(item_ids, visual_dim, "vbpr")
    np.save(output_dir / "visual_features.npy", visual_features)

    metadata = {
        "interactions_file": interactions_path.name,
        "visual_features_file": "visual_features.npy",
        "user_count": len(user_map),
        "item_count": len(item_map),
    }
    manifest_path = _write_manifest(output_dir, dataset_name, "vbpr", metadata)
    return PreparedBaselineDataset(
        dataset_name=dataset_name,
        dataset_format="vbpr",
        source_dir=Path(source_dir),
        output_dir=output_dir,
        manifest_path=manifest_path,
        metadata=metadata,
    )


def prepare_i3mrec_dataset(
    dataset_name: str,
    source_dir: Path,
    output_dir: Path,
    image_dim: int = 8,
    text_dim: int = 8,
) -> PreparedBaselineDataset:
    prepared = prepare_mmrec_dataset(dataset_name, source_dir, output_dir, image_dim=image_dim, text_dim=text_dim)
    inter_file = prepared.output_dir / f"{dataset_name}.inter"
    image_feat = np.load(prepared.output_dir / "image_feat.npy")
    text_feat = np.load(prepared.output_dir / "text_feat.npy")

    for name, payload in {
        "image_feat_missing_test.npy": image_feat,
        "text_feat_missing_test.npy": text_feat,
        "image_feat_missing_moD3.npy": image_feat,
        "text_feat_missing_moD3.npy": text_feat,
    }.items():
        np.save(prepared.output_dir / name, payload)

    metadata = dict(prepared.metadata)
    metadata["inter_file_name"] = inter_file.name
    metadata["feature_variants"] = [
        "image_feat.npy",
        "text_feat.npy",
        "image_feat_missing_test.npy",
        "text_feat_missing_test.npy",
        "image_feat_missing_moD3.npy",
        "text_feat_missing_moD3.npy",
    ]
    manifest_path = _write_manifest(prepared.output_dir, dataset_name, "i3mrec", metadata)
    return PreparedBaselineDataset(
        dataset_name=dataset_name,
        dataset_format="i3mrec",
        source_dir=prepared.source_dir,
        output_dir=prepared.output_dir,
        manifest_path=manifest_path,
        metadata=metadata,
    )


def prepare_graph_imputation_dataset(
    dataset_name: str,
    source_dir: Path,
    output_dir: Path,
    image_dim: int = 8,
    text_dim: int = 8,
) -> PreparedBaselineDataset:
    split_rows = _validate_presplit_source(source_dir)
    user_map, item_map = _build_id_maps(split_rows)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for split, target_name in [("train", "train_indexed.tsv"), ("valid", "val_indexed.tsv"), ("test", "test_indexed.tsv")]:
        target_path = output_dir / target_name
        with target_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            for row in split_rows[split]:
                writer.writerow([user_map[row["user_id"]], item_map[row["item_id"]]])

    visual_dir = output_dir / "visual_embeddings_indexed"
    textual_dir = output_dir / "textual_embeddings_indexed"
    visual_dir.mkdir(parents=True, exist_ok=True)
    textual_dir.mkdir(parents=True, exist_ok=True)

    item_ids = [item_id for item_id, _ in sorted(item_map.items(), key=lambda item: item[1])]
    visual_features = _deterministic_feature_matrix(item_ids, image_dim, "graph-visual")
    textual_features = _deterministic_feature_matrix(item_ids, text_dim, "graph-text")
    for item_idx in range(len(item_ids)):
        np.save(visual_dir / f"{item_idx}.npy", visual_features[item_idx])
        np.save(textual_dir / f"{item_idx}.npy", textual_features[item_idx])

    for empty_name in ["missing_visual_indexed.tsv", "missing_textual_indexed.tsv"]:
        (output_dir / empty_name).write_text("", encoding="utf-8")

    metadata = {
        "user_count": len(user_map),
        "item_count": len(item_map),
        "train_file": "train_indexed.tsv",
        "valid_file": "val_indexed.tsv",
        "test_file": "test_indexed.tsv",
    }
    manifest_path = _write_manifest(output_dir, dataset_name, "graph_imputation", metadata)
    return PreparedBaselineDataset(
        dataset_name=dataset_name,
        dataset_format="graph_imputation",
        source_dir=Path(source_dir),
        output_dir=output_dir,
        manifest_path=manifest_path,
        metadata=metadata,
    )


def prepare_diffmm_dataset(
    dataset_name: str,
    source_dir: Path,
    output_dir: Path,
    image_dim: int = 8,
    text_dim: int = 8,
) -> PreparedBaselineDataset:
    split_rows = _validate_presplit_source(source_dir)
    user_map, item_map = _build_id_maps(split_rows)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_rows = split_rows["train"]
    test_rows = split_rows["test"]
    train_users = [user_map[row["user_id"]] for row in train_rows]
    train_items = [item_map[row["item_id"]] for row in train_rows]
    test_users = [user_map[row["user_id"]] for row in test_rows]
    test_items = [item_map[row["item_id"]] for row in test_rows]

    train_matrix = sparse.coo_matrix(
        (np.ones(len(train_rows), dtype=np.float32), (train_users, train_items)),
        shape=(len(user_map), len(item_map)),
        dtype=np.float32,
    )
    test_matrix = sparse.coo_matrix(
        (np.ones(len(test_rows), dtype=np.float32), (test_users, test_items)),
        shape=(len(user_map), len(item_map)),
        dtype=np.float32,
    )

    with (output_dir / "trnMat.pkl").open("wb") as handle:
        pickle.dump(train_matrix, handle)
    with (output_dir / "tstMat.pkl").open("wb") as handle:
        pickle.dump(test_matrix, handle)

    item_ids = [item_id for item_id, _ in sorted(item_map.items(), key=lambda item: item[1])]
    np.save(output_dir / "image_feat.npy", _deterministic_feature_matrix(item_ids, image_dim, "diffmm-image"))
    np.save(output_dir / "text_feat.npy", _deterministic_feature_matrix(item_ids, text_dim, "diffmm-text"))

    metadata = {
        "train_matrix_file": "trnMat.pkl",
        "test_matrix_file": "tstMat.pkl",
        "image_feature_file": "image_feat.npy",
        "text_feature_file": "text_feat.npy",
        "user_count": len(user_map),
        "item_count": len(item_map),
    }
    manifest_path = _write_manifest(output_dir, dataset_name, "diffmm", metadata)
    return PreparedBaselineDataset(
        dataset_name=dataset_name,
        dataset_format="diffmm",
        source_dir=Path(source_dir),
        output_dir=output_dir,
        manifest_path=manifest_path,
        metadata=metadata,
    )
