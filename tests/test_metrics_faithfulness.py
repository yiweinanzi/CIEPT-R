from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.metrics.faithfulness import (
    comprehensiveness_gap,
    leakage_ratio,
    sufficiency_gap,
    support_precision_recall_f1,
)


def test_faithfulness_metrics_follow_expected_directions():
    assert abs(sufficiency_gap(0.9, 0.8) - 0.1) < 1e-8
    assert abs(comprehensiveness_gap(0.9, 0.3) - 0.6) < 1e-8
    assert abs(leakage_ratio([0.2, 0.8], [1.0, 0.0]) - 0.2) < 1e-6

    precision, recall, f1 = support_precision_recall_f1(
        norm_support=[0.9, 0.2, 0.8],
        support_gold=[1, 0, 1],
        threshold=0.5,
    )
    assert precision == 1.0
    assert recall == 1.0
    assert f1 == 1.0
