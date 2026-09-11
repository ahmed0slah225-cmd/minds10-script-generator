"""
engine/review_engine.py
==========================
بيغطي مرحلتين من الـWorkflow: "Anti-Slop Review" و "Repetition Review".
الاتنين Review-only — بيرجعوا قوائم مشاكل، ومبيعدلوش السكريبت بنفسهم.
الـEditor Engine هو الوحيد اللي بيطبّق التصحيحات، في نداء واحد نهائي.

ده التطبيق الفعلي لقاعدة "Review ≠ Rewrite" اللي بتمنع تكرار نداءات
Gemini وتكرار إعادة الكتابة.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext, ReviewFinding
from skills import StopSlopSkill
from skills.base import SkillResult

_REPETITION_SYSTEM_PROMPT = """أنت مراجع تكرار متخصص في سكريبتات يوتيوب
باللهجة المصرية. مهمتك: اكتشاف إن نفس الفكرة اتقالت أكتر من مرة بصياغات
مختلفة عبر السكريبت (مش تكرار الكلمة نفسها — تكرار المعنى).

الهدف مش حذف كل تكرار؛ بعض التكرار مفيد للتأكيد. المطلوب فقط رصد
"التكرار الكسول": نفس الفكرة بالظبط بتتقال تالت أو رابع مرة من غير
إضافة حقيقية.

أعد ردك بصيغة JSON فقط:
{
  "repeated_ideas": [
    {"idea": "...", "occurrences": ["اقتباس أقل من 15 كلمة", "اقتباس أقل من 15 كلمة"], "keep_first_only": true}
  ]
}"""


class ReviewEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.llm = llm or GeminiClient()
        self.stop_slop = StopSlopSkill(llm)

    def run_anti_slop(self, script_text: str, known_facts: list[str]) -> ReviewFinding:
        result = self.stop_slop.run(script_text, known_facts=known_facts)
        if not result.ok:
            return ReviewFinding(review_type="anti_slop", raw={"error": result.error})
        return ReviewFinding(
            review_type="anti_slop",
            score=result.data.get("total_score"),
            issues=result.data.get("issues", []),
            raw=result.data,
        )

    def run_repetition_review(self, script_text: str) -> ReviewFinding:
        raw = self.llm.generate(_REPETITION_SYSTEM_PROMPT, f"السكريبت:\n\n{script_text}", temperature=0.2)
        result = SkillResult.parse_json("repetition_review", "review", raw)
        if not result.ok:
            return ReviewFinding(review_type="repetition", raw={"error": result.error})
        return ReviewFinding(
            review_type="repetition",
            issues=result.data.get("repeated_ideas", []),
            raw=result.data,
        )

    def run_all(self, ctx: ProjectContext, script_text: str) -> ProjectContext:
        anti_slop = self.run_anti_slop(script_text, ctx.confirmed_facts())
        repetition = self.run_repetition_review(script_text)
        ctx.reviews["anti_slop"] = anti_slop.__dict__
        ctx.reviews["repetition"] = repetition.__dict__
        ctx.touch("anti_slop_review")
        return ctx
