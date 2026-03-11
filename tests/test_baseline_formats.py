from __future__ import annotations

import csv
from pathlib import Path
import sys
import zipfile

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.baselines.archive import extract_baseline_archive
from ciept.baselines.formats import (
    prepare_diffmm_dataset,
    prepare_graph_imputation_dataset,
    prepare_i3mrec_dataset,
    prepare_mmrec_dataset,
    prepare_vbpr_dataset,
)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_presplit_dataset(source_dir: Path) -> None:
    source_dir.mkdir(parents=True)
    _write_csv(
        source_dir / "train.csv",
        [
            {"user_id": "u1", "item_id": "i1", "rating": 1.0, "timestamp": 10},
            {"user_id": "u1", "item_id": "i2", "rating": 1.0, "timestamp": 11},
            {"user_id": "u2", "item_id": "i2", "rating": 1.0, "timestamp": 12},
        ],
    )
    _write_csv(
        source_dir / "valid.csv",
        [{"user_id": "u2", "item_id": "i1", "rating": 1.0, "timestamp": 20}],
    )
    _write_csv(
        source_dir / "test.csv",
        [{"user_id": "u3", "item_id": "i2", "rating": 1.0, "timestamp": 30}],
    )
    _write_csv(
        source_dir / "items.csv",
        [
            {"item_id": "i1", "title": "item one", "has_image": "true"},
            {"item_id": "i2", "title": "item two", "has_image": "false"},
        ],
    )


def test_extract_baseline_archive_unpacks_zip_root(tmp_path):
    archive_path = tmp_path / "baseline.zip"
    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr("demo-root/README.md", "hello")
        zf.writestr("demo-root/src/main.py", "print('ok')")

    extracted = extract_baseline_archive(archive_path, tmp_path / "work")

    assert extracted.archive_path == archive_path
    assert extracted.root_name == "demo-root"
    assert (extracted.extracted_dir / "README.md").exists()
    assert (extracted.extracted_dir / "src" / "main.py").exists()


def test_prepare_mmrec_dataset_writes_inter_file_and_features(tmp_path):
    source_dir = tmp_path / "processed" / "beauty"
    _write_presplit_dataset(source_dir)

    prepared = prepare_mmrec_dataset("beauty", source_dir, tmp_path / "mmrec")

    inter_lines = (prepared.output_dir / "beauty.inter").read_text(encoding="utf-8").splitlines()
    image_feat = np.load(prepared.output_dir / "image_feat.npy")
    text_feat = np.load(prepared.output_dir / "text_feat.npy")

    assert prepared.dataset_format == "mmrec"
    assert inter_lines[0] == "userID\titemID\tx_label"
    assert image_feat.shape[0] == 2
    assert text_feat.shape[0] == 2
    assert prepared.manifest_path.exists()


def test_prepare_vbpr_dataset_writes_numeric_interactions_and_visual_features(tmp_path):
    source_dir = tmp_path / "processed" / "beauty"
    _write_presplit_dataset(source_dir)

    prepared = prepare_vbpr_dataset("beauty", source_dir, tmp_path / "vbpr")

    interactions = (prepared.output_dir / "interactions.csv").read_text(encoding="utf-8").splitlines()
    visual_feat = np.load(prepared.output_dir / "visual_features.npy")

    assert prepared.dataset_format == "vbpr"
    assert interactions[0] == "user_idx,item_idx,split"
    assert visual_feat.shape[0] == 2
    assert visual_feat.shape[1] == 8


def test_prepare_i3mrec_dataset_writes_inter_and_feature_files(tmp_path):
    source_dir = tmp_path / "processed" / "beauty"
    _write_presplit_dataset(source_dir)

    prepared = prepare_i3mrec_dataset("beauty", source_dir, tmp_path / "i3mrec")

    inter_lines = (prepared.output_dir / "beauty.inter").read_text(encoding="utf-8").splitlines()
    assert prepared.dataset_format == "i3mrec"
    assert inter_lines[0] == "userID\titemID\tx_label"
    assert (prepared.output_dir / "image_feat.npy").exists()
    assert (prepared.output_dir / "text_feat.npy").exists()


def test_prepare_graph_imputation_dataset_writes_indexed_splits_and_embeddings(tmp_path):
    source_dir = tmp_path / "processed" / "beauty"
    _write_presplit_dataset(source_dir)

    prepared = prepare_graph_imputation_dataset("beauty", source_dir, tmp_path / "graph")

    assert prepared.dataset_format == "graph_imputation"
    assert (prepared.output_dir / "train_indexed.tsv").exists()
    assert (prepared.output_dir / "val_indexed.tsv").exists()
    assert (prepared.output_dir / "test_indexed.tsv").exists()
    assert (prepared.output_dir / "visual_embeddings_indexed" / "0.npy").exists()
    assert (prepared.output_dir / "textual_embeddings_indexed" / "1.npy").exists()


def test_prepare_diffmm_dataset_writes_pickled_matrices_and_features(tmp_path):
    source_dir = tmp_path / "processed" / "beauty"
    _write_presplit_dataset(source_dir)

    prepared = prepare_diffmm_dataset("beauty", source_dir, tmp_path / "diffmm")

    assert prepared.dataset_format == "diffmm"
    assert (prepared.output_dir / "trnMat.pkl").exists()
    assert (prepared.output_dir / "tstMat.pkl").exists()
    assert (prepared.output_dir / "image_feat.npy").exists()
    assert (prepared.output_dir / "text_feat.npy").exists()
    assert prepared.metadata["train_matrix_file"] == "trnMat.pkl"
