"""
engine/engines/pdf_engine.py
------------------------------
طبقة معمارية مستقلة للتعامل مع PDF نصي، بحيث النظام يفهم الصفحات
كصفحات فعلية وليس كنص طويل واحد. ده يحل المشكلة اللي ذُكرت في مواصفة
المشروع: "النظام الحالي يحول الـ PDF إلى نص متصل من غير طبقة فهم نطاق
صفحات حقيقية".

يعتمد على pypdf (خفيف، بدون تبعيات تانية) لاستخراج نص كل صفحة على حدة.
"""

from __future__ import annotations
from typing import List, Tuple

from config import MAX_PDF_PAGES_PER_REQUEST


def inspect_pdf(file_path: str) -> dict:
    """يرجّع معلومات أساسية عن الملف: عدد الصفحات، وهل فيه نص قابل للاستخراج."""
    from pypdf import PdfReader
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    sample_text = ""
    for page in reader.pages[: min(3, total_pages)]:
        sample_text += (page.extract_text() or "")
    has_extractable_text = len(sample_text.strip()) > 20
    return {
        "total_pages": total_pages,
        "has_extractable_text": has_extractable_text,
    }


def extract_page_range(file_path: str, start_page: int, end_page: int) -> Tuple[str, List[int]]:
    """
    يستخرج نص نطاق صفحات محدد (1-indexed زي ما المستخدم بيكتبها) بدل
    الكتاب كله. يرجع النص مع أرقام الصفحات اللي فعليًا فيها نص.

    الحماية: لو النطاق المطلوب أكبر من MAX_PDF_PAGES_PER_REQUEST،
    بنقصّه ونرجّع تنبيه ضمن النص عشان الـ caller يقدر يعلم المستخدم.
    """
    from pypdf import PdfReader
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)

    start_page = max(1, start_page)
    end_page = min(total_pages, end_page)
    if end_page < start_page:
        raise ValueError("نطاق الصفحات غير صالح: صفحة النهاية أصغر من صفحة البداية.")

    truncated = False
    if (end_page - start_page + 1) > MAX_PDF_PAGES_PER_REQUEST:
        end_page = start_page + MAX_PDF_PAGES_PER_REQUEST - 1
        truncated = True

    chunks = []
    pages_with_text = []
    for page_num in range(start_page, end_page + 1):
        page = reader.pages[page_num - 1]  # PdfReader is 0-indexed
        text = (page.extract_text() or "").strip()
        if text:
            pages_with_text.append(page_num)
            chunks.append(f"--- صفحة {page_num} ---\n{text}")

    full_text = "\n\n".join(chunks)
    if truncated:
        full_text += (
            f"\n\n[ملاحظة نظام: النطاق المطلوب أكبر من الحد الأقصى "
            f"({MAX_PDF_PAGES_PER_REQUEST} صفحة لكل طلب)، تم الاكتفاء "
            f"بالصفحات من {start_page} إلى {end_page}. اطلب باقي النطاق "
            f"في مرحلة لاحقة.]"
        )
    return full_text, pages_with_text
