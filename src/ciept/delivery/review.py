from __future__ import annotations

from pathlib import Path


def build_required_assets(project_root: Path) -> str:
    return "\n".join(
        [
            "# Required Assets",
            "",
            "## Datasets",
            "- Amazon Reviews 2023: Clothing_Shoes_and_Jewelry, Sports_and_Outdoors, Beauty_and_Personal_Care",
            "- Legacy Amazon baselines: Clothing, Sports, Beauty",
            "- Cross-domain appendix datasets: KuaiRec, MicroLens, THACIL-style micro-video set",
            "",
            "## Models",
            "- Core runtime: PyTorch 2.10",
            "- Future VLM choice for audit pre-annotation (provider-agnostic placeholder): GPT-4.1/4o, Qwen2.5-VL, Gemini, or an equivalent local VLM",
            "- Baseline implementations/checkpoints as required for comparison",
            "",
            "## Baselines",
            "- LightGCN",
            "- VBPR",
            "- BM3",
            "- MGCN",
            "- Teach Me How to Denoise",
            "- I3-MRec",
            "- CLEAR",
            "- Training-free Graph-based Imputation",
            "- RecGOAT",
            "- IGDMRec",
            "- Modality-Guided Mixture of Graph Experts",
            "",
            "## Deferred External Assets",
            "- Real benchmark datasets are not yet downloaded",
            "- Real VLM integration is not yet connected",
            "- External baseline methods are not yet integrated",
        ]
    )


def build_implementation_review(project_root: Path) -> str:
    return "\n".join(
        [
            "# Implementation Review",
            "",
            "This review compares the repository against `aaai项目.md`.",
            "",
            "## 数据集配置方案",
            "- Implemented: offline data protocol, stress artifacts, audit dataset protocol",
            "- Placeholder-dependent: real Amazon Reviews 2023 downloads and large-scale preprocessing",
            "",
            "## 技术实施详细方案",
            "- Implemented: graph structures, priors, toy transport, torch reranker, intervention, toy train/eval",
            "- Partial: Gromov structure term, real benchmark-scale solver behavior",
            "",
            "## 评估指标详细配置",
            "- Implemented: ranking metrics, faithfulness metrics, usage-diagnosis metrics",
            "- Deferred: significance testing and multi-seed statistics",
            "",
            "## 实验设计详细方案",
            "- Implemented: dispatcher-based experiment runner and result-directory protocol",
            "- Placeholder-dependent: real benchmark execution and baseline comparisons",
            "",
            "## 最终交付物",
            "- Implemented now: delivery bundle, reproducibility checklist, resource inventory, implementation review",
            "- Deferred: paper writing and benchmark-grade result assets",
            "",
            "## Remaining Placeholder-Dependent Areas",
            "- Real datasets",
            "- Real VLM outputs",
            "- External baselines and checkpoints",
            "- Experiment outputs remain toy/placeholder until those assets are integrated",
        ]
    )
