"""
engines/audience/engine.py
=============================
محرك تحليل الجمهور — يحوّل وصف جمهور خام (أو تخمين من topic_understanding)
لملف جمهور فعلي: اهتمامات، مستوى معرفة متوقع، اعتراضات، لغة مناسبة.
هذا الملف يُستهلك لاحقًا في الاستراتيجية والقصة والهوك والأنسنة.
"""

from __future__ import annotations

from core.context import PipelineContext
from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, get_provider

_SCHEMA = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "knowledge_level": {"type": "string", "enum": ["مبتدئ", "متوسط", "متقدم"]},
        "interests": {"type": "array", "items": {"type": "string"}},
        "pain_points": {"type": "array", "items": {"type": "string"}},
        "likely_objections": {"type": "array", "items": {"type": "string"}},
        "tone_fit": {"type": "string"},
    },
    "required": ["description", "knowledge_level"],
}

_SYSTEM_PROMPT = (
    "أنت محلل جمهور لمحتوى يوتيوب مصري. بناءً على وصف الجمهور والموضوع "
    "المُعطى، حدد: وصف دقيق للجمهور، مستوى معرفته المتوقع بالموضوع، "
    "اهتماماته ذات الصلة، نقاط ألمه المرتبطة بالمشكلة، اعتراضات محتملة "
    "هيقولها وهو بيتفرج، ونبرة الكلام المناسبة له. لا تُعمّم بلا أساس من "
    "المُعطيات."
)


def run(ctx: PipelineContext, *, model_id: str) -> None:
    model_info = get_model(model_id)
    require_capability(model_id, "supports_structured_output")
    provider = get_provider(model_info.provider)

    prompt = (
        f"وصف الجمهور من المستخدم: {ctx.audience or '(لم يُحدَّد — استنتج من الموضوع)'}\n"
        f"الموضوع: {ctx.topic_understanding.get('title', '')}\n"
        f"المشكلة الإنسانية: {ctx.topic_understanding.get('human_problem', '')}"
    )

    request = GenerationRequest(prompt=prompt, system=_SYSTEM_PROMPT, model_id=model_id,
                                 structured_schema=_SCHEMA, temperature=0.3)
    result = provider.generate(request)

    import json
    data = result.structured_output or json.loads(result.text)
    ctx.constraints["audience_profile"] = data
    if not ctx.audience:
        ctx.audience = data.get("description")

    ctx.log_run(engine="audience", skill=None, model_id=model_id, status="passed",
                tokens_in=result.tokens_in, tokens_out=result.tokens_out)
