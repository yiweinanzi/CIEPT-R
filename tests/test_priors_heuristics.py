from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.graph.types import EvidenceNode, NodeModality
from ciept.priors.heuristics import corroboration_score, stability_score, vulnerability_score


def test_marketing_text_scores_high_vulnerability():
    node = EvidenceNode(
        node_id="t-marketing",
        modality=NodeModality.TEXT,
        source="ocr",
        content="BEST AMAZING SALE NOW",
        position=0,
        span=(0, 20),
        bbox=None,
        metadata={"noise_risk": "0.8"},
    )

    score = vulnerability_score(node)

    assert score > 0.7


def test_structured_title_attribute_scores_higher_stability_than_banner_text():
    structured = EvidenceNode(
        node_id="t-structured",
        modality=NodeModality.TEXT,
        source="key_attribute",
        content="water resistant nylon shell",
        position=0,
        span=(0, 27),
        bbox=None,
        metadata={"consistency": "0.9"},
    )
    banner = EvidenceNode(
        node_id="t-banner",
        modality=NodeModality.TEXT,
        source="ocr",
        content="WOW DEAL",
        position=1,
        span=(0, 8),
        bbox=None,
        metadata={},
    )

    assert stability_score(structured) > stability_score(banner)


def test_cross_modal_match_increases_corroboration():
    matched = EvidenceNode(
        node_id="t-match",
        modality=NodeModality.TEXT,
        source="title",
        content="red running shoes",
        position=0,
        span=(0, 17),
        bbox=None,
        metadata={"matched_modalities": "vision", "support_count": "2"},
    )
    unmatched = EvidenceNode(
        node_id="t-unmatched",
        modality=NodeModality.TEXT,
        source="ocr",
        content="limited offer",
        position=1,
        span=(0, 13),
        bbox=None,
        metadata={},
    )

    assert corroboration_score(matched) > corroboration_score(unmatched)
