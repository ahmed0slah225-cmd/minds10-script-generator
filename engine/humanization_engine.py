"""
engine/humanization_engine.py
================================
مرحلة "Humanization". النداء الأول من نداءين الـRewrite المسموحين في
الـpipeline كله (التاني هو Final Editor). بيستخدم HumanizeSkill مرة
واحدة فقط لكل سكريبت.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills import HumanizeSkill


class HumanizationEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.skill = HumanizeSkill(llm)

    def run(self, ctx: ProjectContext) -> ProjectContext:
        result = self.skill.run(
            script_text=ctx.draft_script,
            voice_dna_fragment=ctx.voice_dna.to_prompt_fragment(),
            known_facts=ctx.confirmed_facts(),
        )
        if result.ok:
            ctx.humanized_script = result.data.get("humanized_text", ctx.draft_script)
        else:
            ctx.humanized_script = ctx.draft_script  # لو فشل الـParsing، منكملش بنص فاضي
        ctx.touch("humanization")
        return ctx
