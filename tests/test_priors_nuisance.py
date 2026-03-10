from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.graph.types import EvidenceNode, NodeModality
from ciept.priors.aggregate import aggregate_reliability, build_capacity_prior
from ciept.priors.heuristics import corroboration_score, stability_score, vulnerability_score
from ciept.priors.nuisance import infer_nuisance_mask
from ciept.priors.types import NodeSignalScores


def test_explicit_nuisance_labels_override_heuristics():
    node = EvidenceNode(
        node_id="t-clean-labeled",
        modality=NodeModality.TEXT,
        source="title",
        content="running shoes",
        position=0,
        span=(0, 13),
        bbox=None,
        metadata={"is_nuisance": "false", "matched_modalities": "vision"},
    )

    mask = infer_nuisance_mask([node], reliability={"t-clean-labeled": 0.9})

    assert mask.decisions["t-clean-labeled"].is_nuisance is False
    assert mask.decisions["t-clean-labeled"].source == "explicit"


def test_heuristic_fallback_catches_suspicious_nodes():
    node = EvidenceNode(
        node_id="v-banner",
        modality=NodeModality.VISION,
        source="image_region",
        content="sale banner",
        position=None,
        span=None,
        bbox=(0.0, 0.0, 1.0, 0.2),
        metadata={"region_role": "banner"},
    )

    mask = infer_nuisance_mask([node], reliability={"v-banner": 0.2})

    assert mask.decisions["v-banner"].is_nuisance is True
    assert mask.decisions["v-banner"].source == "heuristic"


def test_clean_nodes_get_higher_reliability_and_capacity_than_nuisance_nodes():
    clean = EvidenceNode(
        node_id="clean",
        modality=NodeModality.TEXT,
        source="key_attribute",
        content="water resistant nylon shell",
        position=0,
        span=(0, 27),
        bbox=None,
        metadata={"consistency": "0.9", "matched_modalities": "vision", "support_count": "2"},
    )
    nuisance = EvidenceNode(
        node_id="nuisance",
        modality=NodeModality.VISION,
        source="image_region",
        content="promo logo overlay",
        position=None,
        span=None,
        bbox=(0.0, 0.0, 1.0, 0.2),
        metadata={"region_role": "logo", "is_low_relevance_region": "true"},
    )

    signals = [
        NodeSignalScores(
            node_id=clean.node_id,
            corroboration=corroboration_score(clean),
            stability=stability_score(clean),
            vulnerability=vulnerability_score(clean),
        ),
        NodeSignalScores(
            node_id=nuisance.node_id,
            corroboration=corroboration_score(nuisance),
            stability=stability_score(nuisance),
            vulnerability=vulnerability_score(nuisance),
        ),
    ]

    profile = aggregate_reliability(signals)
    prior = build_capacity_prior(profile)
    mask = infer_nuisance_mask([clean, nuisance], reliability=profile.reliability)

    assert profile.reliability["clean"] > profile.reliability["nuisance"]
    assert prior.q_cap["clean"] > prior.q_cap["nuisance"]
    assert mask.decisions["nuisance"].is_nuisance is True
