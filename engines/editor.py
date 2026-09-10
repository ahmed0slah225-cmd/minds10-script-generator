"""
engines/editor.py
===================
آخر محطة. لا يغيّر الفكرة الأساسية إطلاقًا. ياخد كل نتائج المراجعات
(اللهجة المصرية، اتساق البصمة الصوتية، المراجعة النهائية كمشاهد) ويخرج
ملف واحد: Final Script جاهز للتسجيل.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class EditorEngine(BaseEngine):
    name = "editor"
    persona = (
        "أنت 'المحرر النهائي' (Editor Engine). مهمتك دمج نتائج كل مراحل "
        "المراجعة السابقة في نسخة نهائية واحدة صالحة للتسجيل أمام الكاميرا. "
        "لا تغيّر الفكرة الأساسية أو المصادر أو الحقائق إطلاقًا - فقط اضبط "
        "أي نقاط محددة أشارت إليها المراجعة النهائية إن كانت ضرورية فعلًا."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        must_fix = []
        if not ctx.final_human_review.get("promise_fulfilled", True):
            must_fix.append("الوعد الأساسي للفيديو لم يتحقق بوضوح كافٍ - يجب تعزيزه في مكانه المناسب.")
        must_fix += ctx.final_human_review.get("drop_off_risk_points", [])
        must_fix += [i.get("suggestion", "") for i in ctx.voice_dna_consistency_report.get("issues", [])]

        if not must_fix:
            ctx.final_script = ctx.egyptian_edited_script
            return ctx

        prompt = f"""
النسخة شبه النهائية:
{ctx.egyptian_edited_script}

نقاط لازم تتعالج قبل الاعتماد كنسخة نهائية (بدون تغيير الفكرة أو الحقائق):
{must_fix}

أخرج النص النهائي الكامل فقط بعد معالجة هذه النقاط، بدون أي شرح إضافي.
"""
        ctx.final_script = self.call(prompt, json_mode=False, temperature=0.5)
        return ctx
