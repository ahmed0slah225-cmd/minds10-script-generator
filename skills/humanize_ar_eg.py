"""
skills/humanize_ar_eg.py
=========================
مهارة الأنسنة (بند 11). تحسّن نصًا موجودًا فعلاً؛ لا تكتب من الصفر.
تعمل على: مستوى الجملة، الفقرة، الانتقالات، الإيقاع، التسليم المنطوق.
ممنوع: اختراع معلومات/تجارب/مصادر، أو تغيير المعنى الواقعي، أو الكتابة فوق الأدلة.
"""

from __future__ import annotations

from core.contracts import Skill, StepResult
from core.context import PipelineContext
from engines.common import call_llm, EGYPTIAN_ARABIC_STYLE_GUIDE

SYSTEM_PROMPT = f"""
أنت مهارة "الأنسنة" (Humanize). مهمتك تحسين نص سكريبت موجود بالفعل، وليس
كتابته من جديد. حسّن فقط: الإيقاع، طول الجمل، الانتقالات، الطبيعية، ومخاطبة
المشاهد.

قواعد صارمة لا يجوز خرقها إطلاقًا:
- لا تخترع معلومة أو تجربة شخصية أو مصدرًا أو اقتباسًا غير موجود في النص الأصلي.
- لا تغيّر أي حقيقة أو معنى واقعي.
- لا تحذف أي دليل أو معلومة مهمة.
- حافظ على بنية الأقسام كما هي، حسّن الصياغة فقط.

{EGYPTIAN_ARABIC_STYLE_GUIDE}

أعد النص الكامل بعد التحسين فقط، بدون أي تعليق أو مقدمة.
"""


class HumanizeSkill(Skill):
    name = "humanize_ar_eg"
    skill_type = "rewrite"
    execution_stage = "post_write"
    depends_on = ["voice_dna"]
    conflicts_with = []

    def run(self, ctx: PipelineContext, provider, **kwargs) -> StepResult:
        draft = ctx.draft_script
        if not draft:
            return StepResult(ok=False, error="لا توجد مسودة سكريبت لأنسنتها بعد.")

        user_prompt = f"""
النص المطلوب أنسنته:
\"\"\"{draft}\"\"\"

ملاحظات الحمض النووي الصوتي: {ctx.voice_dna.notes or "عامية مصرية طبيعية متوسطة."}
"""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)

        ctx.humanized_script = response.text
        return StepResult(ok=True, output=response.text)
