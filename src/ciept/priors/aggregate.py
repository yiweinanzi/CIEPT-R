from __future__ import annotations

from ciept.priors.types import CapacityPrior, NodeSignalScores, ReliabilityProfile


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, float(value)))


def aggregate_reliability(
    signals: list[NodeSignalScores],
    weight_corroboration: float = 0.4,
    weight_stability: float = 0.4,
    weight_vulnerability: float = 0.3,
    eps: float = 1e-6,
) -> ReliabilityProfile:
    if not signals:
        raise ValueError("At least one node signal is required")

    reliability: dict[str, float] = {}
    node_scores = {signal.node_id: signal for signal in signals}
    for signal in signals:
        score = (
            weight_corroboration * signal.corroboration
            + weight_stability * signal.stability
            - weight_vulnerability * signal.vulnerability
        )
        reliability[signal.node_id] = _clamp(score, eps, 1.0)

    return ReliabilityProfile(
        node_scores=node_scores,
        reliability=reliability,
        weights={
            "corroboration": weight_corroboration,
            "stability": weight_stability,
            "vulnerability": weight_vulnerability,
        },
    )


def build_capacity_prior(
    profile: ReliabilityProfile,
    base_capacity: dict[str, float] | None = None,
    eps: float = 1e-6,
) -> CapacityPrior:
    if not profile.reliability:
        raise ValueError("Reliability profile must not be empty")

    if base_capacity is None:
        base_capacity = {node_id: 1.0 for node_id in profile.reliability}

    raw = {
        node_id: max(profile.reliability[node_id], 0.0) * float(base_capacity.get(node_id, 1.0))
        for node_id in profile.reliability
    }
    total = sum(raw.values())

    if total <= eps:
        uniform = 1.0 / len(raw)
        q_cap = {node_id: uniform for node_id in raw}
    else:
        q_cap = {node_id: value / total for node_id, value in raw.items()}

    return CapacityPrior(q_cap=q_cap, base_capacity=dict(base_capacity))
