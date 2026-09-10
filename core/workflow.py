"""
core/workflow.py
==================
هنا بيتجمع كل حاجة: الـ Engines (تنتج محتوى) والـ Skills (تراجع/تحسّن)،
بالترتيب المتفق عليه:

INPUT
 → Input Intelligence          [Engine]
 → Topic Understanding         [Engine]
 → Research                    [Engine]
 → Knowledge                   [Engine]
 → Audience / Why People Care  [Engine]
 → Strategy                    [Engine]  (يستدعي Retention.plan أثناء التخطيط)
 → Story Architecture          [Engine]  (يستدعي Retention.plan مرة أخرى بعد الهيكل)
 → Hook                        [Engine]  (يستخدم Voice DNA + Retention)
 → Script Writing              [Engine]  (يستخدم Voice DNA)
 → Humanization                [Skill]   (بعد وجود مسودة فقط)
 → Anti-Slop Review            [Skill]   (تحليل وتقييم فقط)
 → Retention Review            [Skill]
 → Repetition Review           [Skill]   (نفس محرك Anti-Slop بزاوية التكرار)
 → Egyptian Arabic Editing     [Engine]  (يطبّق كل ملاحظات المراجعات دفعة واحدة)
 → Voice DNA Consistency Check [Skill]
 → Final Human Review          [Engine]
 → Editor                      [Engine]  → FINAL SCRIPT

ملحوظة عن الكفاءة: كل مراجعة بتتنفذ مرة واحدة فقط، وتعديلات المراجعات
الثلاث (Anti-Slop, Retention, Repetition) بتتجمع وتتطبق دفعة واحدة في
Egyptian Arabic Editing بدل ما نعيد كتابة السكريبت 3 مرات منفصلة - وده
يقلل عدد استدعاءات Gemini وتضارب التعليمات بين المراجعات.
"""

from __future__ import annotations

from typing import Callable, Iterator

from core.context import ProjectContext
from db.project_store import save_project

from engines.input_intelligence import InputIntelligenceEngine
from engines.topic_understanding import TopicUnderstandingEngine
from engines.research import ResearchEngine
from engines.knowledge import KnowledgeEngine
from engines.audience import AudienceEngine
from engines.strategy import StrategyEngine
from engines.story import StoryEngine
from engines.hook import HookEngine
from engines.script_writing import ScriptWritingEngine
from engines.egyptian_arabic_editing import EgyptianArabicEditingEngine
from engines.final_review import FinalHumanReviewEngine
from engines.editor import EditorEngine

from skills.humanization import HumanizationSkill
from skills.anti_slop import AntiSlopSkill
from skills.retention import RetentionSkill
from skills.voice_dna import VoiceDnaSkill


# ---------------- Skill-backed stage wrappers ----------------
# دي مش Engines - هي استدعاءات مباشرة للـ Skills، لكن بنحطها في شكل موحّد
# (stage_name, function) عشان تتعامل بنفس منطق الـ Engines جوه run_workflow.

def _stage_humanization(ctx: ProjectContext) -> ProjectContext:
    skill = HumanizationSkill()
    ctx.humanized_script = skill.humanize(
        ctx.script_draft, ctx.voice_dna_profile.as_prompt_guidance()
    )
    return ctx


def _stage_anti_slop_review(ctx: ProjectContext) -> ProjectContext:
    skill = AntiSlopSkill()
    report = skill.review(ctx.humanized_script)
    ctx.anti_slop_report = {
        "scores": report.scores, "issues": report.issues, "summary": report.overall_summary,
    }
    return ctx


def _stage_retention_review(ctx: ProjectContext) -> ProjectContext:
    skill = RetentionSkill()
    result = skill.review(ctx.humanized_script)
    ctx.retention_review = {
        "passed": result.passed, "scores": result.scores,
        "issues": result.issues, "summary": result.summary,
    }
    return ctx


def _stage_repetition_review(ctx: ProjectContext) -> ProjectContext:
    skill = AntiSlopSkill()
    result = skill.repetition_check(ctx.humanized_script)
    ctx.repetition_review = {
        "passed": result.passed, "scores": result.scores,
        "issues": result.issues, "summary": result.summary,
    }
    return ctx


