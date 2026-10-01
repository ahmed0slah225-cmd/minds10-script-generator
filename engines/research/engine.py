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
    # model_id موجود فقط للحفاظ على عقد الـEngine الموحد؛ البحث نفسه مستقل عن Gemini.
    gaps = ctx.topic_understanding.get("knowledge_gaps", [])
    if not gaps:
        ctx.run_log.append({
            "engine": "research",
            "status": "skipped_no_knowledge_gaps",
        })
        return

    max_results = _max_results_for_depth(ctx.research.depth.value)

    # لا نعيد تنفيذ gap اكتمل سابقًا لو المرحلة نفسها توقفت في منتصف البحث.
    completed_gaps = {
        item.get("gap")
        for item in ctx.research.sources
        if item.get("status") == "completed"
    }

    for gap in gaps:
        if gap in completed_gaps:
            continue

        results = _search_duckduckgo(gap, max_results)

        normalized_sources = []
        for item in results:
            url = item.get("href") or item.get("url") or ""
            title = item.get("title") or url
            body = item.get("body") or item.get("snippet") or ""

            normalized_sources.append({
                "url": url,
                "title": title,
                "snippet": body,
            })

            if title or body:
                content = f"{title}\n{body}".strip()
                if url:
                    content += f"\nURL: {url}"

                ctx.sources.append(SourceRef(
                    origin="web_research",
                    content=content,
                    is_primary=False,
                    trust_level="unverified",
                ))

        ctx.research.sources.append({
            "gap": gap,
            "status": "completed",
            "engine": "duckduckgo",
            "results": normalized_sources,
        })

    ctx.run_log.append({
        "engine": "research",
        "status": "passed",
        "provider": "duckduckgo",
        "queries": len(gaps),
    })
