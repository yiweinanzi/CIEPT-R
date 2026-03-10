from __future__ import annotations


def _relative_drop(score_full: float, score_variant: float, eps: float = 1e-6) -> float:
    return (float(score_full) - float(score_variant)) / (abs(float(score_full)) + eps)


def image_shuffle_drop_rate(score_full: float, score_shuffled: float, eps: float = 1e-6) -> float:
    return _relative_drop(score_full, score_shuffled, eps=eps)


def random_caption_drop_rate(score_full: float, score_caption_dropped: float, eps: float = 1e-6) -> float:
    return _relative_drop(score_full, score_caption_dropped, eps=eps)


def missing_modality_drop(score_full: float, score_missing: float, eps: float = 1e-6) -> float:
    return _relative_drop(score_full, score_missing, eps=eps)


def transported_mass_ratio(transported_mass: float, source_mass_sum: float, eps: float = 1e-6) -> float:
    if source_mass_sum < 0:
        raise ValueError("source_mass_sum must be non-negative")
    return float(transported_mass) / (float(source_mass_sum) + eps)
