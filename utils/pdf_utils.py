"""
utils/pdf_utils.py
====================
التعامل مع الـ PDF كمصدر معرفي مرتبط بالصفحات، مش كنص طويل بيتبعت كامل
في كل مرة. لو المستخدم حدد نطاق صفحات (مثلاً "1-20")، بنستخرج النطاق ده
بس.
"""

from __future__ import annotations

import re


def parse_page_range(range_str: str, total_pages: int) -> tuple[int, int]:
    """يحوّل '1-20' أو '15' إلى (start, end) بترقيم يبدأ من 1، محدود بعدد الصفحات."""
    range_str = (range_str or "").strip()
    if not range_str:
        return 1, total_pages
    match = re.match(r"^(\d+)\s*-\s*(\d+)$", range_str)
    if match:
        start, end = int(match.group(1)), int(match.group(2))
    else:
        try:
            start = end = int(range_str)
        except ValueError:
            return 1, total_pages
    start = max(1, start)
    end = min(total_pages, end)
    if start > end:
        start, end = end, start
    return start, end


def extract_pdf_text(file_path: str, page_range: str = "") -> tuple[str, int]:
    """
    يرجع (النص المستخرج, عدد صفحات الملف الكلي).
    لو page_range فاضي بيرجع الكتاب كامل (احترس من الحجم مع الكتب الكبيرة).
    """
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    start, end = parse_page_range(page_range, total_pages)

    chunks = []
    for i in range(start - 1, end):
        page = reader.pages[i]
        chunks.append(page.extract_text() or "")
    return "\n\n".join(chunks), total_pages
