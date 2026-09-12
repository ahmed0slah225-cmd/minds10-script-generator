"""
engines/review/engine.py
===========================
مرحلتا مراجعة منفصلتان عن الكتابة (القسم 43): anti_slop_review و
repetition_review. كلاهما "يكتشف ولا يكتب" — النتيجة تُسجَّل في
ctx.review_notes، والتطبيق الفعلي للإصلاحات يحصل لاحقًا في
engines/editor/engine.py (final_edit) فقط للإصلاحات "الصالحة"
(القسم 43: المراجع → القضايا → الأولوية → الإصلاحات المقترحة → محرر
→ تطبيق الإصلاحات الصالحة فقط).
"""

from __future__ import annotations

from core.context import PipelineContext
from core.registry import skill_registry
from skills.anti_slop_ar_eg.skill import find_repetition_issues


def run_anti_slop(ctx: PipelineContext, *, model_id: str) -> None:
    skill = skill_registry.get("anti_slop_ar_eg")
    skill.validate_input(ctx)
    result = skill.run(ctx)
    skill.validate_output(ctx, result)

    report = result.output["anti_slop_report"]
    ctx.review_notes.append({"type": "anti_slop_report", "detail": report})
    ctx.log_run(engine="anti_slop_review", skill="anti_slop_ar_eg", model_id=None, status="passed")


def run_repetition(ctx: PipelineContext, *, model_id: str) -> None:
    """مرحلة منفصلة عن anti_slop_review عمدًا (القسم 5: ممنوع تشغيل
    Reviewer كأنه شيء آخر) — تركز فقط على التكرار عبر كامل السكريبت،
    وليس كل أنواع الـSlop."""
    text = ctx.humanized_script or ctx.draft_script or ""
    issues = find_repetition_issues(text)
    ctx.review_notes.append({"type": "repetition_report", "detail": issues})
    ctx.log_run(engine="repetition_review", skill=None, model_id=None, status="passed")
