"""طبقة إنشاء Gemini client."""

from __future__ import annotations

from typing import Optional

from google import genai

from config.settings import get_settings
from services.gemini.errors import GeminiConfigurationError


def make_client(api_key: Optional[str] = None):
    settings = get_settings()
    key = api_key or settings.gemini_api_key
    if not key:
        raise GeminiConfigurationError("مفتاح Gemini غير مضبوط. أضف GEMINI_API_KEY في Secrets.")
    return genai.Client(api_key=key)
