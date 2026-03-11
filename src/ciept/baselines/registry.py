from __future__ import annotations

from pathlib import Path


DIRECT_BASELINES = {
    "LightGCN": {
        "patterns": ["LightGCN-master.zip"],
        "paper_mapping": "LightGCN",
        "integration_mode": "recbole",
        "dataset_format": "recbole",
        "main_table": True,
        "notes": "Direct collaborative-filtering baseline through the RecBole auxiliary path.",
    },
    "VBPR": {
        "patterns": ["VBPR-PyTorch-main.zip"],
        "paper_mapping": "VBPR",
        "integration_mode": "vbpr_python",
        "dataset_format": "vbpr",
        "main_table": True,
        "notes": "Visual recommendation baseline through the upstream Python package implementation.",
    },
    "BM3": {
        "patterns": ["BM3-master.zip"],
        "paper_mapping": "BM3",
        "integration_mode": "mmrec",
        "dataset_format": "mmrec",
        "main_table": True,
        "notes": "MMRec-style multimodal baseline.",
    },
    "MGCN": {
        "patterns": ["MGCN-main.zip"],
        "paper_mapping": "MGCN",
        "integration_mode": "mmrec",
        "dataset_format": "mmrec",
        "main_table": True,
        "notes": "MMRec-style multimodal baseline.",
    },
    "I3-MRec": {
        "patterns": ["I3-MRec-main.zip"],
        "paper_mapping": "I3-MRec",
        "integration_mode": "i3mrec",
        "dataset_format": "i3mrec",
        "main_table": True,
        "notes": "Incomplete-modality recommendation baseline with a standalone training script.",
    },
    "CLEAR": {
        "patterns": ["CLEAR-replication-main.zip"],
        "paper_mapping": "CLEAR: Null-Space Projection for Cross-Modal De-Redundancy in Multimodal Recommendation",
        "integration_mode": "asset_mismatch",
        "dataset_format": "unavailable",
        "main_table": True,
        "notes": "Downloaded asset is an API recommendation repository, not the required multimodal CLEAR baseline.",
        "status_if_present": "asset_mismatch",
        "next_action": "Acquire the multimodal CLEAR baseline implementation.",
    },
    "Training-free Graph-based Imputation": {
        "patterns": ["Graph-Missing-Modalities-TKDE-master.zip"],
        "paper_mapping": "Training-free Graph-based Imputation of Missing Modalities in Multimodal Recommendation",
        "integration_mode": "graph_imputation",
        "dataset_format": "graph_imputation",
        "main_table": True,
        "notes": "Graph-imputation baseline from the official TKDE code release.",
    },
}

MAPPED_CANDIDATES = {
    "DiffMM": {
        "patterns": ["DiffMM-main.zip"],
        "status": "mapped_candidate",
        "paper_mapping": "candidate_only",
        "integration_mode": "diffmm",
        "dataset_format": "diffmm",
        "main_table": False,
        "notes": "Downloaded candidate reference, but not part of the current baseline list in aaai项目.md.",
    },
    "Guider": {
        "patterns": ["Guider-main.zip"],
        "status": "mapped_match",
        "paper_mapping": "Teach Me How to Denoise",
        "integration_mode": "guided_mmrec",
        "dataset_format": "mmrec",
        "main_table": True,
        "notes": "Confirmed mapping from the downloaded README to the WSDM 2025 denoising baseline.",
    },
    "MAGNET": {
        "patterns": ["MAGNET-main.zip"],
        "status": "asset_incomplete",
        "paper_mapping": "Modality-Guided Mixture of Graph Experts",
        "integration_mode": "asset_incomplete",
        "dataset_format": "asset_incomplete",
        "main_table": True,
        "notes": "Confirmed mapping, but the local archive does not contain the executable MAGNET model implementation files.",
        "next_action": "Acquire a complete MAGNET code release before integration.",
    },
    "MixRec": {
        "patterns": ["MixRec-main.zip"],
        "status": "runtime_mismatch",
        "paper_mapping": "candidate_only",
        "integration_mode": "runtime_mismatch",
        "dataset_format": "runtime_mismatch",
        "main_table": False,
        "notes": "Downloaded heterogeneous-graph TF1.14 multi-behavior CF reference is incompatible with the current single-behavior multimodal baseline contract.",
        "next_action": "Keep blocked unless a compatible single-behavior runner is introduced.",
    },
    "SMORE": {
        "patterns": ["SMORE-main.zip"],
        "status": "mapped_candidate",
        "paper_mapping": "candidate_only",
        "integration_mode": "mmrec",
        "dataset_format": "mmrec",
        "main_table": False,
        "notes": "Downloaded multimodal recommendation reference, but not a named baseline in the current project list.",
    },
}

MISSING_BASELINES = [
    {
        "name": "RecGOAT",
        "paper_mapping": "RecGOAT",
        "next_action": "Locate and download the official code or a faithful reproduction before integration.",
    },
    {
        "name": "IGDMRec",
        "paper_mapping": "IGDMRec",
        "next_action": "Locate and download the official code or a faithful reproduction before integration.",
    },
]


def _match_pattern(baselines_dir: Path, patterns: list[str]) -> str | None:
    for pattern in patterns:
        path = baselines_dir / pattern
        if path.exists():
            return str(path)
    return None


def build_baseline_inventory(baselines_dir: Path) -> list[dict]:
    baselines_dir = Path(baselines_dir)
    inventory: list[dict] = []

    for name, meta in DIRECT_BASELINES.items():
        source_path = _match_pattern(baselines_dir, meta["patterns"])
        if source_path:
            status = meta.get("status_if_present", "direct_match")
            notes = meta["notes"]
        else:
            status = "missing"
            notes = "Expected baseline asset is not available locally."
        inventory.append(
            {
                "name": name,
                "status": status,
                "source_path": source_path,
                "paper_mapping": meta["paper_mapping"],
                "integration_mode": meta["integration_mode"],
                "dataset_format": meta["dataset_format"],
                "main_table": meta["main_table"],
                "notes": notes,
                "next_action": meta.get(
                    "next_action",
                    "Integrate through the unified baseline runner." if source_path else "Acquire the missing asset.",
                ),
            }
        )

    for name, meta in MAPPED_CANDIDATES.items():
        source_path = _match_pattern(baselines_dir, meta["patterns"])
        if not source_path:
            continue
        inventory.append(
            {
                "name": name,
                "status": meta["status"],
                "source_path": source_path,
                "paper_mapping": meta["paper_mapping"],
                "integration_mode": meta["integration_mode"],
                "dataset_format": meta["dataset_format"],
                "main_table": meta["main_table"],
                "notes": meta["notes"],
                "next_action": meta.get(
                    "next_action",
                    "Keep as candidate reference only." if not meta["main_table"] else "Promote into tracking metadata.",
                ),
            }
        )

    for meta in MISSING_BASELINES:
        inventory.append(
            {
                "name": meta["name"],
                "status": "missing",
                "source_path": None,
                "paper_mapping": meta["paper_mapping"],
                "integration_mode": "unavailable",
                "dataset_format": "unavailable",
                "main_table": True,
                "notes": "Expected baseline not downloaded yet.",
                "next_action": meta["next_action"],
            }
        )

    return inventory
