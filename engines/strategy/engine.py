"""
engines/strategy/engine.py
=============================
محرك الاستراتيجية — يحوّل الفهم + المعرفة + الجمهور لقرار واضح:
إيه الرسالة المركزية، إيه الزاوية النهائية، إيه الوعد اللي هنلتزم بيه،
وإيه الهيكل العام قبل الدخول لتفاصيل القصة.
"""

from __future__ import annotations

from core.context import PipelineContext
from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, get_provider

_SCHEMA = {
    "type": "object",
    "properties": {
        "central_message": {"type": "string"},
        "final_angle": {"type": "string"},
        "viewer_promise": {"type": "string"},
        "key_points_order": {"type": "array", "items": {"type": "string"}},
        "must_address_objections": {"type": "array", "items": {"type": "string"}},
        "success_definition": {"type": "string"},
    },
    "required": ["central_message", "final_angle", "viewer_promise"],
}

_SYSTEM_PROMPT = (
    "أنت استراتيجي محتوى يوتيوب. بناءً على فهم الموضوع والمعرفة المتاحة "
    "وملف الجمهور، حدد: الرسالة المركزية للفيديو، الزاوية النهائية "
    "(المحددة، مش العامة)، الوعد الصريح للمشاهد، ترتيب منطقي للنقاط "
    "الرئيسية، الاعتراضات اللي لازم تتعالج صراحة، وتعريف واضح لمعنى "
    "'نجاح' هذا الفيديو تحديدًا."
)


def run(ctx: PipelineContext, *, model_id: str) -> None:
    model_info = get_model(model_id)
    require_capability(model_id, "supports_structured_output")
    provider = get_provider(model_info.provider)

    prompt = (
        f"فهم الموضوع:\n{ctx.topic_understanding}\n\n"
        f"ملخص المعرفة المتاحة (عدد العناصر: {len(ctx.knowledge_base)}):\n"
        f"{ctx.knowledge_base[:15]}\n\n"
        f"ملف الجمهور:\n{ctx.constraints.get('audience_profile', ctx.audience)}\n\n"
        f"المدة المستهدفة: {ctx.duration_minutes} دقيقة"
    )

    request = GenerationRequest(prompt=prompt, system=_SYSTEM_PROMPT, model_id=model_id,
                                 structured_schema=_SCHEMA, temperature=0.4)
    result = provider.generate(request)

    import json
    ctx.strategy = result.structured_output or json.loads(result.text)

    ctx.log_run(engine="strategy", skill=None, model_id=model_id, status="passed",
                tokens_in=result.tokens_in, tokens_out=result.tokens_out)
