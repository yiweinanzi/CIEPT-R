from __future__ import annotations

import importlib
from pathlib import Path

PaddleOCR = None


class LocalPaddleOCREngine:
    def __init__(self, lang: str = "en", use_angle_cls: bool = True, **ocr_kwargs):
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        self.ocr_kwargs = ocr_kwargs
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            backend_cls = PaddleOCR
            if backend_cls is None:
                try:
                    backend_cls = importlib.import_module("paddleocr").PaddleOCR
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError("PaddleOCR or paddlepaddle is not installed.") from exc
            self._backend = backend_cls(lang=self.lang, use_angle_cls=self.use_angle_cls, **self.ocr_kwargs)
        return self._backend

    def extract_text(self, image_path: str | Path) -> list[dict]:
        backend = self._get_backend()
        raw = backend.ocr(str(image_path), cls=self.use_angle_cls)
        records: list[dict] = []
        for page in raw:
            for _, (text, score) in page:
                records.append({"text": text, "score": float(score)})
        return records
