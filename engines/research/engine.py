"""
engines/research/engine.py
===========================
محرك البحث المباشر — يستخدم DuckDuckGo عبر مكتبة DDGS، بدون Gemini Search
وبدون API key للبحث نفسه.

السلوك:
    - البحث يعمل تلقائيًا عند تشغيل مرحلة research؛ لا يوجد checkbox أو إذن.
    - الاستعلامات تُبنى من knowledge_gaps المكتشفة في topic_understanding.
    - Gemini لا يُستدعى للبحث؛ مفتاح Gemini يُستخدم فقط في مراحل الـLLM الأخرى.
    - نتائج DuckDuckGo تدخل كـ web_research sources، ثم تمر إلى knowledge engine.
"""

from __future__ import annotations

from core.context import PipelineContext, SourceRef


def _max_results_for_depth(depth: str) -> int:
    return {
        "basic": 5,
        "standard": 8,
        "deep": 12,
    }.get(depth, 8)


def _search_duckduckgo(query: str, max_results: int) -> list[dict]:
    """بحث مباشر من DuckDuckGo عبر DDGS."""
    try:
        from ddgs import DDGS
    except ImportError as exc:
        raise RuntimeError(
            "مكتبة ddgs غير مثبتة. أضف ddgs إلى requirements.txt ثم أعد نشر التطبيق."
        ) from exc

    return DDGS(timeout=10).text(
        query,
        region="us-en",
        safesearch="moderate",
        max_results=max_results,
        backend="duckduckgo",
    )


def run(ctx: PipelineContext, *, model_id: str) -> None:
    """مرحلة البحث اليدوي: المستخدم هو من يحدد المصادر، والـPipeline ينظمها فقط."""
    manual_sources = [
        source for source in ctx.research.sources
        if source.get("origin") == "user_provided"
    ]

    ctx.sources = [
        source for source in ctx.sources
        if source.origin != "user_provided_link"
    ]

    for source in manual_sources:
        title = source.get("title", "").strip()
        url = source.get("url", "").strip()
        notes = source.get("notes", "").strip()

        content_parts = [title, notes]
        if url:
            content_parts.append(f"URL: {url}")

        ctx.sources.append(
            SourceRef(
                origin="user_provided_link",
                content="\\n".join(p for p in content_parts if p),
                is_primary=True,
                trust_level="user_selected",
            )
        )

    ctx.run_log.append({
        "engine": "research",
        "status": "passed",
        "provider": "user_selected_sources",
        "sources_count": len(manual_sources),
    })

