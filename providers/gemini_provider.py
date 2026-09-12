"""
providers/gemini_provider.py
=============================
التنفيذ الفعلي لـ LLMProvider فوق Gemini API (مكتبة google-genai الرسمية).
هذا هو المكان الوحيد في المشروع الذي يستدعي مكتبة Gemini مباشرة.
"""

from __future__ import annotations
from typing import Optional

from providers.base import LLMProvider, LLMRequest, LLMResponse, LLMSource
from core import model_registry


class GeminiProvider(LLMProvider):
    provider_name = "google"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key غير موجود. أدخله في الإعدادات.")
        self._api_key = api_key
        self._client = None  # يُنشأ عند أول استخدام (lazy) لتفادي فشل الاستيراد بدون مفتاح

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def supports(self, capability: str) -> bool:
        # يفحص القدرة العامة للمزوّد (وليس لموديل بعينه، هذا في model_registry)
        return capability in {"pdf", "web_search", "structured_output", "tools", "thinking"}

    def generate(self, request: LLMRequest) -> LLMResponse:
        # فحص القدرة قبل التنفيذ (بند 34/72): لا نغيّر الموديل سرًا أبدًا.
        if request.enable_web_search and not model_registry.model_supports(
            request.model_id, "web_search"
        ):
            return LLMResponse(
                text="",
                model_id=request.model_id,
                provider=self.provider_name,
                error=(
                    "هذا الموديل لا يدعم البحث على الويب بالطريقة المطلوبة. "
                    "يرجى اختيار موديل متوافق أو إيقاف البحث."
                ),
            )
        if request.pdf_bytes and not model_registry.model_supports(request.model_id, "pdf"):
            return LLMResponse(
                text="",
                model_id=request.model_id,
                provider=self.provider_name,
                error="هذا الموديل لا يدعم قراءة ملفات PDF.",
            )

        try:
            from google.genai import types

            client = self._get_client()

            contents = []
            if request.pdf_bytes:
                contents.append(
                    types.Part.from_bytes(data=request.pdf_bytes, mime_type="application/pdf")
                )
            contents.append(request.user_prompt)

            tools = []
            if request.enable_web_search:
                tools.append(types.Tool(google_search=types.GoogleSearch()))

            gen_config_kwargs = dict(
                system_instruction=request.system_prompt,
            )
            if tools:
                gen_config_kwargs["tools"] = tools
            if request.max_output_tokens:
                gen_config_kwargs["max_output_tokens"] = request.max_output_tokens
            if request.response_schema:
                gen_config_kwargs["response_mime_type"] = "application/json"
                gen_config_kwargs["response_schema"] = request.response_schema

            thinking_levels = model_registry.get_model(request.model_id).capabilities.thinking_levels
            level = request.thinking_level if request.thinking_level in thinking_levels else thinking_levels[0]
            try:
                gen_config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=level.upper())
            except Exception:
                pass  # بعض إصدارات SDK القديمة قد لا تدعم thinking_level بعد

            config = types.GenerateContentConfig(**gen_config_kwargs)

            response = client.models.generate_content(
                model=request.model_id,
                contents=contents,
                config=config,
            )

            sources = []
            used_search = False
            try:
                grounding = response.candidates[0].grounding_metadata
                if grounding and grounding.grounding_chunks:
                    used_search = True
                    for chunk in grounding.grounding_chunks:
                        web = getattr(chunk, "web", None)
                        if web:
                            sources.append(LLMSource(title=web.title or "", url=web.uri or ""))
            except Exception:
                pass

            usage = getattr(response, "usage_metadata", None)
            return LLMResponse(
                text=response.text or "",
                model_id=request.model_id,
                provider=self.provider_name,
                input_tokens=getattr(usage, "prompt_token_count", 0) or 0,
                output_tokens=getattr(usage, "candidates_token_count", 0) or 0,
                used_web_search=used_search,
                sources=sources,
                raw=response,
            )
        except Exception as exc:  # لا نكسر الـ Pipeline بالكامل بسبب فشل استدعاء واحد
            return LLMResponse(
                text="",
                model_id=request.model_id,
                provider=self.provider_name,
                error=f"فشل استدعاء Gemini: {exc}",
            )


def build_provider(api_key: str) -> LLMProvider:
    return GeminiProvider(api_key=api_key)
