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


def test_run_node_resolves_only_missing_dependencies():
    from core.context import PipelineContext
    from core.orchestrator import Orchestrator
    from core.registry import engine_registry

    executed = []
    original = engine_registry._engines.copy()
    try:
        required = {
            name: (lambda ctx, model_id, _name=name: executed.append(_name))
            for name in Orchestrator()._stage_order
        }
        engine_registry._engines = required

        ctx = PipelineContext(project_id="p2", project_name="test")
        results = Orchestrator().run_node(ctx, "script")

        assert results[-1].stage_name == "script"
        assert results[-1].status.value == "passed"
        assert executed == [
            "input_understanding",
            "topic_understanding",
            "research",
            "knowledge",
            "audience",
            "strategy",
            "story",
            "retention_planning",
            "hook",
            "script",
        ]
    finally:
        engine_registry._engines = original


def test_run_node_does_not_rerun_completed_dependencies():
    from core.context import PipelineContext
    from core.orchestrator import Orchestrator
    from core.registry import engine_registry

    executed = []
    original = engine_registry._engines.copy()
    try:
        engine_registry._engines = {
            name: (lambda ctx, model_id, _name=name: executed.append(_name))
            for name in Orchestrator()._stage_order
        }
        ctx = PipelineContext(project_id="p3", project_name="test")
        for stage in [
            "input_understanding", "topic_understanding", "research", "knowledge",
            "audience", "strategy", "story", "retention_planning", "hook"
        ]:
            ctx.completed_stages[stage] = True

        results = Orchestrator().run_node(ctx, "script")
        assert [r.stage_name for r in results] == ["script"]
        assert executed == ["script"]
    finally:
        engine_registry._engines = original
