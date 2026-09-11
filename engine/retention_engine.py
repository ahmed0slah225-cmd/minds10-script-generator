"""
engine/retention_engine.py
=============================
بيغطي مرحلتين مختلفتين في الـWorkflow باستخدام نفس الـSkill
(AddictiveWritingSkill)، بس بدالتين مختلفتين تمامًا:

- "Retention Planning" (قبل الكتابة): plan()
- "Retention Review" (بعد Humanization): review() — تحليل فقط، لا تكتب.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from engine.strategy_engine import StrategyEngine
from skills import AddictiveWritingSkill


class RetentionEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.skill = AddictiveWritingSkill(llm)

    def plan(self, ctx: ProjectContext) -> ProjectContext:
        result = self.skill.plan(
            strategy_summary=StrategyEngine.summary_text(ctx),
            outline=ctx.outline,
        )
        if result.ok:
            ctx.retention_plan = result.data
        ctx.touch("retention_planning")
        return ctx

    def review(self, ctx: ProjectContext, script_text: str) -> dict:
        """
        Review-only — بترجع dict بس، ومتلمسش ctx.humanized_script.
        الـEditor Engine هو اللي بيقرر إزاي يطبّق النتيجة دي.
        """
        result = self.skill.review(script_text, retention_plan=ctx.retention_plan)
        return result.data if result.ok else {"retention_score": None, "error": result.error}
