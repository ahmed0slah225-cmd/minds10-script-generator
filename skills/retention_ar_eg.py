"""
skills/retention_ar_eg.py
============================
مهارة الاحتفاظ (بند 12). ليست Hook Skill فقط، بل تراجع منظومة الاحتفاظ
الكاملة: كل سؤال مهم يُفتح يجب أن يحصل على Payoff مناسب. ممنوع الـ Clickbait
والفضول الفارغ والـ Open Loops بلا إغلاق.
"""

from __future__ import annotations
import json

from core.contracts import Skill, StepResult
from core.context import PipelineContext
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت مهارة "الاحتفاظ" (Retention) لسكريبت يوتيوب. راجع السكريبت بحثًا عن:
- أسئلة/فضول تم فتحه ولم يُغلق (Open Loops بلا Payoff).
- تشويق وهمي أو Clickbait لا يفي به النص.
- نقاط في منتصف الفيديو قد يفقد فيها المشاهد اهتمامه (زخم ضعيف).

لا تعيد كتابة النص. أعد فقط JSON:
{
  "open_loops_without_payoff": ["..."],
  "weak_momentum_points": ["..."],
  "clickbait_risk": ["..."],
  "overall_retention_note": "..."
}
"""


class RetentionSkill(Skill):
    name = "retention_ar_eg"
    skill_type = "review"
    execution_stage = "review"
    depends_on = []
    conflicts_with = []

    def run(self, ctx: PipelineContext, provider, **kwargs) -> StepResult:
        text = ctx.humanized_script or ctx.draft_script
        if not text:
            return StepResult(ok=False, error="لا يوجد نص لمراجعة الاحتفاظ فيه.")

        user_prompt = f"النص:\n\"\"\"{text}\"\"\""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)

        try:
            data = json.loads(response.text.strip().strip("```json").strip("```").strip())
        except Exception:
            data = {"overall_retention_note": response.text}

        return StepResult(ok=True, output=data)
