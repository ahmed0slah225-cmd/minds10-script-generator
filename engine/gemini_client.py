"""
engine/gemini_client.py
=========================
نقطة واحدة فقط لاستدعاء Gemini في المشروع كله. أي Engine أو Skill محتاج
يكلّم النموذج بيعدّي من هنا، مش بيعمل import مباشر لمكتبة google-generativeai
بنفسه — عشان لو غيّرنا الموديل أو أضفنا Retry/Logging، نغيّره في مكان واحد.

مفتاح الـAPI بيتقرأ بالترتيب التالي:
1) st.secrets["GEMINI_API_KEY"]   (لو شغال جوه Streamlit)
2) متغير البيئة GEMINI_API_KEY

لو مفيش مفتاح، الكلاينت بيرمي RuntimeError واضح بدل ما ياخد Exception
غامضة من المكتبة، عشان تعرف فورًا إن المشكلة في الإعداد مش في الكود.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from config import GEMINI_MODEL_NAME, GEMINI_TEMPERATURE_DEFAULT


def _read_api_key() -> str:
    try:
        import streamlit as st  # noqa: PLC0415

        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")


@dataclass
class GeminiClient:
    """
    Wrapper بسيط حوالين google-generativeai.
    كل الـSkills والـEngines بتستخدم دالة generate() بس، مش أي حاجة تانية
    من المكتبة مباشرة.
    """

    model_name: str = GEMINI_MODEL_NAME
    api_key: str = ""

    def __post_init__(self) -> None:
        self.api_key = self.api_key or _read_api_key()
        self._model = None  # يتحمّل Lazy عند أول استخدام فعلي

    def _ensure_model(self):
        if self._model is not None:
            return self._model
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY مش موجود. ضيفه في .streamlit/secrets.toml أو "
                "كمتغير بيئة قبل تشغيل التطبيق."
            )
        import google.generativeai as genai  # noqa: PLC0415

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model_name)
        return self._model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = GEMINI_TEMPERATURE_DEFAULT,
    ) -> str:
        model = self._ensure_model()
        full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
        response = model.generate_content(
            full_prompt,
            generation_config={"temperature": temperature},
        )
        return response.text
