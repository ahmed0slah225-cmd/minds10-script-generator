"""
utils/pdf_utils.py
=====================
طبقة "Document Intelligence" — التعامل مع الـPDF كصفحات، مش كنص متصل
واحد. النسخة دي بتدعم PDF نصي فقط (مفيش OCR في هذه النسخة، زي ما حددت
في المواصفة).

ده اللي بيحل بالظبط المشكلة المذكورة في المواصفة: "النظام الحالي يحول
الـPDF لنص متصل ثم يبنيه في Context" — هنا كل صفحة موجودة منفصلة،
فتقدر تطلب "من صفحة 1 لـ20" وتاخد بالظبط النطاق ده.
"""

from __future__ import annotations

from dataclasses import dataclass

from config import MAX_PDF_PAGES_PER_REQUEST


@dataclass
class PdfPage:
    page_number: int  # 1-indexed زي ما المستخدم بيتكلم عادي
    text: str


@dataclass
class PdfDocument:
    total_pages: int
    pages: list[PdfPage]

    def get_range(self, start_page: int, end_page: int) -> list[PdfPage]:
        """
        بيرجّع الصفحات من start_page لـ end_page (شاملة الطرفين، 1-indexed).
        لو النطاق أكبر من MAX_PDF_PAGES_PER_REQUEST بيقصّه ويرجّع تحذير
        عن طريق الاستثناء، عشان الطلب يتقسّم بدل ما يبعت كتاب كامل
        لـGemini في مرة واحدة.
        """
        if start_page < 1 or end_page > self.total_pages or start_page > end_page:
            raise ValueError(
                f"نطاق الصفحات غير صالح: الكتاب فيه {self.total_pages} صفحة، "
                f"والمطلوب من {start_page} لـ{end_page}."
            )
        span = end_page - start_page + 1
        if span > MAX_PDF_PAGES_PER_REQUEST:
            raise ValueError(
                f"النطاق المطلوب ({span} صفحة) أكبر من الحد الأقصى "
                f"({MAX_PDF_PAGES_PER_REQUEST} صفحة) في الطلب الواحد. "
                f"قسّم الطلب لأكتر من نطاق أصغر."
            )
        return [p for p in self.pages if start_page <= p.page_number <= end_page]

    def range_text(self, start_page: int, end_page: int) -> str:
        pages = self.get_range(start_page, end_page)
        return "\n\n".join(f"[صفحة {p.page_number}]\n{p.text}" for p in pages)


def load_pdf(file_path: str) -> PdfDocument:
    """
    يقرأ ملف PDF نصي ويحوّله لـPdfDocument بصفحات منفصلة.
    لو الملف مفيهوش نص قابل للاستخراج (يعني كتاب ممسوح ضوئيًا/Scanned)،
    بيرمي ValueError واضح بدل ما يرجّع صفحات فاضية بصمت.
    """
    from pypdf import PdfReader  # noqa: PLC0415

    reader = PdfReader(file_path)
    pages: list[PdfPage] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        pages.append(PdfPage(page_number=i, text=text))

    non_empty = [p for p in pages if p.text]
    if not non_empty:
        raise ValueError(
            "مفيش نص قابل للاستخراج من الـPDF ده — على الأرجح كتاب ممسوح "
            "ضوئيًا (Scanned). النسخة الحالية بتدعم PDF نصي فقط."
        )
    return PdfDocument(total_pages=len(pages), pages=pages)
