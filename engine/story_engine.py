"""
engine/story_engine.py
=========================
مرحلة "Story Architecture". بيستخدم StorytellingSkill لبناء القوس
السردي (موقف → سؤال → حيرة → اكتشاف → تفسير → تعقيد → مفاجأة → فهم جديد)،
وبيبني منه outline مبدئي تستخدمه Retention Planning و Hook.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills import StorytellingSkill


class StoryEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.skill = StorytellingSkill(llm)

    def run(self, ctx: ProjectContext) -> ProjectContext:
        result = self.skill.build_story_beats(
            topic_understanding=ctx.topic_understanding,
            core_ideas=ctx.core_ideas,
            audience_pain_point=ctx.audience_pain_point,
            knowledge_facts=ctx.confirmed_facts(),
        )
        if result.ok:
            ctx.strategy["opening_situation"] = result.data.get("opening_situation", "")
            ctx.strategy["story_beats"] = result.data.get("beats", [])
            ctx.outline = [ctx.strategy["opening_situation"]] + [
                b.get("content", "") for b in result.data.get("beats", [])
            ]
        ctx.touch("story_architecture")
        return ctx
