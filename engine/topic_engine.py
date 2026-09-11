"""
engine/topic_engine.py
=========================
مرحلة "Topic Understanding". أول مرحلة تفكير حقيقية بعد استقبال المدخل:
تفكيك الموضوع الظاهري لإيجاد المشكلة الإنسانية تحته.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills import DeepThinkingSkill


class TopicEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.skill = DeepThinkingSkill(llm)

    def run(self, ctx: ProjectContext) -> ProjectContext:
        raw_input = "\n".join(s.raw_text for s in ctx.sources if s.raw_text) or ctx.title
        result = self.skill.analyze_topic(raw_input)
        if result.ok:
            ctx.topic_understanding = {
                "surface_topic": result.data.get("surface_topic", ""),
                "possible_underlying_problems": result.data.get("possible_underlying_problems", []),
            }
            ctx.core_ideas = result.data.get("core_ideas", [])
        ctx.touch("topic_understanding")
        return ctx
