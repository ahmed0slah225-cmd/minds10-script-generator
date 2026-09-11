from __future__ import annotations
import random
import time
from typing import Any, Optional

from config import get_secret, DEFAULT_MODEL, FALLBACK_MODEL, MAX_API_ATTEMPTS
from core.json_utils import extract_json


def _sdk():
    try:
        from google import genai
        from google.genai import types
        return genai, types
    except ImportError as exc:
        raise RuntimeError("حزمة google-genai غير مثبتة. نفّذ pip install -r requirements.txt") from exc


def _status_code(exc: Exception) -> int | None:
    code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    try:
        return int(code) if code is not None else None
    except (TypeError, ValueError):
        return None


def _is_transient(exc: Exception) -> bool:
    code = _status_code(exc)
    if code in {408, 429} or (code is not None and 500 <= code <= 599):
        return True
    text = str(exc).lower()
    return any(marker in text for marker in ("503 unavailable", "service unavailable", "temporarily unavailable", "resource exhausted"))


class GeminiClient:
    def __init__(self, model: Optional[str] = None, web_research: bool = False):
        genai, self.types = _sdk()
        api_key = get_secret("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY غير مضبوط. أضفه في Streamlit Secrets أو متغير البيئة.")
        self.client = genai.Client(api_key=api_key)
        self.model = model or get_secret("GEMINI_MODEL", DEFAULT_MODEL)
        self.fallback_model = get_secret("GEMINI_FALLBACK_MODEL", FALLBACK_MODEL)
        self.web_research = web_research
        try:
            self.max_attempts = max(1, int(get_secret("GEMINI_MAX_ATTEMPTS", str(MAX_API_ATTEMPTS))))
        except ValueError:
            self.max_attempts = MAX_API_ATTEMPTS

    def _config(self, *, use_web: bool, json_mode: bool):
        config = self.types.GenerateContentConfig()
        if json_mode:
            config.response_mime_type = "application/json"
        if use_web and self.web_research:
            config.tools = [self.types.Tool(google_search=self.types.GoogleSearch())]
        return config

    def _generate(self, prompt: str, *, use_web: bool, json_mode: bool):
        config = self._config(use_web=use_web, json_mode=json_mode)
        models = [self.model]
        if self.fallback_model and self.fallback_model != self.model:
            models.append(self.fallback_model)

        last_exc: Exception | None = None
        for model_index, model in enumerate(models):
            for attempt in range(self.max_attempts):
                try:
                    return self.client.models.generate_content(model=model, contents=prompt, config=config), model
                except Exception as exc:
                    last_exc = exc
                    if not _is_transient(exc):
                        raise
                    if attempt == self.max_attempts - 1:
                        break
                    # Extra protection around the SDK's own transient-error retry behavior.
                    delay = min(20.0, 1.5 * (2 ** attempt)) + random.uniform(0, 0.75)
                    time.sleep(delay)
            if model_index == 0 and len(models) > 1:
                continue

        assert last_exc is not None
        raise RuntimeError(
            f"Gemini تعذر عليه تنفيذ الطلب بعد المحاولات المتاحة. "
            f"النموذج الأساسي: {self.model}. "
            f"النموذج البديل: {self.fallback_model or 'غير مضبوط'}. "
            f"آخر خطأ: {last_exc}"
        ) from last_exc

    def generate_text(self, prompt: str, *, use_web: bool = False) -> tuple[str, list[dict[str, Any]]]:
        response, _used_model = self._generate(prompt, use_web=use_web, json_mode=False)
        text = getattr(response, "text", None) or ""
        citations: list[dict[str, Any]] = []
        try:
            metadata = getattr(response, "grounding_metadata", None)
            if metadata:
                citations.append({"grounding_metadata": str(metadata)})
        except Exception:
            pass
        return text.strip(), citations

    def generate_json(self, prompt: str, *, use_web: bool = False) -> tuple[Any, list[dict[str, Any]]]:
        response, _used_model = self._generate(prompt, use_web=use_web, json_mode=True)
        text = getattr(response, "text", None) or "{}"
        return extract_json(text), []
