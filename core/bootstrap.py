"""
core/bootstrap.py
==================
نقطة تجميع واحدة لكل الموفرين (Providers) والمحركات (Engines) والمهارات
(Skills). مقسّمة لدالتين مقصودًا:

- bootstrap(): تسجّل الـEngines والـSkills — مرة واحدة فقط طول عمر العملية،
  لأنها لا تعتمد على أي إعداد متغيّر من المستخدم.
- configure_provider(api_key): تُستدعى في *كل* مرة يتغيّر فيها مفتاح الـAPI
  (مثلاً المستخدم يكتبه في حقل بالواجهة) — لذلك ما تنضمّش بحارس واحد مرة
  زي bootstrap(). القاعدة 33 و72: المفتاح ييجي من المستخدم عبر الواجهة،
  مش env var إجباري، وأي فشل في المفتاح لازم يبان بوضوح مش يكسر التطبيق كله.
"""

from __future__ import annotations

from core.registry import engine_registry, skill_registry
from providers.base import register_provider
from providers.gemini import GeminiProvider

_engines_and_skills_bootstrapped = False


def configure_provider(api_key: str | None) -> None:
    """يُسجَّل/يُحدَّث موفر Gemini بالمفتاح الحالي من الواجهة. آمن الاستدعاء
    المتكرر — يستبدل التسجيل السابق بدل تجاهل التحديث."""
    register_provider("google", GeminiProvider(api_key=api_key))


def bootstrap() -> None:
    global _engines_and_skills_bootstrapped
    if _engines_and_skills_bootstrapped:
        return

    # --- المحركات (Engines) — كل واحد مُسجَّل باسم مرحلته في core/orchestrator.py ---
    from engines.understanding.engine import run_input_understanding, run_topic_understanding
    engine_registry.register("input_understanding", run_input_understanding)
    engine_registry.register("topic_understanding", run_topic_understanding)

    from engines.source_analysis.engine import run as source_analysis_run
    engine_registry.register("source_analysis", source_analysis_run)

    from engines.research.engine import run as research_run
    engine_registry.register("research", research_run)

    from engines.knowledge.engine import run as knowledge_run
    engine_registry.register("knowledge", knowledge_run)

    from engines.audience.engine import run as audience_run
    engine_registry.register("audience", audience_run)

    from engines.strategy.engine import run as strategy_run
    engine_registry.register("strategy", strategy_run)

    from engines.story.engine import run as story_run
    engine_registry.register("story", story_run)

    from engines.retention.engine import run_planning as retention_planning_run
    from engines.retention.engine import run_review as retention_review_run
    engine_registry.register("retention_planning", retention_planning_run)
    engine_registry.register("retention_review", retention_review_run)

    from engines.hook.engine import run as hook_run
    engine_registry.register("hook", hook_run)

    from engines.script.engine import run as script_run
    engine_registry.register("script", script_run)

    from engines.humanize.engine import run as humanize_run
    engine_registry.register("humanize", humanize_run)

    from engines.review.engine import run_anti_slop, run_repetition
    engine_registry.register("anti_slop_review", run_anti_slop)
    engine_registry.register("repetition_review", run_repetition)

    from engines.editor.engine import run_egyptian_arabic_edit, run_fact_check, run_final_edit
    engine_registry.register("egyptian_arabic_edit", run_egyptian_arabic_edit)
    engine_registry.register("fact_check", run_fact_check)
    engine_registry.register("final_edit", run_final_edit)

    from engines.voice.engine import run as voice_dna_check_run
    engine_registry.register("voice_dna_check", voice_dna_check_run)

    # --- المهارات (Skills) ---
    from skills.anti_slop_ar_eg.skill import AntiSlopSkill
    skill_registry.register(AntiSlopSkill(), enabled=True)

    from skills.voice_dna_ar_eg.skill import VoiceDNASkill
    skill_registry.register(VoiceDNASkill(), enabled=True)

    from skills.humanize_ar_eg.skill import HumanizeSkill
    skill_registry.register(HumanizeSkill(), enabled=True)

    from skills.storytelling_ar_eg.skill import StorytellingSkill
    skill_registry.register(StorytellingSkill(), enabled=True)

    from skills.viral_hooks_ar_eg.skill import ViralHooksSkill
    skill_registry.register(ViralHooksSkill(), enabled=True)

    from skills.retention_ar_eg.skill import RetentionSkill
    skill_registry.register(RetentionSkill(), enabled=True)

    from skills.dumpify_ar_eg.skill import DumpifySkill
    skill_registry.register(DumpifySkill(), enabled=True)

    _engines_and_skills_bootstrapped = True
