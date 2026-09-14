"""
engines/story/engine.py
==========================
محرك القصة — غلاف رقيق فوق مهارة storytelling_ar_eg، يستدعيها عبر
core.registry.skill_registry بدل استيرادها مباشرة (فصل Engine عن تفاصيل
تنفيذ الـSkill الداخلية — القسم 4).
"""

from __future__ import annotations

from core.context import PipelineContext
from core.registry import skill_registry


def run(ctx: PipelineContext, *, model_id: str) -> None:
    skill = skill_registry.get("storytelling_ar_eg")
    skill.validate_input(ctx)
    result = skill.run(ctx)
    skill.validate_output(ctx, result)

    if not result.success:
        raise RuntimeError(f"storytelling_ar_eg فشلت: {result.error}")

    ctx.story = result.output["story"]
    ctx.log_run(engine="story", skill="storytelling_ar_eg", model_id=result.model_used,
                status="passed", tokens_in=result.tokens_in, tokens_out=result.tokens_out)
