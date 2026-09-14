"""
providers/gemini.py
====================
تطبيق LLMProvider لموديلات Gemini (3.6 Flash / 3.7 Flash وما بعدها).

هذا الملف هو الموضع الوحيد في المشروع الذي يُفترض أن "يعرف" شكل استدعاء
Gemini API فعليًا. أي Engine آخر يمر عبر providers.base.get_provider().

ملاحظة تنفيذ: يعتمد على مكتبة `google-genai` (أو `google-generativeai`).
الاستيراد مؤجَّل (lazy import) داخل __init__ حتى لا يفشل تحميل بقية
المشروع في بيئة بدون هذه المكتبة أو بدون مفتاح API مضبوط.
"""

from __future__ import annotations

import os
import time
from typing import Any

from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, GenerationResult, LLMProvider


class GeminiProvider(LLMProvider):
    provider_name = "google"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self._client = None  # يُهيَّأ عند أول استخدام فعلي (lazy)

    def _client_or_init(self):
        if self._client is None:
            if not self._api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY غير مضبوط. اضبطه كمتغيّر بيئة أو مرّره لـ GeminiProvider(api_key=...)."
                )
            try:
                from google import genai  # google-genai SDK
            except ImportError as exc:
                raise RuntimeError(
                    "مكتبة google-genai غير مثبّتة. نفّذ: pip install google-genai"
                ) from exc
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def supports(self, capability: str) -> bool:
        # يُستخدم كتحقق سريع بدون الحاجة لمعرفة model_id هنا — الفحص الدقيق
        # لكل موديل يمر عبر core.model_registry.require_capability.
        return capability in {
            "supports_pdf", "supports_search", "supports_structured_output",
            "supports_tools", "supports_thinking",
        }

    def generate(self, request: GenerationRequest) -> GenerationResult:
        model_info = get_model(request.model_id)

        if request.enable_search:
            require_capability(request.model_id, "supports_search")
        if request.documents:
            require_capability(request.model_id, "supports_pdf")
        if request.structured_schema:
            require_capability(request.model_id, "supports_structured_output")

        client = self._client_or_init()

        config: dict[str, Any] = {"temperature": request.temperature}
        if request.max_output_tokens:
            config["max_output_tokens"] = request.max_output_tokens
        if request.system:
            config["system_instruction"] = request.system
        tools = []
        if request.enable_search:
            tools.append({"google_search": {}})
        if tools:
            config["tools"] = tools

        start = time.monotonic()
        response = client.models.generate_content(
            model=model_info.model_id,
            contents=request.prompt,
            config=config,
        )
        duration_ms = int((time.monotonic() - start) * 1000)

        text = getattr(response, "text", "") or ""
        usage = getattr(response, "usage_metadata", None)
        tokens_in = getattr(usage, "prompt_token_count", 0) if usage else 0
        tokens_out = getattr(usage, "candidates_token_count", 0) if usage else 0

        search_sources: list[dict[str, Any]] = []
        grounding = getattr(response, "candidates", None)
        if grounding:
            for cand in grounding:
                meta = getattr(cand, "grounding_metadata", None)
                if meta and getattr(meta, "grounding_chunks", None):
                    for chunk in meta.grounding_chunks:
                        web = getattr(chunk, "web", None)
                        if web:
                            search_sources.append({
                                "url": getattr(web, "uri", None),
                                "title": getattr(web, "title", None),
                            })

        return GenerationResult(
            text=text,
            model_id=model_info.model_id,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            search_sources=search_sources,
            raw=response,
        )
