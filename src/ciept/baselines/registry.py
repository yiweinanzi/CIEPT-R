from __future__ import annotations

from pathlib import Path


DIRECT_MATCHES = {
    "LightGCN": {
        "patterns": ["LightGCN-master.zip"],
        "paper_mapping": "LightGCN",
        "integration_mode": "recbole",
    },
    "VBPR": {
        "patterns": ["VBPR-PyTorch-main.zip"],
        "paper_mapping": "VBPR",
        "integration_mode": "external_script",
    },
    "BM3": {
        "patterns": ["BM3-master.zip"],
        "paper_mapping": "BM3",
        "integration_mode": "external_script",
    },
    "MGCN": {
        "patterns": ["MGCN-main.zip"],
        "paper_mapping": "MGCN",
        "integration_mode": "external_script",
    },
    "I3-MRec": {
        "patterns": ["I3-MRec-main.zip"],
        "paper_mapping": "I3-MRec",
        "integration_mode": "external_script",
    },
    "CLEAR": {
        "patterns": ["CLEAR-replication-main.zip"],
        "paper_mapping": "CLEAR",
        "integration_mode": "external_script",
    },
    "Training-free Graph-based Imputation": {
        "patterns": ["Graph-Missing-Modalities-TKDE-master.zip"],
        "paper_mapping": "Training-free Graph-based Imputation of Missing Modalities in Multimodal Recommendation",
        "integration_mode": "external_script",
    },
}

MAPPED_CANDIDATES = {
    "DiffMM": {"patterns": ["DiffMM-main.zip"], "notes": "Downloaded locally, needs manual paper mapping."},
    "Guider": {"patterns": ["Guider-main.zip"], "notes": "Downloaded locally, needs manual paper mapping."},
    "MAGNET": {"patterns": ["MAGNET-main.zip"], "notes": "Downloaded locally, needs manual paper mapping."},
    "MixRec": {"patterns": ["MixRec-main.zip"], "notes": "Downloaded locally, needs manual paper mapping."},
    "SMORE": {"patterns": ["SMORE-main.zip"], "notes": "Downloaded locally, needs manual paper mapping."},
}

MISSING_BASELINES = [
    "RecGOAT",
    "IGDMRec",
    "Modality-Guided Mixture of Graph Experts",
    "Teach Me How to Denoise",
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

    for name, meta in DIRECT_MATCHES.items():
        source_path = _match_pattern(baselines_dir, meta["patterns"])
        inventory.append(
            {
                "name": name,
                "status": "direct_match" if source_path else "missing",
                "source_path": source_path,
                "paper_mapping": meta["paper_mapping"],
                "integration_mode": meta["integration_mode"],
                "notes": "Ready for direct integration." if source_path else "Expected baseline not downloaded yet.",
            }
        )

    for name, meta in MAPPED_CANDIDATES.items():
        source_path = _match_pattern(baselines_dir, meta["patterns"])
        if source_path:
            inventory.append(
                {
                    "name": name,
                    "status": "mapped_candidate",
                    "source_path": source_path,
                    "paper_mapping": "manual_review",
                    "integration_mode": "external_script",
                    "notes": meta["notes"],
                }
            )

    known_missing = {entry["name"] for entry in inventory if entry["status"] == "missing"}
    for name in MISSING_BASELINES:
        if name not in known_missing:
            inventory.append(
                {
                    "name": name,
                    "status": "missing",
                    "source_path": None,
                    "paper_mapping": name,
                    "integration_mode": "external_script",
                    "notes": "Expected baseline not downloaded yet.",
                }
            )

    return inventory
