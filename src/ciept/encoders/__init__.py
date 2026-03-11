"""Local encoder and OCR adapters."""

from ciept.encoders.ocr import LocalPaddleOCREngine
from ciept.encoders.registry import ensure_local_backend_path, load_local_backend_config
from ciept.encoders.text import LocalQwenTextEmbedder
from ciept.encoders.vlm import LocalQwenVLM
from ciept.encoders.vision import LocalQwenVLEmbedder

__all__ = [
    "LocalPaddleOCREngine",
    "LocalQwenTextEmbedder",
    "LocalQwenVLM",
    "LocalQwenVLEmbedder",
    "ensure_local_backend_path",
    "load_local_backend_config",
]
