"""
utils/pdf_reader.py
=====================
معالجة PDF ذكية (بند 49): لا يُعامل كـ Text Blob كامل. يستخرج فقط نطاق
الصفحات الذي حدده المستخدم.
"""

from __future__ import annotations
from typing import Tuple


def get_pdf_page_count(pdf_path: str) -> int:
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    return len(reader.pages)


def extract_pdf_text_range(pdf_path: str, page_start: int, page_end: int) -> str:
    """يستخرج نص الصفحات من page_start إلى page_end (1-indexed, شامل الطرفين)."""
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    start = max(1, page_start)
    end = min(total, page_end)

    texts = []
    for i in range(start - 1, end):
        try:
            texts.append(reader.pages[i].extract_text() or "")
        except Exception:
            continue
    return "\n\n".join(texts).strip()


def read_pdf_bytes(pdf_path: str) -> bytes:
    with open(pdf_path, "rb") as f:
        return f.read()
