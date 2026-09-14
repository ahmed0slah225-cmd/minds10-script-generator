"""
engines/knowledge/engine.py
=============================
طبقة المعرفة — القسم 20. البحث/المصادر لا تدخل مباشرة للكاتب؛ تمر من هنا
أولًا لتتحول لعناصر معرفة (Knowledge Items) مُصنَّفة بوضوح حسب مصدرها:

    user_provided | source_backed | research_derived | model_inference | unverified

القاعدة الصارمة: أي معلومة غير مؤكدة تبقى "unverified" ولا تتحول لحقيقة
في النص لاحقًا — محرك السكريبت (engines/script/engine.py) يستقبل
knowledge_base بالكامل ويُطلب منه صراحة عدم اختراع ما هو خارجها.
"""

from __future__ import annotations

from core.context import PipelineContext
from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, get_provider

_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "kind": {
                        "type": "string",
                        "enum": ["fact", "quote", "example", "number", "story", "contradiction"],
                    },
                    "origin": {
                        "type": "string",
                        "enum": ["user_provided", "source_backed", "research_derived",
                                 "model_inference", "unverified"],
                    },
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                },
                "required": ["content", "kind", "origin"],
            },
        }
    },
}

_SYSTEM_PROMPT = (
    "أنت مسؤول بناء قاعدة معرفة (Knowledge Base) لسكريبت يوتيوب. مهمتك "
    "تنظيم المعلومات المتاحة فقط — لا تخترع أي معلومة جديدة. لكل عنصر "
    "حدد: نوعه (حقيقة/اقتباس/مثال/رقم/قصة/تناقض)، ومصدره الحقيقي "
    "(مُقدَّم من المستخدم، مدعوم بمصدر، مشتق من بحث، استدلال نموذجي غير "
    "مؤكد)، ومستوى الثقة. أي معلومة غير مؤكدة يجب تصنيفها 'unverified' "
    "صراحة ولا يُسمح بترقيتها لحقيقة."
)


def run(ctx: PipelineContext, *, model_id: str) -> None:
    if not ctx.sources and not ctx.topic_understanding.get("known_facts"):
        # مفيش أي مادة خام معرفية — لا داعي لاستدعاء LLM بلا محتوى
        ctx.knowledge_base = []
        return

    model_info = get_model(model_id)
    require_capability(model_id, "supports_structured_output")
    provider = get_provider(model_info.provider)

    sources_block = "\n---\n".join(
        f"[{s.origin} | primary={s.is_primary} | trust={s.trust_level}]\n{s.content}"
        for s in ctx.sources if s.content
    )
    known_facts = "\n".join(f"- {f}" for f in ctx.topic_understanding.get("known_facts", []))

    prompt = (
        f"حقائق مستخرجة من فهم الموضوع:\n{known_facts or '(لا يوجد)'}\n\n"
        f"المصادر المتاحة:\n{sources_block or '(لا يوجد)'}\n\n"
        f"نتائج بحث خارجي (لو وُجدت):\n{ctx.research.sources or '(لا يوجد)'}"
    )

    request = GenerationRequest(
        prompt=prompt, system=_SYSTEM_PROMPT, model_id=model_id,
        structured_schema=_SCHEMA, temperature=0.2,
    )
    result = provider.generate(request)

    import json
    data = result.structured_output or json.loads(result.text)
    ctx.knowledge_base = data.get("items", [])

    ctx.log_run(engine="knowledge", skill=None, model_id=model_id, status="passed",
                tokens_in=result.tokens_in, tokens_out=result.tokens_out)
