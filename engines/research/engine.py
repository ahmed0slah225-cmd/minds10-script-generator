"""
engines/research/engine.py
===========================
محرك البحث — القسم 19/21/22/77.

القاعدة الحاكمة الصارمة هنا:
    - لو ctx.research.enabled == False: لا يحدث أي اتصال خارجي إطلاقًا.
      المحرك يكتفي بما هو موجود بالفعل (مدخلات المستخدم، PDF، قاعدة معرفة سابقة).
    - لا يجوز لأي Skill أخرى تجاوز هذا القرار من تلقاء نفسها.
    - البحث يخدم القصة، وليس العكس: لا نجمع معلومات لمجرد إمكانية جمعها —
      حاليًا هذا يعني أن الاستعلامات يجب أن تُبنى من topic_understanding
      (الفجوات المعرفية المكتشفة)، لا بشكل عشوائي.
"""

from __future__ import annotations

from core.context import PipelineContext, SourceRef
from core.model_registry import require_capability
from providers.base import GenerationRequest, get_provider
from core.model_registry import get_model


def run(ctx: PipelineContext, *, model_id: str) -> None:
    if not ctx.research.enabled:
        # القاعدة 22: البحث متوقف = صفر استدعاءات خارجية. لا استثناءات.
        ctx.run_log.append({
            "engine": "research",
            "status": "skipped_by_user_setting",
        })
        return

    model_info = get_model(model_id)
    require_capability(model_id, "supports_search")  # يفشل بوضوح لو الموديل لا يدعم البحث

    gaps = ctx.topic_understanding.get("knowledge_gaps", [])
    if not gaps:
        # لا بحث بلا حاجة فعلية مكتشفة — القاعدة 19
        return

    provider = get_provider(model_info.provider)

    for gap in gaps:
        request = GenerationRequest(
            prompt=f"ابحث عن معلومات دقيقة وحديثة حول: {gap}",
            model_id=model_id,
            enable_search=True,
        )
        result = provider.generate(request)

        for src in result.search_sources:
            ctx.sources.append(SourceRef(
                origin="web_research",
                content=src.get("title") or src.get("url") or "",
                is_primary=False,
                trust_level="unverified",  # يبقى غير مؤكَّد حتى يمر بتحقق لاحق صريح
            ))
        ctx.research.sources.append({
            "gap": gap,
            "raw_text": result.text,
            "sources": result.search_sources,
        })
