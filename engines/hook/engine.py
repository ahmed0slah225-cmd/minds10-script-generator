"""engines/hook/engine.py — غلاف رقيق فوق مهارة viral_hooks_ar_eg."""

from __future__ import annotations

from core.context import PipelineContext
from core.registry import skill_registry


def run(ctx: PipelineContext, *, model_id: str) -> None:
    skill = skill_registry.get("viral_hooks_ar_eg")
    skill.validate_input(ctx)
    result = skill.run(ctx)
    skill.validate_output(ctx, result)

    if not result.success:
        raise RuntimeError(f"viral_hooks_ar_eg فشلت: {result.error}")

    ctx.hooks = result.output["hooks"]
    ctx.log_run(engine="hook", skill="viral_hooks_ar_eg", model_id=result.model_used,
                status="passed", tokens_in=result.tokens_in, tokens_out=result.tokens_out)
