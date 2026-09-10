"""
engines/final_review.py
=========================
يقرأ السكريبت كأنه مشاهد فعليًا - مش كاتب ولا باحث ولا AI. يسأل: هل أنا
فاهم؟ هل أنا مهتم؟ هل حسيت إن الكلام عني؟ هل النهاية تستحق الفيديو؟
هل الوعد اللي بدأ بيه الفيديو (من Strategy Engine) اتحقق فعلاً؟
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class FinalHumanReviewEngine(BaseEngine):
    name = "final_human_review"
    persona = (
        "أنت مشاهد عادي بتسمع سكريبت فيديو يوتيوب لأول مرة - لست كاتبًا ولا "
        "باحثًا ولا ذكاءً اصطناعيًا. قيّم تجربتك الصادقة فقط: هل أنت مهتم؟ "
        "هل هناك جزء كنت ستخرج عنده؟ هل تحقق الوعد الذي بدأ به الفيديو؟"
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        prompt = f"""
الوعد الذي بدأ به الفيديو: {ctx.strategy.get("promise_to_viewer")}

السكريبت:
{ctx.egyptian_edited_script}

المطلوب JSON:
{{
  "would_keep_watching": true أو false,
  "drop_off_risk_points": ["أماكن محتمل يخرج المشاهد عندها ولماذا"],
  "promise_fulfilled": true أو false,
  "ending_satisfaction": "رأي صادق مختصر في النهاية",
  "overall_feeling": "وصف تجربة المشاهدة بجملتين كحد أقصى"
}}
"""
        result = self.call(prompt, json_mode=True, temperature=0.5)
        ctx.final_human_review = result
        return ctx
