"""Audit and intervention helpers built on transport outputs."""

from ciept.audit.adjudication import init_adjudication_queue
from ciept.audit.audit_dataset import build_audit_dataset
from ciept.audit.gating import binary_gumbel_ste
from ciept.audit.losses import leakage_ratio, single_pass_intervention
from ciept.audit.support import normalized_support, support_to_logits
from ciept.audit.types import InterventionOutputs, SupportOutputs
from ciept.audit.vlm_io import export_vlm_requests, merge_vlm_predictions

__all__ = [
    "SupportOutputs",
    "InterventionOutputs",
    "build_audit_dataset",
    "export_vlm_requests",
    "merge_vlm_predictions",
    "init_adjudication_queue",
    "normalized_support",
    "support_to_logits",
    "binary_gumbel_ste",
    "leakage_ratio",
    "single_pass_intervention",
]
