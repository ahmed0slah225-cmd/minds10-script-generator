"""
engine/input_router.py
=========================
مرحلة "Input Intelligence". مش كل حاجة هنا محتاجة Gemini — تصنيف نوع
المدخل (عنوان / فكرة / سؤال / نص / PDF / رابط) منطق بسيط، وده بيوفر
نداء Gemini كامل مش لازم.
"""

from __future__ import annotations

from engine.models import SourceItem, new_id


def classify_source(raw_text: str = "", file_path: str = "", url: str = "") -> SourceItem:
    if file_path:
        kind = "pdf"
    elif url:
        kind = "url"
    elif raw_text:
        stripped = raw_text.strip()
        if stripped.endswith("؟") or stripped.endswith("?"):
            kind = "question"
        elif len(stripped.split()) <= 12:
            kind = "title"
        else:
            kind = "idea" if len(stripped) < 400 else "text"
    else:
        raise ValueError("لازم تديني حاجة واحدة على الأقل: نص أو ملف أو رابط.")

    return SourceItem(
        id=new_id("src"),
        kind=kind,
        raw_text=raw_text,
        file_path=file_path,
        url=url,
        title=raw_text[:80] if kind in ("title", "idea", "question") else "",
    )
