"""اختبارات البحث المباشر عبر DuckDuckGo."""

from unittest.mock import patch

from core.context import PipelineContext, ResearchConfig
from engines.research.engine import run as research_run


def _make_ctx() -> PipelineContext:
    return PipelineContext(
        project_id="p1",
        project_name="test",
        research=ResearchConfig(enabled=True),
    )


def test_research_uses_duckduckgo_without_llm_provider():
    ctx = _make_ctx()
    ctx.topic_understanding = {"knowledge_gaps": ["إحصائية حديثة عن X"]}

    fake_results = [
        {
            "title": "مصدر تجريبي",
            "href": "https://example.com",
            "body": "معلومة تجريبية",
        }
    ]

    with patch("engines.research.engine._search_duckduckgo", return_value=fake_results) as search:
        research_run(ctx, model_id="gemini-3.6-flash")
        search.assert_called_once_with("إحصائية حديثة عن X", 8)

    assert len(ctx.sources) == 1
    assert ctx.sources[0].origin == "web_research"
    assert ctx.research.sources[0]["engine"] == "duckduckgo"


def test_research_skips_when_no_knowledge_gaps():
    ctx = _make_ctx()
    ctx.topic_understanding = {"knowledge_gaps": []}

    with patch("engines.research.engine._search_duckduckgo") as search:
        research_run(ctx, model_id="gemini-3.6-flash")
        search.assert_not_called()

    assert ctx.sources == []
