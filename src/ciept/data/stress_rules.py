from __future__ import annotations

from math import ceil

from ciept.data.stress_types import PerturbationConfig, PerturbationExample, PerturbationRecord


def _validate_config(config: PerturbationConfig) -> None:
    if config.strength not in {0.1, 0.3, 0.5}:
        raise ValueError("strength must be one of 0.1, 0.3, 0.5")


def _num_to_modify(count: int, strength: float) -> int:
    if count <= 0:
        return 0
    return max(1, ceil(count * strength))


def apply_positive_preserving_nuisance(
    example: PerturbationExample,
    config: PerturbationConfig,
) -> PerturbationRecord:
    _validate_config(config)
    text_nodes = [dict(node) for node in example.text_nodes]
    vision_nodes = [dict(node) for node in example.vision_nodes]
    text_mask = [False] * len(text_nodes)
    vision_mask = [False] * len(vision_nodes)
    changed_fields: list[str] = []

    text_budget = _num_to_modify(len(text_nodes), config.strength)
    for idx in range(min(text_budget, len(text_nodes))):
        text_nodes[idx]["content"] = f"{text_nodes[idx]['content']} premium sale"
        text_nodes[idx]["perturbation_tag"] = "nuisance_marketing"
        text_mask[idx] = True
        if "text_nodes" not in changed_fields:
            changed_fields.append("text_nodes")

    vision_budget = _num_to_modify(len(vision_nodes), config.strength)
    for idx in range(min(vision_budget, len(vision_nodes))):
        vision_nodes[idx]["content"] = f"{vision_nodes[idx]['content']} banner decor"
        vision_nodes[idx]["perturbation_tag"] = "nuisance_background"
        vision_mask[idx] = True
        if "vision_nodes" not in changed_fields:
            changed_fields.append("vision_nodes")

    return PerturbationRecord(
        example_id=example.example_id,
        label=example.label,
        perturbation_family=config.family,
        strength=config.strength,
        original_text_nodes=example.text_nodes,
        original_vision_nodes=example.vision_nodes,
        perturbed_text_nodes=text_nodes,
        perturbed_vision_nodes=vision_nodes,
        text_mask=text_mask,
        vision_mask=vision_mask,
        changed_fields=changed_fields,
    )


def apply_negative_preserving_lure(
    example: PerturbationExample,
    config: PerturbationConfig,
) -> PerturbationRecord:
    _validate_config(config)
    text_nodes = [dict(node) for node in example.text_nodes]
    vision_nodes = [dict(node) for node in example.vision_nodes]
    text_mask = [False] * len(text_nodes)
    vision_mask = [False] * len(vision_nodes)
    changed_fields: list[str] = []

    text_budget = _num_to_modify(len(text_nodes), config.strength)
    for idx in range(min(text_budget, len(text_nodes))):
        text_nodes[idx]["content"] = f"{text_nodes[idx]['content']} sporty trendy"
        text_nodes[idx]["perturbation_tag"] = "lure_style"
        text_mask[idx] = True
        if "text_nodes" not in changed_fields:
            changed_fields.append("text_nodes")

    vision_budget = _num_to_modify(len(vision_nodes), config.strength)
    for idx in range(min(vision_budget, len(vision_nodes))):
        vision_nodes[idx]["content"] = f"{vision_nodes[idx]['content']} glossy style cue"
        vision_nodes[idx]["perturbation_tag"] = "lure_visual"
        vision_mask[idx] = True
        if "vision_nodes" not in changed_fields:
            changed_fields.append("vision_nodes")

    return PerturbationRecord(
        example_id=example.example_id,
        label=example.label,
        perturbation_family=config.family,
        strength=config.strength,
        original_text_nodes=example.text_nodes,
        original_vision_nodes=example.vision_nodes,
        perturbed_text_nodes=text_nodes,
        perturbed_vision_nodes=vision_nodes,
        text_mask=text_mask,
        vision_mask=vision_mask,
        changed_fields=changed_fields,
    )
