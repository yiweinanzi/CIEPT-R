from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.delivery.review import build_implementation_review, build_required_assets


def test_required_assets_lists_datasets_models_and_baselines():
    content = build_required_assets(Path(__file__).resolve().parents[1])

    assert "Datasets" in content
    assert "Amazon Reviews 2023" in content
    assert "Baselines" in content


def test_implementation_review_references_project_sections():
    review = build_implementation_review(Path(__file__).resolve().parents[1])

    assert "数据集配置方案" in review
    assert "实验设计详细方案" in review
