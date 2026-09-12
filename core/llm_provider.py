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
    def _status(exc: Exception) -> int | None:
        return getattr(exc, 'code', None) or getattr(exc, 'status_code', None)

    @classmethod
    def _is_retryable_service_error(cls, exc: Exception) -> bool:
        status = cls._status(exc)
        text = str(exc).upper()
        return status in (429, 500, 502, 503, 504) or any(x in text for x in ('RESOURCE_EXHAUSTED', 'UNAVAILABLE', 'DEADLINE_EXCEEDED'))

    @staticmethod
    def _is_daily_quota_error(exc: Exception) -> bool:
        text=str(exc).lower().replace('_',' ')
        return (
            'generate content free tier requests' in text
            or 'requests per day per project per model' in text
            or 'quota exceeded for metric' in text and 'free tier' in text
        )

    def generate(self, prompt: str, *, model_label: str, system: str = '', web_search: bool = False, temperature: float = 0.7, json_mode: bool = False) -> LLMResult:
        run_id=str(uuid.uuid4())

        def call(spec):
            cfg={}
            if system:
                cfg['system_instruction']=system
            if web_search:
                cfg['tools']=[self._types.Tool(google_search=self._types.GoogleSearch())]
            if json_mode:
                cfg['response_mime_type']='application/json'

            # Gemini 3.x no longer accepts the legacy sampling temperature.
            # Keep the public engine API unchanged, but omit it at the provider boundary.
            if not spec.model_id.startswith('gemini-3.'):
                cfg['temperature']=temperature

            return self.client.models.generate_content(
                model=spec.model_id,
                contents=prompt,
                config=self._types.GenerateContentConfig(**cfg),
            )

        started=time.perf_counter()
        tried=[]
        candidates=[model_label] + [label for label in FALLBACK_MODEL_LABELS if label != model_label]

        # Try each registered model once. The Google SDK already performs its own
        # low-level retries; this layer handles model failover for service/quota errors.
        for label in candidates:
            spec=get_model(label)
            try:
                response=call(spec)
                return LLMResult(response.text or '',spec.model_id,run_id,int((time.perf_counter()-started)*1000),response)
            except Exception as exc:
                tried.append((label, exc))
                if not self._is_retryable_service_error(exc):
                    raise
                continue

        daily_errors=[exc for _,exc in tried if self._is_daily_quota_error(exc)]
        service_errors=[exc for _,exc in tried if not self._is_daily_quota_error(exc)]

        if daily_errors:
            models=', '.join(label for label,_ in tried)
            raise RuntimeError(
                'Gemini API quota اليومية انتهت للمشروع/الموديلات المتاحة حاليًا. '
                'كل مرحلة في الـPipeline ما زالت تعمل بشكل مستقل، لكن Google رفضت الطلبات بسبب حدود الاستخدام. '
                'فعّل Billing أو انتظر إعادة ضبط الـRPD. '
                f'الموديلات التي تمت تجربتها: {models}'
            ) from daily_errors[-1]

        if service_errors:
            models=', '.join(label for label,_ in tried)
            raise RuntimeError(
                'Gemini API غير متاح حاليًا أو تحت ضغط مرتفع. '
                'تمت تجربة كل الموديلات المسجلة بدون تغيير الـPipeline. '
                f'الموديلات التي تمت تجربتها: {models}. حاول تشغيل المرحلة مرة أخرى.'
            ) from service_errors[-1]

        raise RuntimeError('GeminiProvider failed without a response.')

def parse_json(text: str) -> Any:
    text=text.strip()
    if text.startswith('```'):
        parts=text.split('\n',1)
        if len(parts) == 2:
            text=parts[1].rsplit('```',1)[0]
    return json.loads(text)
