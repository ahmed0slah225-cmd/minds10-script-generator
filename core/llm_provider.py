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


class RetryableLLMError(RuntimeError):
    """A transient Gemini/service/network error that may be retried safely."""

    retryable = True


class LLMProvider:
    def generate(self, prompt: str, *, model_label: str, system: str = '', web_search: bool = False, temperature: float = 0.7, json_mode: bool = False) -> LLMResult:
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')
        if not self.api_key:
            raise RuntimeError('GEMINI_API_KEY غير موجود.')
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
        retry_tokens = (
            'RESOURCE_EXHAUSTED', 'UNAVAILABLE', 'DEADLINE_EXCEEDED',
            'TIMEOUT', 'TIMED OUT', 'CONNECTION', 'CONNECTERROR',
            'CONNECTIONRESET', 'CONNECTION RESET', 'REMOTE_PROTOCOL_ERROR',
            'TEMPORARY_FAILURE', 'TEMPORARILY_UNAVAILABLE', 'DNS',
            'NAME OR SERVICE NOT KNOWN', 'NETWORK IS UNREACHABLE',
            'BROKEN PIPE', 'SERVER DISCONNECTED',
        )
        return status in (429, 500, 502, 503, 504) or any(x in text for x in retry_tokens)

    @staticmethod
    def is_retryable_exception(exc: Exception) -> bool:
        if isinstance(exc, RetryableLLMError):
            return True
        current: BaseException | None = exc
        seen: set[int] = set()
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            if isinstance(current, RetryableLLMError):
                return True
            status = getattr(current, 'code', None) or getattr(current, 'status_code', None)
            text = str(current).upper()
            if status in (429, 500, 502, 503, 504) or any(token in text for token in (
                'RESOURCE_EXHAUSTED', 'UNAVAILABLE', 'DEADLINE_EXCEEDED', 'TIMEOUT',
                'TIMED OUT', 'CONNECTION', 'CONNECTERROR', 'CONNECTIONRESET',
                'CONNECTION RESET', 'REMOTE_PROTOCOL_ERROR', 'TEMPORARY_FAILURE',
                'TEMPORARILY_UNAVAILABLE', 'DNS', 'NETWORK IS UNREACHABLE',
                'SERVER DISCONNECTED',
            )):
                return True
            current = current.__cause__ or current.__context__
        return False

    @staticmethod
    def _is_daily_quota_error(exc: Exception) -> bool:
        text = str(exc).lower().replace('_', ' ')
        return (
            'generate content free tier requests' in text
            or 'requests per day per project per model' in text
            or ('quota exceeded for metric' in text and 'free tier' in text)
        )

    def generate(self, prompt: str, *, model_label: str, system: str = '', web_search: bool = False, temperature: float = 0.7, json_mode: bool = False) -> LLMResult:
        run_id = str(uuid.uuid4())
        spec = get_model(model_label)
        cfg = {}
        if system:
            cfg['system_instruction'] = system
        if web_search:
            if not spec.support_search:
                raise RuntimeError(f'{model_label} لا يدعم البحث المطلوب.')
            cfg['tools'] = [self._types.Tool(google_search=self._types.GoogleSearch())]
        if json_mode:
            if not spec.support_structured_output:
                raise RuntimeError(f'{model_label} لا يدعم structured output المطلوب.')
            cfg['response_mime_type'] = 'application/json'

        if not spec.model_id.startswith('gemini-3.'):
            cfg['temperature'] = temperature

        started = time.perf_counter()
        try:
            response = self.client.models.generate_content(
                model=spec.model_id,
                contents=prompt,
                config=self._types.GenerateContentConfig(**cfg),
            )
        except Exception as exc:
            if self._is_daily_quota_error(exc):
                raise RuntimeError(
                    f'حصة Gemini اليومية انتهت للموديل المختار {model_label}. '
                    'المشروع لن يبدّل الموديل تلقائيًا. انتظر إعادة ضبط الحصة أو غيّر الموديل يدويًا.'
                ) from exc
            if self._is_retryable_service_error(exc):
                raise RetryableLLMError(
                    f'Gemini لم ينفذ الطلب بالموديل المختار {model_label} بسبب خطأ خدمة/اتصال مؤقت. '
                    'سيتم إعادة المحاولة من نفس المرحلة دون تبديل الموديل.'
                ) from exc
            raise

        return LLMResult(response.text or '', spec.model_id, run_id, int((time.perf_counter() - started) * 1000), response)


def parse_json(text: str) -> Any:
    text = text.strip()
    if text.startswith('```'):
        parts = text.split('\n', 1)
        if len(parts) == 2:
            text = parts[1].rsplit('```', 1)[0]
    return json.loads(text)
