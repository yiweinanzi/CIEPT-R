"""Baseline inventory and RecBole bootstrap helpers."""

from ciept.baselines.archive import ExtractedBaselineArchive, extract_baseline_archive
from ciept.baselines.data_bridge import RecboleDatasetBridge, bridge_presplit_dataset_to_recbole
from ciept.baselines.formats import (
    PreparedBaselineDataset,
    prepare_diffmm_dataset,
    prepare_graph_imputation_dataset,
    prepare_i3mrec_dataset,
    prepare_mmrec_dataset,
    prepare_vbpr_dataset,
)
from ciept.baselines.recbole_adapter import build_recbole_config, is_recbole_available
from ciept.baselines.registry import build_baseline_inventory
from ciept.baselines.runner import BaselineRunRequest, BaselineRunResult, run_baseline

__all__ = [
    "BaselineRunRequest",
    "BaselineRunResult",
    "ExtractedBaselineArchive",
    "PreparedBaselineDataset",
    "RecboleDatasetBridge",
    "bridge_presplit_dataset_to_recbole",
    "build_baseline_inventory",
    "build_recbole_config",
    "extract_baseline_archive",
    "is_recbole_available",
    "prepare_diffmm_dataset",
    "prepare_graph_imputation_dataset",
    "prepare_i3mrec_dataset",
    "prepare_mmrec_dataset",
    "prepare_vbpr_dataset",
    "run_baseline",
]
