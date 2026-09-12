"""
engines/editor_engine.py
==========================
التحرير النهائي (بند 43/58): مراجعة منفصلة عن إعادة الكتابة.
يطبّق فقط الإصلاحات المستهدفة القادمة من anti_slop_report وتقرير الاحتفاظ،
ولا يعيد بناء السكريبت كاملاً. "الحد الأدنى من التحرير الفعال" (بند 15):
لا تعدّل شيئًا إلا لو التعديل له فائدة واضحة.
"""

from __future__ import annotations
import json

from core.contracts import Engine, StepResult
from core.context import PipelineContext
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت "المحرر النهائي". أمامك نص سكريبت، وقائمة مشاكل محددة (من مراجعة مكافحة
الانزلاق والاحتفاظ). طبّق فقط الإصلاحات ذات الفائدة الواضحة، بأقل تعديل
ممكن على الجملة أو الفقرة المعنية. لا تعيد صياغة أي جزء سليم لمجرد إعادة
الصياغة. لا تغيّر المعنى أو الحقائق أو الأدلة أو الحمض النووي الصوتي.

أعد النص الكامل بعد التحرير المستهدف فقط، بدون أي تعليق.
"""


class EditorEngine(Engine):
    name = "editor_engine"
    stage = "final_edit"

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        text = ctx.humanized_script or ctx.draft_script
        if not text:
            return StepResult(ok=False, error="لا يوجد نص لتحريره.")

        issues = ctx.anti_slop_report.get("issues", []) if isinstance(ctx.anti_slop_report, dict) else []
        high_priority = [i for i in issues if i.get("priority") in ("عالية", "متوسطة")]

        if not high_priority:
            # لا توجد مشاكل تستحق التعديل: اتركه كما هو (بند 15)
            ctx.final_script = text
            return StepResult(ok=True, output=text, warnings=["لم يتم العثور على مشاكل ذات أولوية تستدعي التعديل."])

        issues_text = "\n".join(
            f"- المشكلة: {i.get('problem')} | الإصلاح المقترح: {i.get('suggested_fix')} | الموقع: {i.get('location_hint')}"
            for i in high_priority
        )

        user_prompt = f"""
النص:
\"\"\"{text}\"\"\"

الإصلاحات المطلوب تطبيقها فقط (تجاهل أي شيء غير مذكور هنا):
{issues_text}
"""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)

        ctx.final_script = response.text
        return StepResult(ok=True, output=response.text)
