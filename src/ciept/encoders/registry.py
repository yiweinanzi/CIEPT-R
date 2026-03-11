from __future__ import annotations

from pathlib import Path

import yaml


def load_local_backend_config(path: str | Path) -> dict:
    config_path = Path(path)
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid local backend config: {config_path}")
    return payload


def ensure_local_backend_path(path: str | Path) -> Path:
    backend_path = Path(path)
    if not backend_path.exists():
        raise FileNotFoundError(f"Local backend path does not exist: {backend_path}")
    return backend_path
