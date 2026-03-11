from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.baselines.recbole_adapter import build_recbole_config, is_recbole_available


def test_build_recbole_config_uses_presplit_full_sort_defaults(tmp_path):
    config = build_recbole_config(
        dataset_name="amazon2023",
        data_path=tmp_path,
        model_name="LightGCN",
    )

    assert config["model"] == "LightGCN"
    assert config["dataset"] == "amazon2023"
    assert config["benchmark_filename"] == ["train", "valid", "test"]
    assert config["eval_args"]["order"] == "TO"
    assert config["eval_args"]["mode"] == "full"


def test_is_recbole_available_returns_bool():
    assert isinstance(is_recbole_available(), bool)
