from __future__ import annotations

from ciept.graph.types import EvidenceNode, NodeModality


MARKETING_TERMS = {
    "amazing",
    "best",
    "deal",
    "exclusive",
    "limited",
    "now",
    "premium",
    "sale",
    "wow",
}

HIGH_RISK_REGION_ROLES = {"background", "banner", "logo", "decor", "text_overlay"}
STABLE_REGION_ROLES = {"foreground", "object", "product", "hero"}
STRUCTURED_TEXT_SOURCES = {"title", "key_attribute", "attribute", "meta"}


def _parse_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    return None


def _parse_float(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, float(value)))


def _tokenize(content: str) -> set[str]:
    return {token.strip(".,!?;:").lower() for token in content.split() if token.strip()}


def corroboration_score(node: EvidenceNode) -> float:
    metadata = node.metadata
    explicit = _parse_float(metadata.get("corroboration"))
    if explicit is not None:
        return _clamp(explicit)

    score = 0.2
    if _parse_bool(metadata.get("corroborated")) is True:
        score += 0.3

    support_count = _parse_float(metadata.get("support_count"))
    if support_count is not None:
        score += min(support_count, 3.0) * 0.1

    matched_modalities = str(metadata.get("matched_modalities", "")).lower()
    if "vision" in matched_modalities or "text" in matched_modalities:
        score += 0.2

    if node.source in STRUCTURED_TEXT_SOURCES:
        score += 0.15

    return _clamp(score)


def stability_score(node: EvidenceNode) -> float:
    metadata = node.metadata
    explicit = _parse_float(metadata.get("stability"))
    if explicit is None:
        explicit = _parse_float(metadata.get("consistency"))
    if explicit is not None:
        return _clamp(explicit)

    score = 0.45
    if node.modality is NodeModality.TEXT:
        tokens = _tokenize(node.content)
        if node.source in STRUCTURED_TEXT_SOURCES:
            score += 0.25
        if len(tokens) <= 2:
            score -= 0.15
        if tokens & MARKETING_TERMS:
            score -= 0.2
    else:
        region_role = str(metadata.get("region_role", "")).lower()
        if region_role in STABLE_REGION_ROLES:
            score += 0.25
        if region_role in HIGH_RISK_REGION_ROLES:
            score -= 0.2

    return _clamp(score)


def vulnerability_score(node: EvidenceNode) -> float:
    metadata = node.metadata
    explicit = _parse_float(metadata.get("vulnerability"))
    if explicit is None:
        explicit = _parse_float(metadata.get("noise_risk"))
    if explicit is not None:
        return _clamp(explicit)

    score = 0.2
    if node.modality is NodeModality.TEXT:
        tokens = _tokenize(node.content)
        marketing_hits = len(tokens & MARKETING_TERMS)
        score += min(marketing_hits * 0.2, 0.5)
        if node.source == "ocr":
            score += 0.2
        if len(tokens) <= 2:
            score += 0.1
    else:
        region_role = str(metadata.get("region_role", "")).lower()
        if region_role in HIGH_RISK_REGION_ROLES:
            score += 0.45
        if _parse_bool(metadata.get("is_low_relevance_region")) is True:
            score += 0.25

    return _clamp(score)
