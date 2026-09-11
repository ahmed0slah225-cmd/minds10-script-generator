"""
engine/gemini_client.py
------------------------
غلاف موحّد لاستدعاء Gemini. كل الـ Engines والـ Skills بتنادي على
`generate()` أو `generate_json()` من هنا بدل ما كل ملف يبني اتصاله
الخاص. ده اللي بيخلينا نقدر نغيّر الموديل أو نضيف caching لاحقًا
من مكان واحد بس.
"""

from __future__ import annotations
import json
import time
from typing import Optional, Dict, Any

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MODEL_DEEP

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY غير موجود. ضيفه في Environment Variables محليًا "
            "أو في st.secrets على Streamlit Cloud."
        )
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    _client = genai
    return _client


def generate(
    prompt: str,
    system_instruction: Optional[str] = None,
    deep: bool = False,
    temperature: float = 0.8,
    max_retries: int = 3,
) -> str:
    """نداء نصي بسيط. يرجّع نص خام."""
    genai = _get_client()
    model_name = GEMINI_MODEL_DEEP if deep else GEMINI_MODEL
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
    )
    last_err = None
    for attempt in range(max_retries):
        try:
            resp = model.generate_content(
                prompt,
                generation_config={"temperature": temperature},
            )
            return (resp.text or "").strip()
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"فشل الاتصال بـ Gemini بعد {max_retries} محاولات: {last_err}")


def generate_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    deep: bool = False,
    temperature: float = 0.4,
) -> Dict[str, Any]:
    """
    نداء لمخرجات JSON منظمة (تستخدمه محركات زي Review / Anti-Slop / Knowledge).
    بيضيف تعليمة صارمة إن الرد JSON فقط، وبيحاول ينظف أي fencing زيادة.
    """
    strict_prompt = (
        f"{prompt}\n\n"
        "مهم جدًا: رد بصيغة JSON صالحة فقط، بدون أي شرح قبلها أو بعدها، "
        "وبدون ```json في البداية أو ``` في النهاية."
    )
    raw = generate(strict_prompt, system_instruction=system_instruction, deep=deep, temperature=temperature)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # محاولة أخيرة: نلقط أول { ... } في النص
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                pass
        return {"_raw": raw, "_parse_error": True}
