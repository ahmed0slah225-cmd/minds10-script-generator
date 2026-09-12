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

        def call(model_id: str):
            return self.client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=self._types.GenerateContentConfig(**cfg),
            )

        started=time.perf_counter()
        try:
            response=call(spec.model_id)
        except Exception as exc:
            # Free-tier quota can be exhausted for one model while another available
            # model in the registry still has capacity. Try exactly one controlled fallback.
            is_quota_error=getattr(exc,'code',None)==429 or getattr(exc,'status_code',None)==429 or 'RESOURCE_EXHAUSTED' in str(exc) or 'quota' in str(exc).lower()
            fallback_label='Gemini 3.7 Flash'
            if is_quota_error and model_label != fallback_label:
                fallback=get_model(fallback_label)
                try:
                    response=call(fallback.model_id)
                    return LLMResult(response.text or '',fallback.model_id,run_id,int((time.perf_counter()-started)*1000),response)
                except Exception as fallback_exc:
                    raise RuntimeError(
                        'Gemini quota exhausted for the selected model, and the fallback model was also unavailable. '
                        'Reduce request usage or wait for the quota reset. '\
                        f'Original error: {exc}'
                    ) from fallback_exc
            raise
        return LLMResult(response.text or '',spec.model_id,run_id,int((time.perf_counter()-started)*1000),response)

def parse_json(text: str) -> dict:
    text=text.strip()
    if text.startswith('```'):
        text=text.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(text)
