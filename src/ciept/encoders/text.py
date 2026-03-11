from __future__ import annotations

import importlib
from pathlib import Path

SentenceTransformer = None

from ciept.encoders.registry import ensure_local_backend_path


class LocalQwenTextEmbedder:
    def __init__(self, model_path: str | Path, **model_kwargs):
        self.model_path = str(ensure_local_backend_path(model_path))
        self.model_kwargs = model_kwargs
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            backend_cls = SentenceTransformer
            if backend_cls is None:
                try:
                    backend_cls = importlib.import_module("sentence_transformers").SentenceTransformer
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError("sentence-transformers is not installed.") from exc
            self._backend = backend_cls(self.model_path, **self.model_kwargs)
        return self._backend

    def embed_texts(self, texts: list[str], instruction: str | None = None):
        backend = self._get_backend()
        encode_kwargs = {}
        if instruction is not None:
            encode_kwargs["prompt_name"] = instruction
        return backend.encode(texts, **encode_kwargs)
