from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RankingMetrics:
    recall_at_k: float
    ndcg_at_k: float
    mrr: float


@dataclass(frozen=True)
class FaithfulnessMetrics:
    sufficiency_gap: float
    comprehensiveness_gap: float
    leakage_ratio: float
    support_precision: float
    support_recall: float
    support_f1: float


@dataclass(frozen=True)
class UsageDiagnostics:
    image_shuffle_drop_rate: float
    random_caption_drop_rate: float
    missing_modality_drop: float
    transported_mass_ratio: float
