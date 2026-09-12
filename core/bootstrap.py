"""
core/bootstrap.py
==================
نقطة تجميع واحدة: تسجّل كل الموفرين (Providers) والمحركات (Engines)
والمهارات (Skills) الحالية في السجلات المركزية عند إقلاع التطبيق.

app.py (أو أي نقطة دخول أخرى مستقبلاً — CLI, API, ...) يستدعي
`bootstrap()` مرة واحدة قبل استخدام أي Orchestrator.

هذا هو الموضع الوحيد الذي "يعرف" كل مكونات المشروع مجتمعة — بقية
الكود (core/orchestrator.py مثلاً) لا يستورد أي Engine/Skill مباشرة.
"""

from __future__ import annotations

from core.registry import engine_registry, skill_registry
from providers.base import register_provider
from providers.gemini import GeminiProvider

_bootstrapped = False


def bootstrap(*, gemini_api_key: str | None = None) -> None:
    global _bootstrapped
    if _bootstrapped:
        return

    # --- الموفرون (Providers) ---
    register_provider("google", GeminiProvider(api_key=gemini_api_key))

    # --- المحركات (Engines) — كل واحد يُسجَّل باسم المرحلة التي ينتمي لها ---
    from engines.research.engine import run as research_run
    engine_registry.register("research", research_run)

    from engines.script.engine import run as script_run
    engine_registry.register("script", script_run)

    # ملاحظة: بقية المحركات (understanding, knowledge, strategy, story,
    # hook, humanize, review, editor...) لم تُبنَ بعد بنفس التفصيل — يُضاف
    # كل واحد هنا بنفس الطريقة عند تنفيذه، دون تعديل core/orchestrator.py.

    # --- المهارات (Skills) ---
    from skills.anti_slop_ar_eg.skill import AntiSlopSkill
    skill_registry.register(AntiSlopSkill(), enabled=True)

    from skills.voice_dna_ar_eg.skill import VoiceDNASkill
    skill_registry.register(VoiceDNASkill(), enabled=True)

    from skills.humanize_ar_eg.skill import HumanizeSkill
    skill_registry.register(HumanizeSkill(), enabled=True)

    _bootstrapped = True
