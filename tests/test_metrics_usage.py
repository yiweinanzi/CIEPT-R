from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.metrics.usage import (
    image_shuffle_drop_rate,
    missing_modality_drop,
    random_caption_drop_rate,
    transported_mass_ratio,
)


def test_usage_metrics_return_expected_relative_drops():
    assert image_shuffle_drop_rate(1.0, 0.7) > 0.0
    assert random_caption_drop_rate(1.0, 0.8) > 0.0
    assert missing_modality_drop(1.0, 0.6) > 0.0
    assert 0.0 < transported_mass_ratio(0.5, 1.0) <= 1.0
