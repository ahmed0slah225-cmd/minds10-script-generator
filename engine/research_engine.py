"""
engine/research_engine.py
============================
مرحلة "Research". بيستخدم skills.DeepResearchSkill لتنظيم المعرفة من
مصادر المستخدم + (اختياريًا) بحث خارجي، لكن استدعاء أي API بحث فعلي
مسؤولية دالة web_search_fn اللي بتتمرر من برّه (Dependency Injection)
عشان الـEngine ما يبقاش مربوط بمزوّد بحث معيّن.
"""

from __future__ import annotations

from typing import Callable, Optional

from config import WEB_RESEARCH_ENABLED_DEFAULT, MAX_WEB_SOURCES_PER_RESEARCH_RUN
from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills import DeepResearchSkill


class ResearchEngine:
    def __init__(
        self,
        llm: Optional[GeminiClient] = None,
        web_search_fn: Optional[Callable[[str], list[dict]]] = None,
    ):
        self.skill = DeepResearchSkill(llm)
        self.web_search_fn = web_search_fn  # None = البحث الخارجي متعطل

    def run(self, ctx: ProjectContext, web_research_enabled: bool = WEB_RESEARCH_ENABLED_DEFAULT) -> ProjectContext:
        user_excerpts = [
            s.raw_text for s in ctx.sources if s.raw_text
        ]

        web_snippets: list[dict] = []
        if web_research_enabled and self.web_search_fn:
            query = ctx.topic_understanding.get("surface_topic", ctx.title)
            web_snippets = self.web_search_fn(query)[:MAX_WEB_SOURCES_PER_RESEARCH_RUN]

        result = self.skill.synthesize(
            topic_understanding=ctx.topic_understanding,
            user_source_excerpts=user_excerpts,
            web_snippets=web_snippets or None,
        )
        if result.ok:
            ctx.research_notes.append({
                "findings": result.data.get("findings", []),
                "gaps": result.data.get("gaps", []),
            })
        ctx.touch("research")
        return ctx
