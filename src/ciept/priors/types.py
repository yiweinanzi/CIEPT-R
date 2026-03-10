from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NodeSignalScores:
    node_id: str
    corroboration: float
    stability: float
    vulnerability: float


@dataclass(frozen=True)
class ReliabilityProfile:
    node_scores: dict[str, NodeSignalScores]
    reliability: dict[str, float]
    weights: dict[str, float]


@dataclass(frozen=True)
class CapacityPrior:
    q_cap: dict[str, float]
    base_capacity: dict[str, float]


@dataclass(frozen=True)
class NuisanceDecision:
    node_id: str
    is_nuisance: bool
    source: str


@dataclass(frozen=True)
class NuisanceMask:
    decisions: dict[str, NuisanceDecision]


@dataclass(frozen=True)
class NodePriorBundle:
    reliability: ReliabilityProfile
    capacity: CapacityPrior
    nuisance_mask: NuisanceMask
