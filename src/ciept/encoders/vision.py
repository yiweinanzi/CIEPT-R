from __future__ import annotations

import importlib.util
from pathlib import Path

Qwen3VLEmbedder = None

from ciept.encoders.registry import ensure_local_backend_path


class LocalQwenVLEmbedder:
    def __init__(self, model_path: str | Path, **model_kwargs):
        self.model_path = str(ensure_local_backend_path(model_path))
        self.model_kwargs = model_kwargs
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            backend_cls = Qwen3VLEmbedder
            if backend_cls is None:
                script_path = Path(self.model_path) / "scripts" / "qwen3_vl_embedding.py"
                if not script_path.exists():
                    raise RuntimeError("Qwen3-VL embedding script is missing from the local model directory.")
                spec = importlib.util.spec_from_file_location("ciept_local_qwen3_vl_embedding", script_path)
                if spec is None or spec.loader is None:  # pragma: no cover
                    raise RuntimeError("Failed to load the local Qwen3-VL embedding script.")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                backend_cls = module.Qwen3VLEmbedder
            self._backend = backend_cls(self.model_path, **self.model_kwargs)
        return self._backend

    def embed_inputs(self, items: list[dict], instruction: str | None = None):
        backend = self._get_backend()
        return backend.process(items, instruction=instruction)