def _stage_voice_dna_consistency_check(ctx: ProjectContext) -> ProjectContext:
    skill = VoiceDnaSkill()
    result = skill.consistency_check(ctx.egyptian_edited_script, ctx.voice_dna_profile)
    ctx.voice_dna_consistency_report = {
        "passed": result.passed, "scores": result.scores,
        "issues": result.issues, "summary": result.summary,
    }
    return ctx


# ---------------- Stage registry (order matters) ----------------

def _engine_stage(engine_cls) -> Callable[[ProjectContext], ProjectContext]:
    def runner(ctx: ProjectContext) -> ProjectContext:
        return engine_cls().run_and_mark(ctx)
    return runner


STAGES: list[tuple[str, Callable[[ProjectContext], ProjectContext]]] = [
    ("input_intelligence", _engine_stage(InputIntelligenceEngine)),
    ("topic_understanding", _engine_stage(TopicUnderstandingEngine)),
    ("research", _engine_stage(ResearchEngine)),
    ("knowledge", _engine_stage(KnowledgeEngine)),
    ("audience", _engine_stage(AudienceEngine)),
    ("strategy", _engine_stage(StrategyEngine)),
    ("story", _engine_stage(StoryEngine)),
    ("hook", _engine_stage(HookEngine)),
    ("script_writing", _engine_stage(ScriptWritingEngine)),
    ("humanization", _stage_humanization),
    ("anti_slop_review", _stage_anti_slop_review),
    ("retention_review", _stage_retention_review),
    ("repetition_review", _stage_repetition_review),
    ("egyptian_arabic_editing", _engine_stage(EgyptianArabicEditingEngine)),
    ("voice_dna_consistency_check", _stage_voice_dna_consistency_check),
    ("final_human_review", _engine_stage(FinalHumanReviewEngine)),
    ("editor", _engine_stage(EditorEngine)),
]

STAGE_LABELS_AR = {
    "input_intelligence": "فهم المدخلات",
    "topic_understanding": "فهم الموضوع",
    "research": "البحث",
    "knowledge": "بناء المعرفة",
    "audience": "فهم الجمهور",
    "strategy": "الاستراتيجية",
    "story": "بناء الحكاية",
    "hook": "صناعة الهوك",
    "script_writing": "كتابة السكريبت",
    "humanization": "الإنسنة",
    "anti_slop_review": "مراجعة الكتابة الرديئة",
    "retention_review": "مراجعة الاحتفاظ بالمشاهد",
    "repetition_review": "مراجعة التكرار",
    "egyptian_arabic_editing": "تحرير اللهجة المصرية",
    "voice_dna_consistency_check": "فحص اتساق البصمة الصوتية",
    "final_human_review": "المراجعة النهائية كمشاهد",
    "editor": "التحرير النهائي",
}


def run_workflow(ctx: ProjectContext, resume: bool = True) -> Iterator[tuple[str, ProjectContext]]:
    """
    يشغّل كل المراحل بالترتيب، ويحفظ المشروع في قاعدة البيانات بعد كل مرحلة.
    لو resume=True وكانت المرحلة موجودة بالفعل في ctx.completed_stages، يتم تخطيها -
    وده اللي بيخلي المشروع "قابل للاستكمال" بدل ما يبدأ من الصفر كل مرة.

    الدالة generator: بترجع (stage_name, ctx) بعد كل مرحلة عشان واجهة
    Streamlit تقدر تعرض تقدم مباشر (Progress).
    """
    ctx.status = "in_progress"
    for stage_name, runner in STAGES:
        if resume and stage_name in ctx.completed_stages:
            yield stage_name, ctx
            continue
        try:
            ctx = runner(ctx)
            save_project(ctx)
            yield stage_name, ctx
        except Exception as e:
            ctx.status = "failed"
            ctx.current_stage = stage_name
            save_project(ctx)
            raise RuntimeError(f"فشلت مرحلة '{STAGE_LABELS_AR.get(stage_name, stage_name)}': {e}") from e

    ctx.status = "done"
    save_project(ctx)
    yield "done", ctx
