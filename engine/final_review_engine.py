"""
engine/final_review_engine.py
================================
مرحلة "Final Human Review" — آخر مرحلة قبل اعتماد السكريبت. مش تدقيق
لغوي، ومش مراجعة تقنية؛ القارئ هنا "مشاهد"، مش كاتب ولا باحث ولا AI.

Review-only. لو فيه مشاكل، بترجع في التقرير للمستخدم يقرر بنفسه —
مفيش نداء Rewrite تلقائي هنا عشان نمنع تمريرة كتابة رابعة من غير داعي.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills.base import SkillResult

_SYSTEM_PROMPT = """أنت مشاهد عادي بيسمع سكريبت فيديو يوتيوب مصري، مش
كاتب ومش باحث ومش AI. اقرأ السكريبت وجاوب بصدق:

- هل أنا فاهم من البداية؟
- هل أنا مهتم فعلًا، ولا حاسس إني بضيع وقتي؟
- هل حسيت إن الكلام عني أنا؟
- هل في جزء كنت هقفل الفيديو عنده؟
- هل النهاية تستحق اللي قعدته بتسمع؟
- هل الوعد اللي الفيديو بدأ بيه (الهوك) اتحقق فعلًا؟

أعد ردك بصيغة JSON فقط:
{
  "would_keep_watching": true,
  "understood_from_start": true,
  "felt_personal": true,
  "drop_off_point": "اقتباس أقل من 15 كلمة أو فارغ لو مفيش",
  "promise_fulfilled": true,
  "overall_verdict": "جملة أو اتنين تلخّص انطباعك كمشاهد"
}"""


class FinalReviewEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.llm = llm or GeminiClient()

    def run(self, ctx: ProjectContext) -> ProjectContext:
        raw = self.llm.generate(
            _SYSTEM_PROMPT, f"السكريبت:\n\n{ctx.egyptian_final_script}", temperature=0.4
        )
        result = SkillResult.parse_json("final_review_engine", "review", raw)
        ctx.reviews["final_human"] = result.data if result.ok else {"error": result.error}
        ctx.final_script = ctx.egyptian_final_script
        ctx.touch("final_script")
        return ctx
