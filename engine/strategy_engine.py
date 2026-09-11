"""
engine/strategy_engine.py
============================
مرحلة "Strategy". تحديد الزاوية والسؤال المركزي والوعد للمشاهد، بناءً
على فهم الموضوع + ألم المشاهد + المعرفة الموثقة فقط (مفيش اختراع).
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills import DeepThinkingSkill


class StrategyEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.skill = DeepThinkingSkill(llm)

    def run(self, ctx: ProjectContext) -> ProjectContext:
        result = self.skill.find_angle(
            topic_understanding=ctx.topic_understanding,
            audience_pain_point=ctx.audience_pain_point,
            known_facts=ctx.confirmed_facts(),
        )
        if result.ok:
            ctx.strategy = result.data
        ctx.touch("strategy")
        return ctx

    @staticmethod
    def summary_text(ctx: ProjectContext) -> str:
        """نص مختصر لاستخدامه كمدخل في Skills تانية (Retention, Story)."""
        s = ctx.strategy
        return (
            f"الزاوية: {s.get('angle', '')}\n"
            f"السؤال المركزي: {s.get('central_question', '')}\n"
            f"الوعد للمشاهد: {s.get('promise_to_viewer', '')}"
        )
