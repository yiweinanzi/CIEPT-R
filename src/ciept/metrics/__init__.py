"""Reusable ranking, faithfulness, and usage-diagnosis metrics."""

from ciept.metrics.faithfulness import (
    comprehensiveness_gap,
    leakage_ratio,
    sufficiency_gap,
    support_precision_recall_f1,
)
from ciept.metrics.ranking import mrr_at_k, ndcg_at_k, recall_at_k
from ciept.metrics.types import FaithfulnessMetrics, RankingMetrics, UsageDiagnostics
from ciept.metrics.usage import (
    image_shuffle_drop_rate,
    missing_modality_drop,
    random_caption_drop_rate,
    transported_mass_ratio,
)

__all__ = [
    "RankingMetrics",
    "FaithfulnessMetrics",
    "UsageDiagnostics",
    "recall_at_k",
    "ndcg_at_k",
    "mrr_at_k",
    "sufficiency_gap",
    "comprehensiveness_gap",
    "leakage_ratio",
    "support_precision_recall_f1",
    "image_shuffle_drop_rate",
    "random_caption_drop_rate",
    "missing_modality_drop",
    "transported_mass_ratio",
]
