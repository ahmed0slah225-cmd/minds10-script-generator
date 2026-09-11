"""
engine/hook_engine.py
========================
مرحلة "Hook". بيستخدم ViralHooksSkill + بصمة الكاتب الصوتية (لو موجودة)
لبناء اقتراحات هوك، ويختار الأنسب تلقائيًا (المستخدم يقدر يغيّر اختياره
من الواجهة لاحقًا).
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills import ViralHooksSkill


class HookEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.skill = ViralHooksSkill(llm)

    def run(self, ctx: ProjectContext) -> ProjectContext:
        result = self.skill.build_hooks(
            opening_situation=ctx.strategy.get("opening_situation", ""),
            promise=ctx.strategy.get("promise_to_viewer", ""),
            audience_pain_point=ctx.audience_pain_point,
            voice_dna_fragment=ctx.voice_dna.to_prompt_fragment(),
        )
        if result.ok:
            hooks = result.data.get("hooks", [])
            idx = result.data.get("recommended_index", 0)
            if hooks:
                ctx.strategy["hook_options"] = hooks
                ctx.hook_text = hooks[min(idx, len(hooks) - 1)].get("text", "")
        ctx.touch("hook")
        return ctx
