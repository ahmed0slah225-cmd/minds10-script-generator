"""
llm/gemini_client.py
=====================
غلاف موحّد لاستدعاء Gemini API.

المبدأ: "تعدد العقول لا يعني بالضرورة تعدد الموديلات". فبنستخدم نفس الموديل
لكن بأدوار (Roles/Personas) مختلفة حسب الـ Engine أو الـ Skill المستدعية،
عن طريق تمرير system_instruction مختلفة لكل استدعاء.

لو ضبطت GEMINI_API_KEY في الـ Secrets، الاستدعاءات هتشتغل فعليًا.
لو مش متوفر، بيرجع خطأ واضح عشان الواجهة تظهره بدل ما تفشل بصمت.
"""

from __future__ import annotations

import os
import json
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:  # المكتبة قد لا تكون مثبتة وقت القراءة الأولى للكود
    genai = None


DEFAULT_MODEL = "gemini-2.0-flash"  # يمكن تغييره من config.py


class GeminiNotConfigured(RuntimeError):
    pass


def _get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
    return key


def _client():
    if genai is None:
        raise GeminiNotConfigured(
            "مكتبة google-generativeai غير مثبتة. أضفها في requirements.txt."
        )
    api_key = _get_api_key()
    if not api_key:
        raise GeminiNotConfigured(
            "GEMINI_API_KEY غير موجود. ضيفه في .streamlit/secrets.toml أو كمتغير بيئة."
        )
    genai.configure(api_key=api_key)
    return genai


def generate(
    system_instruction: str,
    user_prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.8,
    json_mode: bool = False,
    max_output_tokens: int = 8192,
) -> str:
    """استدعاء عام لـ Gemini. يرجع نص خام (أو JSON نصي لو json_mode=True)."""
    client = _client()
    generation_config = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if json_mode:
        generation_config["response_mime_type"] = "application/json"

    model_obj = client.GenerativeModel(
        model_name=model,
        system_instruction=system_instruction,
        generation_config=generation_config,
    )
    response = model_obj.generate_content(user_prompt)
    return response.text


def generate_json(system_instruction: str, user_prompt: str, *, model: str = DEFAULT_MODEL,
                   temperature: float = 0.5) -> dict:
    """نسخة تطلب من النموذج إخراج JSON منظم، وتحاول تحليله بأمان."""
    raw = generate(
        system_instruction=system_instruction,
        user_prompt=user_prompt + "\n\nأخرج JSON فقط بدون أي شرح إضافي وبدون ```.",
        model=model,
        temperature=temperature,
        json_mode=True,
    )
    cleaned = raw.strip().strip("`")
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # فشل التحليل - نرجّع النص الخام جوه مفتاح عشان ما نضيعش المحتوى
        return {"_raw": raw, "_parse_error": True}
