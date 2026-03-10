from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.data.stress_rules import (
    apply_negative_preserving_lure,
    apply_positive_preserving_nuisance,
)
from ciept.data.stress_types import PerturbationConfig, PerturbationExample


def make_example(label: int) -> PerturbationExample:
    return PerturbationExample(
        example_id="ex-1",
        label=label,
        text_nodes=[
            {"node_id": "t1", "content": "running shoes", "source": "title"},
            {"node_id": "t2", "content": "lightweight mesh", "source": "attribute"},
        ],
        vision_nodes=[
            {"node_id": "v1", "content": "product foreground", "source": "image_region"},
            {"node_id": "v2", "content": "plain background", "source": "image_region"},
        ],
    )


def test_positive_nuisance_preserves_label_and_marks_changed_nodes():
    record = apply_positive_preserving_nuisance(
        make_example(label=1),
        PerturbationConfig(strength=0.5, family="positive_nuisance"),
    )

    assert record.label == 1
    assert any(record.text_mask) or any(record.vision_mask)
    assert record.perturbation_family == "positive_nuisance"


def test_negative_lure_preserves_label_and_adds_lure_nodes():
    record = apply_negative_preserving_lure(
        make_example(label=0),
        PerturbationConfig(strength=0.5, family="negative_lure"),
    )

    assert record.label == 0
    assert any(record.text_mask) or any(record.vision_mask)
    assert record.perturbation_family == "negative_lure"
