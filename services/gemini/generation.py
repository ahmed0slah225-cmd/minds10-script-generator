"""توليد Gemini المركزي: text / JSON مع معالجة أخطاء أساسية."""

from __future__ import annotations

import json
import time
from typing import Any, Optional

from google.genai import errors as genai_errors
from google.genai import types

from config.models import GenerationOptions, GenerationResult
from config.settings import get_settings
from services.gemini.errors import (
    GeminiModelError,
    GeminiQuotaError,
    GeminiServiceError,
)


def _friendly_error(exc: Exception) -> GeminiServiceError:
    code = getattr(exc, "code", None)

    if code == 429:
        return GeminiQuotaError(
            "وصلت لحصة Gemini الحالية. جرّب لاحقًا أو غيّر خطة/حدود المشروع.",
            code=429,
            original=exc,
        )

    if code == 404:
        return GeminiModelError(
            "موديل Gemini المحدد غير متاح للمفتاح الحالي.",
            code=404,
            original=exc,
        )

    if isinstance(exc, genai_errors.ServerError):
        return GeminiServiceError(
            f"حصل خطأ مؤقت من خوادم Gemini (كود {code or 503}).",
            code=code or 503,
            original=exc,
        )

    return GeminiServiceError(str(exc), code=code, original=exc)


def generate_text(
    client: Any,
    prompt: str,
    system_instruction: Optional[str] = None,
    options: Optional[GenerationOptions] = None,
    retries: int = 2,
) -> GenerationResult:
    settings = get_settings()
    opts = options or GenerationOptions()

    model = opts.model or settings.gemini_model
    config = types.GenerateContentConfig(
        system_instruction=system_instruction or None,
        max_output_tokens=opts.max_output_tokens or settings.gemini_max_output_tokens,
        temperature=opts.temperature if opts.temperature is not None else settings.gemini_temperature,
        response_mime_type=opts.response_mime_type,
        response_schema=opts.response_schema,
    )

    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            text = (getattr(response, "text", None) or "").strip()
            if not text:
                raise GeminiServiceError("Gemini رجّع استجابة فارغة.")

            usage: dict[str, Any] = {}
            metadata = getattr(response, "usage_metadata", None)
            if metadata is not None:
                for key in (
                    "prompt_token_count",
                    "candidates_token_count",
                    "total_token_count",
                ):
                    value = getattr(metadata, key, None)
                    if value is not None:
                        usage[key] = value

            return GenerationResult(
                text=text,
                model=model,
                raw_response=response,
                usage=usage,
            )
        except GeminiServiceError:
            raise
        except Exception as exc:
            last_error = exc
            friendly = _friendly_error(exc)
            if getattr(friendly, "code", None) == 503 and attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            raise friendly from exc

    raise _friendly_error(last_error or RuntimeError("فشل غير معروف"))


def generate_json(
    client: Any,
    prompt: str,
    system_instruction: Optional[str] = None,
    options: Optional[GenerationOptions] = None,
    retries: int = 2,
) -> Any:
    opts = options or GenerationOptions()
    opts = GenerationOptions(
        model=opts.model,
        temperature=opts.temperature,
        max_output_tokens=opts.max_output_tokens,
        response_mime_type="application/json",
        response_schema=opts.response_schema,
    )

    result = generate_text(
        client=client,
        prompt=prompt,
        system_instruction=system_instruction,
        options=opts,
        retries=retries,
    )

    try:
        return json.loads(result.text)
    except json.JSONDecodeError as exc:
        raise GeminiServiceError(
            f"Gemini رجّع JSON غير صالح. بداية الاستجابة: {result.text[:500]}"
        ) from exc
