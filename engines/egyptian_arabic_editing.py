"""
engines/egyptian_arabic_editing.py
=====================================
بعد ما نجمع ملاحظات Humanization و Anti-Slop و Retention Review و
Repetition Review، المحرك ده بيطبق التعديلات المقترحة فعليًا، وبيظبط
اللهجة المصرية بحيث تكون طبيعية من غير مبالغة أو ركاكة، مع الحفاظ التام
على المعنى والمصادر.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class EgyptianArabicEditingEngine(BaseEngine):
    name = "egyptian_arabic_editing"
    persona = (
        "أنت 'محرر اللهجة المصرية' (Egyptian Arabic Editor). مهمتك تطبيق "
        "مجموعة ملاحظات مراجعة محددة على نص موجود بالفعل، وضبط اللهجة "
        "المصرية لتكون طبيعية ومفهومة - لا فصحى جامدة ولا عامية مبالغ فيها. "
        "الأولوية: المعنى أولًا، ثم الوضوح، ثم الإنسانية، ثم الإيقاع. "
        "ممنوع حذف أي معلومة أو مصدر أو تغيير الفكرة الأساسية."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        issues = []
        issues += ctx.anti_slop_report.get("issues", [])
        issues += ctx.retention_review.get("issues", [])
        issues += ctx.repetition_review.get("issues", [])

        prompt = f"""
النص الحالي (بعد الإنسنة):
{ctx.humanized_script}

ملاحظات المراجعة المطلوب تطبيقها (بدون حذف أي معلومة أو مصدر):
{issues}

المطلوب: أعد كتابة النص كاملًا مع تطبيق التعديلات المناسبة فقط من
الملاحظات أعلاه، وضبط اللهجة المصرية لتكون طبيعية ومتسقة الإيقاع.
احتفظ بكل الأفكار والحقائق والمصادر كما هي بالضبط.
أخرج النص النهائي فقط بدون أي شرح.
"""
        ctx.egyptian_edited_script = self.call(prompt, json_mode=False, temperature=0.6)
        return ctx
