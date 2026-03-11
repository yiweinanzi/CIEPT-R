from __future__ import annotations

import importlib
from pathlib import Path

AutoModelForCausalLM = None
AutoTokenizer = None

from ciept.encoders.registry import ensure_local_backend_path


class LocalQwenVLM:
    def __init__(self, model_path: str | Path, **model_kwargs):
        self.model_path = str(ensure_local_backend_path(model_path))
        self.model_kwargs = model_kwargs
        self._tokenizer = None
        self._model = None

    def _ensure_backend(self):
        if self._tokenizer is None or self._model is None:
            tokenizer_cls = AutoTokenizer
            model_cls = AutoModelForCausalLM
            if tokenizer_cls is None or model_cls is None:
                try:
                    transformers = importlib.import_module("transformers")
                    tokenizer_cls = transformers.AutoTokenizer
                    model_cls = transformers.AutoModelForCausalLM
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError("transformers is not installed.") from exc
            self._tokenizer = tokenizer_cls.from_pretrained(self.model_path)
            self._model = model_cls.from_pretrained(self.model_path, **self.model_kwargs)
        return self._tokenizer, self._model

    def generate(self, messages: list[dict], **generate_kwargs) -> str:
        tokenizer, model = self._ensure_backend()
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = tokenizer(prompt, return_tensors="pt")
        generated_ids = model.generate(**model_inputs, **generate_kwargs)
        return tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
