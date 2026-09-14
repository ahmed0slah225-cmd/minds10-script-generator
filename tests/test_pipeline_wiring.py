"""
اختبار تكامل شامل: كل مرحلة في DEFAULT_STAGE_ORDER لازم يكون ليها Engine
مسجَّل فعليًا — القسم 82/85 (المهمة مش مكتملة لو Engine ناقص لمرحلة).
"""
from core.bootstrap import bootstrap, configure_provider
from core.orchestrator import DEFAULT_STAGE_ORDER
from core.registry import engine_registry, skill_registry


def test_every_default_stage_has_a_registered_engine():
    bootstrap()
    configure_provider(api_key=None)
    missing = [s for s in DEFAULT_STAGE_ORDER if s not in engine_registry.names()]
    assert missing == [], f"مراحل بدون Engine: {missing}"


def test_all_manifested_skills_are_registered():
    bootstrap()
    expected = {
        "anti_slop_ar_eg", "voice_dna_ar_eg", "humanize_ar_eg",
        "storytelling_ar_eg", "viral_hooks_ar_eg", "retention_ar_eg", "dumpify_ar_eg",
    }
    registered = {m.name for m in skill_registry.all_manifests()}
    assert expected.issubset(registered)


def test_pipeline_fails_clearly_at_first_llm_stage_without_api_key():
    """بدون مفتاح API، أول مرحلة تحتاج LLM فعليًا (topic_understanding)
    لازم تفشل برسالة واضحة، مش أي مرحلة تانية بعدها بمسافة تربك المستخدم."""
    from core.context import PipelineContext, ResearchConfig
    from core.orchestrator import Orchestrator

    bootstrap()
    configure_provider(api_key=None)

    ctx = PipelineContext(
        project_id="p1", project_name="test",
        raw_input="فكرة تجريبية",
        research=ResearchConfig(enabled=False),
    )
    results = Orchestrator().run(ctx)

    failed = [r for r in results if r.status.value == "failed"]
    assert len(failed) == 1
    assert failed[0].stage_name == "topic_understanding"
    assert "GEMINI_API_KEY" in failed[0].detail
