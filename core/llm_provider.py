from __future__ import annotations
import json, os, time, uuid
from dataclasses import dataclass
from typing import Any
from .model_registry import get_model, FALLBACK_MODEL_LABELS

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

    @staticmethod
    def _is_429(exc: Exception) -> bool:
        return (
            getattr(exc,'code',None) == 429
            or getattr(exc,'status_code',None) == 429
            or 'RESOURCE_EXHAUSTED' in str(exc)
            or 'quota' in str(exc).lower()
        )

    @staticmethod
    def _is_daily_quota_error(exc: Exception) -> bool:
        text=str(exc).lower()
        return (
            'generate_requestsperdayperprojectpermodelfreetier' in text.replace('_','')
            or 'generaterequestsperdayperprojectpermodelfreetier' in text.replace('_','')
            or 'requests per day' in text
            or 'generate_content_free_tier_requests' in text
        )

    def generate(self, prompt: str, *, model_label: str, system: str = '', web_search: bool = False, temperature: float = 0.7, json_mode: bool = False) -> LLMResult:
        selected=get_model(model_label)
        run_id=str(uuid.uuid4())
        cfg={'temperature':temperature}
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
        tried=[]
        candidates=[model_label] + [label for label in FALLBACK_MODEL_LABELS if label != model_label]
        last_error: Exception | None = None

        for label in candidates:
            spec=get_model(label)
            try:
                response=call(spec.model_id)
                return LLMResult(
                    response.text or '',
                    spec.model_id,
                    run_id,
                    int((time.perf_counter()-started)*1000),
                    response,
                )
            except Exception as exc:
                last_error=exc
                tried.append(f'{label}: {exc}')
                if not self._is_429(exc):
                    raise
                # A daily project/model quota cannot be fixed by retrying the same model.
                # Move to the next registered model instead.
                if self._is_daily_quota_error(exc):
                    continue
                # Other 429s may be transient; let the SDK's own retry handling deal with them.
                # If it still fails, continue to the next model.
                continue

        if last_error is not None and self._is_429(last_error):
            if self._is_daily_quota_error(last_error):
                raise RuntimeError(
                    'Gemini API quota اليومية انتهت للمشروع/الموديلات المتاحة حاليًا. '
                    'المشروع لم يعد يرسل محاولات إضافية لنفس الحصة. '
                    'فعّل Billing في Google AI Studio لرفع حدود الاستخدام، أو انتظر إعادة ضبط RPD. '
                    'الموديلات التي جرت محاولتها: ' + ' | '.join(x.split(':',1)[0] for x in tried)
                ) from last_error
            raise RuntimeError(
                'Gemini API أعاد 429 بعد تجربة الموديلات المتاحة. '
                'تحقق من الـRPM/TPM أو حدود المشروع ثم أعد المحاولة.'
            ) from last_error
        if last_error is not None:
            raise last_error
        raise RuntimeError('GeminiProvider failed without a response.')

def parse_json(text: str) -> dict:
    text=text.strip()
    if text.startswith('```'):
        text=text.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(text)
