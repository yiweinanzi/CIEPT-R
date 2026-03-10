from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NodeModality(str, Enum):
    TEXT = "text"
    VISION = "vision"


@dataclass(frozen=True)
class EvidenceNode:
    node_id: str
    modality: NodeModality
    source: str
    content: str
    position: int | None = None
    span: tuple[int, int] | None = None
    bbox: tuple[float, float, float, float] | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TopologyMatrix:
    node_ids: list[str]
    values: list[list[float]]
    block_labels: list[str]
    cross_block_penalty: float


@dataclass(frozen=True)
class EvidenceGraph:
    item_id: str
    text_nodes: list[EvidenceNode]
    vision_nodes: list[EvidenceNode]
    all_nodes: list[EvidenceNode]
    topology: TopologyMatrix


@dataclass(frozen=True)
class ItemTopologyCacheRecord:
    item_id: str
    node_count: int
    modalities: dict[str, int]
    topology: TopologyMatrix
    node_payloads: list[EvidenceNode]
