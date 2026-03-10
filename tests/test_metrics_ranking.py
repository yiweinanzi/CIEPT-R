from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.metrics.ranking import mrr_at_k, ndcg_at_k, recall_at_k


def test_ranking_metrics_return_expected_toy_values():
    pos_score = 0.9
    neg_scores = [0.3, 0.2, 0.1]

    assert recall_at_k(pos_score, neg_scores, k=1) == 1.0
    assert mrr_at_k(pos_score, neg_scores) == 1.0
    assert ndcg_at_k([1, 0, 0], [0.9, 0.2, 0.1], k=3) == 1.0
