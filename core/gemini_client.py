from __future__ import annotations
from typing import Any, Optional

from config import get_secret, DEFAULT_MODEL
from core.json_utils import extract_json

def _sdk():
    try:
        from google import genai
        from google.genai import types
        return genai, types
    except ImportError as exc:
        raise RuntimeError("حزمة google-genai غير مثبتة. نفّذ pip install -r requirements.txt") from exc


class GeminiClient:
    def __init__(self, model: Optional[str] = None, web_research: bool = False):
        genai, self.types = _sdk()
        api_key = get_secret("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY غير مضبوط. أضفه في Streamlit Secrets أو متغير البيئة.")
        self.client = genai.Client(api_key=api_key)
        self.model = model or get_secret("GEMINI_MODEL", DEFAULT_MODEL)
        self.web_research = web_research

    def generate_text(self, prompt: str, *, use_web: bool = False, temperature: float = 0.6) -> tuple[str, list[dict[str, Any]]]:
        types = self.types
        config = types.GenerateContentConfig(temperature=temperature)
        if use_web and self.web_research:
            config.tools = [types.Tool(google_search=types.GoogleSearch())]
        response = self.client.models.generate_content(model=self.model, contents=prompt, config=config)
        text = getattr(response, "text", None) or ""
        citations: list[dict[str, Any]] = []
        try:
            for candidate in getattr(response, "candidates", []) or []:
                for part in getattr(getattr(candidate, "content", None), "parts", []) or []:
                    for grounding in getattr(part, "grounding_metadata", []) or []:
                        citations.append(str(grounding))
        except Exception:
            pass
        return text.strip(), citations

    def generate_json(self, prompt: str, *, use_web: bool = False, temperature: float = 0.35) -> tuple[Any, list[dict[str, Any]]]:
        types = self.types
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
        )
        if use_web and self.web_research:
            config.tools = [types.Tool(google_search=types.GoogleSearch())]
        response = self.client.models.generate_content(model=self.model, contents=prompt, config=config)
        text = getattr(response, "text", None) or "{}"
        return extract_json(text), []
