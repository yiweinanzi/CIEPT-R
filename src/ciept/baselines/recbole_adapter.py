from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


def is_recbole_available() -> bool:
    return importlib.util.find_spec("recbole") is not None


def _load_base_config() -> dict:
    config_path = Path(__file__).resolve().parents[3] / "configs" / "baselines" / "recbole_base.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def build_recbole_config(
    dataset_name: str,
    data_path: Path,
    model_name: str,
    benchmark_filename: list[str] | None = None,
) -> dict:
    config = _load_base_config()
    config["dataset"] = dataset_name
    config["data_path"] = str(Path(data_path))
    config["model"] = model_name
    config["benchmark_filename"] = benchmark_filename or ["train", "valid", "test"]
    return config
