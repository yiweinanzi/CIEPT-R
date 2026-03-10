from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AuditExample:
    audit_id: str
    source_example_id: str
    label: int
    perturbation_family: str
    strength: float
    text_nodes: list[dict]
    vision_nodes: list[dict]
    nuisance_mask: dict
    review_status: str = "pending"


@dataclass(frozen=True)
class AuditPrediction:
    audit_id: str
    predicted_minimal_evidence: list[str]
    predicted_nuisance_nodes: list[str]
    confidence: float
    raw_response: str


@dataclass(frozen=True)
class AuditAdjudication:
    audit_id: str
    source_example_id: str
    label: int
    vlm_prediction: dict
    adjudicator_a: str = ""
    adjudicator_b: str = ""
    final_label: str = ""
    status: str = "pending"


@dataclass(frozen=True)
class AuditDatasetManifest:
    sample_count: int
    strengths: list[float]
    families: dict[str, int]
    prediction_coverage: int = 0
    missing_predictions: int = 0
    unknown_prediction_ids: int = 0
    adjudication_queue_count: int = 0
    metadata: dict = field(default_factory=dict)
