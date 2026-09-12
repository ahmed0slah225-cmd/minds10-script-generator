from __future__ import annotations
import json, os, time, uuid
from dataclasses import dataclass
from typing import Any
from .model_registry import get_model

@dataclass
class LLMResult:
    text: str
    model_id: str
    run_id: str
    elapsed_ms: int
    raw: Any = None

class LLMProvider:
    def generate(self, prompt: str, *, model_label: str, system: str = '', web_search: bool = False, temperature: float = 0.7, json_mode: bool = False) -> LLMResult:
        raise NotImplementedError

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY','')
        if not self.api_key: raise RuntimeError('GEMINI_API_KEY غير موجود.')
        try:
            from google import genai
            from google.genai import types
            self._types = types
            self.client = genai.Client(api_key=self.api_key)
        except ImportError as exc:
            raise RuntimeError('google-genai package is required for GeminiProvider.') from exc

    def generate(self, prompt: str, *, model_label: str, system: str = '', web_search: bool = False, temperature: float = 0.7, json_mode: bool = False) -> LLMResult:
        spec=get_model(model_label); run_id=str(uuid.uuid4()); cfg={'temperature':temperature}
        if system: cfg['system_instruction']=system
        if web_search: cfg['tools']=[self._types.Tool(google_search=self._types.GoogleSearch())]
        if json_mode: cfg['response_mime_type']='application/json'
        started=time.perf_counter()
        response=self.client.models.generate_content(model=spec.model_id,contents=prompt,config=self._types.GenerateContentConfig(**cfg))
        return LLMResult(response.text or '',spec.model_id,run_id,int((time.perf_counter()-started)*1000),response)

def parse_json(text: str) -> dict:
    text=text.strip()
    if text.startswith('```'):
        text=text.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(text)
