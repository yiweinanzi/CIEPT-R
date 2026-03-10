from __future__ import annotations


def sufficiency_gap(score_full: float, score_selected: float) -> float:
    return float(score_full) - float(score_selected)


def comprehensiveness_gap(score_full: float, score_removed: float) -> float:
    return float(score_full) - float(score_removed)


def leakage_ratio(norm_support: list[float], nuisance_mask: list[float], eps: float = 1e-6) -> float:
    if len(norm_support) != len(nuisance_mask):
        raise ValueError("norm_support and nuisance_mask must share length")
    if eps <= 0:
        raise ValueError("eps must be positive")
    numerator = sum(float(s) * float(m) for s, m in zip(norm_support, nuisance_mask))
    denominator = sum(float(s) for s in norm_support) + eps
    return numerator / denominator


def support_precision_recall_f1(
    norm_support: list[float],
    support_gold: list[int],
    threshold: float = 0.5,
) -> tuple[float, float, float]:
    if len(norm_support) != len(support_gold):
        raise ValueError("norm_support and support_gold must share length")

    predicted = [1 if float(score) >= threshold else 0 for score in norm_support]
    tp = sum(1 for pred, gold in zip(predicted, support_gold) if pred == 1 and gold == 1)
    fp = sum(1 for pred, gold in zip(predicted, support_gold) if pred == 1 and gold == 0)
    fn = sum(1 for pred, gold in zip(predicted, support_gold) if pred == 0 and gold == 1)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall == 0.0:
        return precision, recall, 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1
