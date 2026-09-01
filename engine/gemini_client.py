# -*- coding: utf-8 -*-
"""
engine/gemini_client.py

طبقة واحدة لكل نداءات Gemini API، مستخدمة من كل مراحل خط الإنتاج
(engine/pipeline.py) عشان منكررش منطق الـ retry وتحليل الـ JSON في كل
مكان. الملف ده معندوش أي منطق خاص بمرحلة معيّنة - كله عام.
"""

import json
import re
import time

from google import genai
from google.genai import types
from google.genai import errors as genai_errors


class GenerationError(Exception):
    """خطأ عام بيتلف حوله أي استثناء من الـ API مع رسالة عربية مفهومة."""

    def __init__(self, message: str, code=None, original: Exception = None):
        super().__init__(message)
        self.code = code
        self.original = original


def make_client(api_key: str):
    return genai.Client(api_key=api_key)


def _friendly_error(e: Exception) -> GenerationError:
    if isinstance(e, genai_errors.ServerError):
        if getattr(e, "code", None) == 503:
            return GenerationError(
                "🔧 سيرفرات Gemini مزنوقة مؤقتًا بسبب ضغط استخدام كبير. جرب تاني بعد شوية، "
                "أو غيّر الموديل من الشريط الجانبي.", code=503, original=e,
            )
        return GenerationError(f"حصل خطأ من سيرفر الـ API (كود {getattr(e, 'code', '؟')}): {e}",
                                code=getattr(e, "code", None), original=e)
    if isinstance(e, genai_errors.APIError):
        code = getattr(e, "code", None)
        if code == 429:
            return GenerationError(
                "⏳ وصلت لحد الحصة المجانية (Quota) بتاعة مفتاح الـ Gemini API دلوقتي. "
                "فعّل Billing على مشروعك في Google AI Studio أو جرب تاني بعد شوية.",
                code=429, original=e,
            )
        if code == 404:
            return GenerationError(
                "🚫 النموذج ده مش متاح للمفتاح بتاعك. اختار موديل تاني من الشريط الجانبي.",
                code=404, original=e,
            )
        return GenerationError(f"حصل خطأ من الـ API (كود {code}): {e}", code=code, original=e)
    return GenerationError(f"حصل خطأ غير متوقع: {e}", original=e)


def call_text(client, model: str, system_instruction: str, user_prompt: str,
              max_output_tokens: int = 8000, max_attempts: int = 3) -> str:
    """بينادي الموديل ويرجع نص عادي (مش JSON)."""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=max_output_tokens,
    )
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(model=model, contents=user_prompt, config=config)
            return response.text or ""
        except genai_errors.ServerError as e:
            last_error = e
            if getattr(e, "code", None) == 503 and attempt < max_attempts:
                time.sleep(5 * attempt)
                continue
            raise _friendly_error(e)
        except Exception as e:
            raise _friendly_error(e)
    raise _friendly_error(last_error)


def call_json(client, model: str, system_instruction: str, user_prompt: str,
              max_output_tokens: int = 8000, max_attempts: int = 3):
    """بينادي الموديل بطلب صريح لمخرجات JSON، وبيرجّع dict/list جاهز.
    بيستخدم response_mime_type='application/json' لتقليل احتمال إن
    الموديل يرجع نص زيادة حوالين الـ JSON."""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=max_output_tokens,
        response_mime_type="application/json",
    )
    last_error = None
    raw_text = ""
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(model=model, contents=user_prompt, config=config)
            raw_text = response.text or ""
            return safe_json_parse(raw_text)
        except genai_errors.ServerError as e:
            last_error = e
            if getattr(e, "code", None) == 503 and attempt < max_attempts:
                time.sleep(5 * attempt)
                continue
            raise _friendly_error(e)
        except json.JSONDecodeError:
            if attempt < max_attempts:
                continue
            raise GenerationError(f"الموديل رجّع رد مش JSON صحيح بعد {max_attempts} محاولات:\n{raw_text[:500]}")
        except Exception as e:
            raise _friendly_error(e)
    raise _friendly_error(last_error)


def safe_json_parse(text: str):
    """بيشيل ```json fences أو أي نص زيادة حوالين الـ JSON قبل ما يعمل parse."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned.strip(), flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned.strip()).strip()
    # لو لسه فيه نص قبل أول { أو [ أو بعد آخر } أو ]، حاول تقص عليه
    start_candidates = [i for i in (cleaned.find("{"), cleaned.find("[")) if i != -1]
    if start_candidates:
        start = min(start_candidates)
        end_brace = cleaned.rfind("}")
        end_bracket = cleaned.rfind("]")
        end = max(end_brace, end_bracket)
        if start > 0 or end < len(cleaned) - 1:
            cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)
