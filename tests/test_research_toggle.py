"""اختبارات سلوك تفعيل/إيقاف البحث على الويب — القسم 81.

هذا هو الاختبار المباشر لطلب المستخدم: لو مربع البحث مش متفعّل،
محرك البحث ميعملش أي اتصال خارجي إطلاقًا.
"""
from unittest.mock import patch

from core.context import PipelineContext, ResearchConfig
from engines.research.engine import run as research_run


def _make_ctx(research_enabled: bool) -> PipelineContext:
    return PipelineContext(
        project_id="p1",
        project_name="test",
        research=ResearchConfig(enabled=research_enabled),
    )


def test_research_off_never_calls_provider():
    ctx = _make_ctx(research_enabled=False)
    with patch("engines.research.engine.get_provider") as mock_get_provider:
        research_run(ctx, model_id="gemini-3-6-flash")
        mock_get_provider.assert_not_called()

    assert ctx.sources == []
    assert any(log.get("status") == "skipped_by_user_setting" for log in ctx.run_log)


def test_research_on_but_no_knowledge_gaps_still_skips_calls():
    # حتى لو البحث ON، لو مفيش gaps مكتشفة فعلاً، لا داعي للبحث (القاعدة 19)
    ctx = _make_ctx(research_enabled=True)
    ctx.topic_understanding = {"knowledge_gaps": []}
    with patch("engines.research.engine.get_provider") as mock_get_provider:
        research_run(ctx, model_id="gemini-3-6-flash")
        mock_get_provider.assert_not_called()


def test_research_on_with_gaps_calls_provider_with_search_enabled():
    ctx = _make_ctx(research_enabled=True)
    ctx.topic_understanding = {"knowledge_gaps": ["إحصائية حديثة عن X"]}

    with patch("engines.research.engine.get_provider") as mock_get_provider:
        mock_provider = mock_get_provider.return_value
        mock_provider.generate.return_value.text = "نتيجة تجريبية"
        mock_provider.generate.return_value.search_sources = [
            {"url": "https://example.com", "title": "مثال"}
        ]

        research_run(ctx, model_id="gemini-3-6-flash")

        mock_get_provider.assert_called_once()
        called_request = mock_provider.generate.call_args[0][0]
        assert called_request.enable_search is True

    assert len(ctx.sources) == 1
    assert ctx.sources[0].origin == "web_research"
