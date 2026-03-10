from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PerturbationConfig:
    strength: float
    family: str


@dataclass(frozen=True)
class PerturbationExample:
    example_id: str
    label: int
    text_nodes: list[dict]
    vision_nodes: list[dict]


@dataclass(frozen=True)
class PerturbationRecord:
    example_id: str
    label: int
    perturbation_family: str
    strength: float
    original_text_nodes: list[dict]
    original_vision_nodes: list[dict]
    perturbed_text_nodes: list[dict]
    perturbed_vision_nodes: list[dict]
    text_mask: list[bool]
    vision_mask: list[bool]
    changed_fields: list[str]
