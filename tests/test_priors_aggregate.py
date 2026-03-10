from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.priors.aggregate import aggregate_reliability, build_capacity_prior
from ciept.priors.types import NodeSignalScores


def test_capacity_prior_normalizes_and_prefers_reliable_nodes():
    signals = [
        NodeSignalScores(
            node_id="clean",
            corroboration=0.9,
            stability=0.9,
            vulnerability=0.1,
        ),
        NodeSignalScores(
            node_id="noisy",
            corroboration=0.2,
            stability=0.3,
            vulnerability=0.9,
        ),
    ]

    profile = aggregate_reliability(signals)
    prior = build_capacity_prior(profile)

    assert abs(sum(prior.q_cap.values()) - 1.0) < 1e-6
    assert prior.q_cap["clean"] > prior.q_cap["noisy"]


def test_capacity_prior_uses_safe_fallback_when_scores_collapse():
    signals = [
        NodeSignalScores(
            node_id="n1",
            corroboration=0.0,
            stability=0.0,
            vulnerability=1.0,
        ),
        NodeSignalScores(
            node_id="n2",
            corroboration=0.0,
            stability=0.0,
            vulnerability=1.0,
        ),
    ]

    profile = aggregate_reliability(signals, eps=0.0)
    prior = build_capacity_prior(profile, eps=1e-6)

    assert abs(prior.q_cap["n1"] - 0.5) < 1e-6
    assert abs(prior.q_cap["n2"] - 0.5) < 1e-6
