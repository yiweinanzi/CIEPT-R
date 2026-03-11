from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.encoders.ocr import LocalPaddleOCREngine
from ciept.encoders.registry import load_local_backend_config
from ciept.encoders.text import LocalQwenTextEmbedder
from ciept.encoders.vlm import LocalQwenVLM
from ciept.encoders.vision import LocalQwenVLEmbedder


def test_load_local_backend_config_points_at_downloaded_assets():
    config = load_local_backend_config("configs/models/local_backends.yaml")

    assert config["text_embedding"]["path"].endswith("models/Qwen3-Embedding-4B")
    assert config["vision_embedding"]["path"].endswith("models/Qwen3-VL-Embedding-2B")
    assert config["vlm"]["path"].endswith("models/Qwen3.5-9B")
    assert config["ocr"]["backend"] == "paddleocr"


def test_local_qwen_text_embedder_uses_lazy_sentence_transformer_backend(monkeypatch):
    calls: dict[str, object] = {}

    class FakeSentenceTransformer:
        def __init__(self, model_name_or_path, **kwargs):
            calls["path"] = model_name_or_path
            calls["kwargs"] = kwargs

        def encode(self, texts, **kwargs):
            calls["texts"] = texts
            calls["encode_kwargs"] = kwargs
            return np.array([[1.0, 0.0], [0.0, 1.0]])

    monkeypatch.setattr("ciept.encoders.text.SentenceTransformer", FakeSentenceTransformer)
    embedder = LocalQwenTextEmbedder("models/Qwen3-Embedding-4B")
    vectors = embedder.embed_texts(["a", "b"], instruction="query")

    assert vectors.shape == (2, 2)
    assert calls["path"] == "models/Qwen3-Embedding-4B"
    assert calls["texts"] == ["a", "b"]
    assert calls["encode_kwargs"]["prompt_name"] == "query"


def test_local_qwen_vl_embedder_uses_lazy_backend(monkeypatch):
    calls: dict[str, object] = {}

    class FakeEmbedder:
        def __init__(self, model_name_or_path, **kwargs):
            calls["path"] = model_name_or_path
            calls["kwargs"] = kwargs

        def process(self, items, instruction=None):
            calls["items"] = items
            calls["instruction"] = instruction
            return np.array([[0.1, 0.2]])

    monkeypatch.setattr("ciept.encoders.vision.Qwen3VLEmbedder", FakeEmbedder)
    embedder = LocalQwenVLEmbedder("models/Qwen3-VL-Embedding-2B")
    vectors = embedder.embed_inputs([{"text": "hello", "image": "demo.png"}], instruction="Represent the input.")

    assert vectors.shape == (1, 2)
    assert calls["path"] == "models/Qwen3-VL-Embedding-2B"
    assert calls["instruction"] == "Represent the input."


def test_local_paddle_ocr_engine_uses_lazy_backend(monkeypatch):
    calls: dict[str, object] = {}

    class FakePaddleOCR:
        def __init__(self, **kwargs):
            calls["kwargs"] = kwargs

        def ocr(self, image_path, cls=True):
            calls["image_path"] = image_path
            calls["cls"] = cls
            return [[("box", ("recognized text", 0.99))]]

    monkeypatch.setattr("ciept.encoders.ocr.PaddleOCR", FakePaddleOCR)
    engine = LocalPaddleOCREngine(lang="en", use_angle_cls=True)
    records = engine.extract_text("demo.png")

    assert records == [{"text": "recognized text", "score": 0.99}]
    assert calls["image_path"] == "demo.png"
    assert calls["cls"] is True


def test_local_qwen_vlm_uses_lazy_transformers_backend(monkeypatch):
    calls: dict[str, object] = {}

    class FakeTokenizer:
        @classmethod
        def from_pretrained(cls, model_path, **kwargs):
            calls["tokenizer_path"] = model_path
            return cls()

        def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
            calls["messages"] = messages
            return "PROMPT"

        def __call__(self, text, return_tensors=None):
            calls["prompt"] = text
            return {"input_ids": [[1, 2, 3]]}

        def batch_decode(self, generated_ids, skip_special_tokens=True):
            return ["decoded answer"]

    class FakeModel:
        @classmethod
        def from_pretrained(cls, model_path, **kwargs):
            calls["model_path"] = model_path
            return cls()

        def generate(self, **kwargs):
            calls["generate_kwargs"] = kwargs
            return [[1, 2, 3, 4]]

    monkeypatch.setattr("ciept.encoders.vlm.AutoTokenizer", FakeTokenizer)
    monkeypatch.setattr("ciept.encoders.vlm.AutoModelForCausalLM", FakeModel)

    backend = LocalQwenVLM("models/Qwen3.5-9B")
    output = backend.generate([{"role": "user", "content": "hello"}])

    assert output == "decoded answer"
    assert calls["tokenizer_path"] == "models/Qwen3.5-9B"
    assert calls["model_path"] == "models/Qwen3.5-9B"
