from __future__ import annotations

from ciept.graph.types import EvidenceNode
from ciept.priors.heuristics import corroboration_score, vulnerability_score
from ciept.priors.types import NuisanceDecision, NuisanceMask


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


def infer_nuisance_mask(
    nodes: list[EvidenceNode],
    reliability: dict[str, float],
) -> NuisanceMask:
    decisions: dict[str, NuisanceDecision] = {}

    for node in nodes:
        explicit = _parse_bool(node.metadata.get("is_nuisance"))
        if explicit is not None:
            decisions[node.node_id] = NuisanceDecision(
                node_id=node.node_id,
                is_nuisance=explicit,
                source="explicit",
            )
            continue

        region_role = str(node.metadata.get("region_role", "")).lower()
        vulnerability = vulnerability_score(node)
        corroboration = corroboration_score(node)
        reliability_score = reliability.get(node.node_id, 0.5)
        content = node.content.lower()

        heuristic_flag = False
        if region_role in {"background", "banner", "logo", "decor", "text_overlay"}:
            heuristic_flag = True
        if any(term in content for term in ["sale", "deal", "amazing", "best", "wow", "limited"]):
            heuristic_flag = True
        if vulnerability >= 0.7 and corroboration <= 0.4:
            heuristic_flag = True
        if vulnerability >= 0.6 and reliability_score <= 0.35:
            heuristic_flag = True

        decisions[node.node_id] = NuisanceDecision(
            node_id=node.node_id,
            is_nuisance=heuristic_flag,
            source="heuristic",
        )

    return NuisanceMask(decisions=decisions)
