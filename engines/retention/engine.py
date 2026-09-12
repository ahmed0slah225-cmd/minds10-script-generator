"""
engines/retention/engine.py
==============================
غلاف رقيق فوق مهارة retention_ar_eg — مرحلتان منفصلتان (تخطيط ثم مراجعة)
لكن نفس المهارة، بنفس منطق فصل "الفهم" عن "المراجعة" في باقي المشروع.
"""

from __future__ import annotations

from core.context import PipelineContext
from core.registry import skill_registry


def run_planning(ctx: PipelineContext, *, model_id: str) -> None:
    skill = skill_registry.get("retention_ar_eg")
    skill.validate_input(ctx)
    result = skill.plan(ctx)
    skill.validate_output(ctx, result)

    if not result.success:
        raise RuntimeError(f"retention_ar_eg (plan) فشلت: {result.error}")

    ctx.outline = result.output["outline"]
    ctx.log_run(engine="retention_planning", skill="retention_ar_eg", model_id=result.model_used,
                status="passed", tokens_in=result.tokens_in, tokens_out=result.tokens_out)


def run_review(ctx: PipelineContext, *, model_id: str) -> None:
    skill = skill_registry.get("retention_ar_eg")
    result = skill.review(ctx)
    skill.validate_output(ctx, result)

    ctx.review_notes.extend(result.output.get("review_notes", []))
    high_priority = [n for n in result.output.get("review_notes", []) if n.get("priority") == "high"]

    ctx.log_run(engine="retention_review", skill="retention_ar_eg", model_id=None, status="passed")

    if high_priority:
        # لا نكسر الـPipeline، لكن نسجّل تحذيرًا واضحًا يظهر للمستخدم لاحقًا
        ctx.run_log[-1]["error"] = f"{len(high_priority)} مشكلة احتفاظ عالية الأولوية تحتاج مراجعة يدوية."
