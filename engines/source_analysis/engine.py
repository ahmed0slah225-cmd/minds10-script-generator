"""
engines/source_analysis/engine.py
====================================
خط أنابيب PDF — القسم 49.

يتعامل مع الـPDF كملف له صفحات، مش Text Blob. لو المستخدم قال
"من صفحة 1 لـ20"، لازم يتقرأ النطاق ده بالظبط، مش الكتاب كله.

هذه مهارة/محرك حتمي بالكامل (لا يحتاج LLM) — استخراج نص خام فقط.
أي تلخيص أو تحليل للمحتوى المُستخرج يحصل لاحقًا في محرك المعرفة
(engines/knowledge/engine.py)، مش هنا — فصل واضح بين "الاستخراج"
و"الفهم"، بنفس روح القسم 49.

إذا لم تتوفر مكتبة قراءة PDF في البيئة، يفشل بوضوح بدل التظاهر بالنجاح.
"""

from __future__ import annotations

from core.context import PipelineContext, SourceRef


def _extract_pages(pdf_path: str, start_page: int, end_page: int) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "مكتبة pypdf غير مثبّتة. نفّذ: pip install pypdf"
        ) from exc

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    if start_page < 1 or end_page > total_pages or start_page > end_page:
        raise ValueError(
            f"نطاق الصفحات ({start_page}-{end_page}) غير صالح. "
            f"الملف فيه {total_pages} صفحة فقط."
        )

    texts = []
    for i in range(start_page - 1, end_page):
        page_text = reader.pages[i].extract_text() or ""
        texts.append(page_text)
    return "\n\n".join(texts)


def run(ctx: PipelineContext, *, model_id: str) -> None:
    input_profile = ctx.constraints.get("input_profile", {})
    if not input_profile.get("requires_source_analysis"):
        # مفيش PDF مرفق أصلًا — المرحلة دي مش لازمة (القاعدة: لا تعالج
        # ما لا يوجد سبب لمعالجته)
        return

    pdf_path = ctx.constraints["pdf_path"]
    page_range = ctx.constraints.get("page_range")  # tuple (start, end) أو None = الكتاب كله

    if page_range is None:
        # تحذير صريح بدل معالجة الكتاب كله ضمنيًا دون علم المستخدم
        raise ValueError(
            "لم يُحدَّد نطاق صفحات (page_range) لملف الـPDF. حدّد النطاق "
            "المطلوب صراحة (مثال: من صفحة 1 إلى 20) قبل المتابعة، تنفيذًا "
            "للقاعدة: لا تعالج الكتاب كله في كل طلب."
        )

    start_page, end_page = page_range
    text = _extract_pages(pdf_path, start_page, end_page)

    ctx.sources.append(SourceRef(
        origin="user_pdf",
        content=text,
        is_primary=True,   # القسم 24: مصدر المستخدم يظل الأساسي دائمًا
        trust_level="verified",
        page_range=(start_page, end_page),
    ))

    ctx.log_run(engine="source_analysis", skill=None, model_id=None, status="passed")
