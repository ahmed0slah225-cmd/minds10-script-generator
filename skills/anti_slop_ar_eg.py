"""
skills/anti_slop_ar_eg.py
===========================
مهارة مكافحة الانزلاق (بند 13/14). "المراجع أولاً" وليس كاتبًا أعمى:
تحليل → نتيجة → تحديد المشاكل → شرح → اقتراح إصلاحات → المحرر يطبق الصالح فقط.
تعيد تقييمًا منظمًا برقم من 1-10 لكل بُعد: الطبيعية، كثافة المعلومات،
الوضوح، قوة اللغة، الإحساس بالـAI.
"""

from __future__ import annotations
import json

from core.contracts import Skill, StepResult
from core.context import PipelineContext
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت مراجع "مكافحة الانزلاق" (Anti-Slop) لسكريبت يوتيوب مصري. أنت مراجع، لست
كاتبًا. لا تعيد كتابة النص؛ فقط حلّله وأنتج تقريرًا.

ابحث عن: الحشو، العموميات، الكلام العميق الفارغ، التكرار، الانتقالات
الجاهزة، اللغة الرسمية الزائدة، التعميم، الصياغة الآلية، الجمل التي تُخبر
المشاهد بما يشعر به بدل إظهار الموقف.

أعد JSON فقط بهذا الشكل بالضبط:
{
  "scores": {
    "naturalness": 0,
    "information_density": 0,
    "clarity": 0,
    "language_strength": 0,
    "ai_feel": 0
  },
  "issues": [
    {"location_hint": "...", "problem": "...", "suggested_fix": "...", "priority": "عالية|متوسطة|منخفضة"}
  ]
}
كل درجة من 1 إلى 10 (10 = أفضل، أي أن ai_feel=10 يعني لا يبدو مكتوبًا بالذكاء الاصطناعي إطلاقًا).
"""


class AntiSlopSkill(Skill):
    name = "anti_slop_ar_eg"
    skill_type = "review"
    execution_stage = "review"
    depends_on = []
    conflicts_with = []

    def run(self, ctx: PipelineContext, provider, **kwargs) -> StepResult:
        text = ctx.humanized_script or ctx.draft_script
        if not text:
            return StepResult(ok=False, error="لا يوجد نص لمراجعته.")

        user_prompt = f"النص المطلوب مراجعته:\n\"\"\"{text}\"\"\""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)

        try:
            data = json.loads(response.text.strip().strip("```json").strip("```").strip())
        except Exception:
            data = {"raw_response": response.text}

        ctx.anti_slop_report = data
        return StepResult(ok=True, output=data)
