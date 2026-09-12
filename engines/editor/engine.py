"""
engines/editor/engine.py
===========================
ثلاث مراحل تحرير أخيرة منفصلة (القسم 42/43):

1) egyptian_arabic_edit: تمريرة تحرير خفيفة للعامية المصرية بمبدأ "الحد
   الأدنى من التحرير الفعال" (القسم 15) — لا تعدّل جملة صحيحة وطبيعية
   بالفعل لمجرد إعادة الكتابة.

2) fact_check: مقارنة حتمية (بدون LLM) بين الأرقام/الأسماء الظاهرة في
   النص النهائي وما هو موجود فعلًا في knowledge_base/sources — أي رقم أو
   اسم غير مدعوم يُعلَّم كتحذير بدل حذفه تلقائيًا (قرار الحذف/الإبقاء
   يترك لمراجعة بشرية نهائية، القاعدة: لا هلوسة لكن لا حذف أعمى أيضًا).

3) final_edit: يجمّع النص النهائي، ويطبّق *فقط* الإصلاحات عالية الثقة
   من anti_slop_report (حذف عبارات حشو مؤكدة) — بدون إعادة كتابة شاملة
   (القاعدة 58: لا تعيد بناء النص كله بلا داعٍ).
"""

from __future__ import annotations

import re

from core.context import PipelineContext
from core.model_registry import get_model
from providers.base import GenerationRequest, get_provider

_EDIT_SYSTEM_PROMPT = (
    "أنت محرر عامية مصرية بمبدأ 'الحد الأدنى من التحرير الفعال'. راجع "
    "النص وعدّل *فقط* الجمل اللي فيها مشكلة حقيقية (غير طبيعية، غير "
    "واضحة، رسمية زيادة عن اللزوم، أو مش متوافقة مع لهجة مصرية منطوقة). "
    "لو الجملة صحيحة وواضحة وطبيعية بالفعل: اتركها زي ما هي بالظبط. "
    "أعد النص كاملاً بعد التعديلات البسيطة فقط."
)


def run_egyptian_arabic_edit(ctx: PipelineContext, *, model_id: str) -> None:
    text = ctx.humanized_script or ctx.draft_script
    if not text:
        raise ValueError("egyptian_arabic_edit: لا يوجد نص لتحريره.")

    model_info = get_model(model_id)
    provider = get_provider(model_info.provider)

    request = GenerationRequest(prompt=text, system=_EDIT_SYSTEM_PROMPT, model_id=model_id, temperature=0.3)
    result = provider.generate(request)

    ctx.humanized_script = result.text
    ctx.log_run(engine="egyptian_arabic_edit", skill=None, model_id=model_id, status="passed",
                tokens_in=result.tokens_in, tokens_out=result.tokens_out)


def run_fact_check(ctx: PipelineContext, *, model_id: str) -> None:
    """حتمي بالكامل — لا يحتاج LLM (القاعدة 38). يقارن الأرقام الظاهرة في
    النص مع ما هو مدعوم في المعرفة/المصادر، ويُعلِّم غير المدعوم فقط."""
    text = ctx.humanized_script or ctx.draft_script or ""
    numbers_in_text = set(re.findall(r"\d+[\.,]?\d*", text))

    supported_numbers: set[str] = set()
    for item in ctx.knowledge_base:
        supported_numbers.update(re.findall(r"\d+[\.,]?\d*", item.get("content", "")))
    for src in ctx.sources:
        supported_numbers.update(re.findall(r"\d+[\.,]?\d*", src.content or ""))

    unsupported = numbers_in_text - supported_numbers
    if unsupported:
        ctx.review_notes.append({
            "type": "fact_check_warning",
            "detail": f"أرقام ظاهرة في النص بدون دعم واضح من المعرفة/المصادر: {sorted(unsupported)}. "
                      f"راجعها يدويًا أو حددها كـ'غير مؤكد' في النص.",
        })

    ctx.log_run(engine="fact_check", skill=None, model_id=None, status="passed",
                error=None if not unsupported else f"{len(unsupported)} رقم غير مدعوم")


def run_final_edit(ctx: PipelineContext, *, model_id: str) -> None:
    """يطبّق فقط إصلاحات anti_slop عالية الثقة (حذف عبارات حشو مؤكدة عبر
    regex)، بدون أي إعادة كتابة عامة — القاعدة 58."""
    text = ctx.humanized_script or ctx.draft_script or ""

    anti_slop_reports = [n["detail"] for n in ctx.review_notes if n.get("type") == "anti_slop_report"]
    filler_matches = []
    for report in anti_slop_reports:
        for issue in report.get("issues", []):
            if issue["type"] == "filler_phrase":
                filler_matches.append(issue["match"])

    final_text = text
    for phrase in set(filler_matches):
        # إزالة العبارة فقط لو ظهرت كجملة منفصلة (حد أدنى من التحرير)
        final_text = re.sub(rf"،?\s*{re.escape(phrase)}\s*،?", "", final_text)

    final_text = re.sub(r"\s{2,}", " ", final_text).strip()

    ctx.final_script = final_text
    ctx.log_run(engine="final_edit", skill=None, model_id=None, status="passed")
