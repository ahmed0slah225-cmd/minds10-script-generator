"""اختبارات مرحلة تنظيم المصادر اليدوية."""

from core.context import PipelineContext, ResearchConfig
from engines.research.engine import run as research_run


def _make_ctx() -> PipelineContext:
    ctx = PipelineContext(
        project_id="p1",
        project_name="test",
        research=ResearchConfig(enabled=False),
    )
    ctx.research.sources = [
        {
            "origin": "user_provided",
            "title": "مصدر تجريبي",
            "url": "https://example.com",
            "notes": "معلومة تجريبية",
        }
    ]
    return ctx


def test_research_uses_user_selected_sources_without_llm():
    ctx = _make_ctx()
    research_run(ctx, model_id="gemini-3.6-flash")

    assert len(ctx.sources) == 1
    assert ctx.sources[0].origin == "user_provided_link"
    assert "مصدر تجريبي" in ctx.sources[0].content
    assert ctx.run_log[-1]["provider"] == "user_selected_sources"


def test_research_allows_empty_manual_sources():
    ctx = PipelineContext(
        project_id="p1",
        project_name="test",
        research=ResearchConfig(enabled=False),
    )
    research_run(ctx, model_id="gemini-3.6-flash")
    assert ctx.sources == []
