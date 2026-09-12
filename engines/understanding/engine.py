"""
engines/understanding/engine.py
=================================
محرك الفهم — قلب المبدأ الحاكم للمشروع كله: "لا تبدأ بالكتابة، ابدأ بالفهم".

مرحلتان منفصلتان تنتميان لنفس المحرك المفاهيمي:

1) input_understanding: فهم *شكل* المدخل نفسه — هل هو فكرة خام؟ نص طويل؟
   فيه PDF مرفق؟ فيه رابط؟ ما لغته؟ ما طوله؟ — بدون أي تفسير موضوعي بعد.
   هذه خطوة حتمية بسيطة (لا تحتاج LLM) تجهّز القرار: هل نحتاج
   source_analysis (PDF) قبل topic_understanding أو لأ.

2) topic_understanding: الفهم الفعلي العميق للمادة — القسم 1 من المواصفات:
   الموضوع، المشكلة الإنسانية، الفكرة المركزية، الزاوية، الجمهور المتوقع،
   ما نعرفه بالفعل، ما نحتاج للبحث عنه (knowledge_gaps — يُستهلك مباشرة في
   engines/research/engine.py)، الأدلة المطلوبة، بذور القصص، الاعتراضات
   المحتملة، الوعد للمشاهد، تلميح للهيكل ومسار الاحتفاظ.

الناتج (ctx.topic_understanding) هو ما تُبنى عليه كل المراحل اللاحقة —
لو غاب أو كان سطحيًا، الاستراتيجية والقصة والهوك كلها هتتبني على أساس ضعيف.
"""

from __future__ import annotations

from core.context import PipelineContext
from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, get_provider

_TOPIC_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "human_problem": {"type": "string"},
        "core_idea": {"type": "string"},
        "angle": {"type": "string"},
        "audience_hint": {"type": "string"},
        "known_facts": {"type": "array", "items": {"type": "string"}},
        "knowledge_gaps": {"type": "array", "items": {"type": "string"}},
        "evidence_needed": {"type": "array", "items": {"type": "string"}},
        "story_seeds": {"type": "array", "items": {"type": "string"}},
        "objections": {"type": "array", "items": {"type": "string"}},
        "viewer_promise": {"type": "string"},
        "structure_hint": {"type": "string"},
        "retention_path_hint": {"type": "string"},
    },
    "required": ["title", "human_problem", "core_idea", "angle", "viewer_promise"],
}

_SYSTEM_PROMPT = (
    "أنت محلل مواضيع متخصص في محتوى يوتيوب طويل بالعامية المصرية. مهمتك "
    "الوحيدة هي *الفهم* قبل أي كتابة — لا تكتب أي سكريبت أو مقدمة الآن. "
    "حلّل المادة الخام المُعطاة واستخرج: الموضوع، المشكلة الإنسانية "
    "الحقيقية وراءه، الفكرة المركزية، زاوية مميزة للتناول، تخمين عن "
    "الجمهور المناسب، الحقائق المعروفة بالفعل من المادة نفسها، فجوات "
    "معرفية حقيقية تحتاج بحثًا خارجيًا (لو وُجدت فعلاً ولا تخترعها لمجرد "
    "الاكتمال)، أدلة مطلوبة لدعم الفكرة، بذور قصص ممكنة، اعتراضات محتملة "
    "من المشاهد، وعد واضح للمشاهد (هيخرج بإيه من الفيديو)، وتلميح مبدئي "
    "للهيكل ومسار الاحتفاظ بالانتباه. أعد النتيجة JSON مطابقًا للمخطط."
)


def run_input_understanding(ctx: PipelineContext, *, model_id: str) -> None:
    """خطوة حتمية بسيطة — لا تحتاج LLM (القاعدة 38)."""
    has_pdf = bool(ctx.constraints.get("pdf_path"))
    has_links = bool(ctx.constraints.get("user_links"))
    word_count = len(ctx.raw_input.split()) if ctx.raw_input else 0

    ctx.constraints["input_profile"] = {
        "has_raw_text": bool(ctx.raw_input),
        "has_pdf": has_pdf,
        "has_user_links": has_links,
        "raw_word_count": word_count,
        "requires_source_analysis": has_pdf,
    }
    ctx.log_run(engine="input_understanding", skill=None, model_id=None, status="passed")


def run_topic_understanding(ctx: PipelineContext, *, model_id: str) -> None:
    if not ctx.raw_input and not ctx.sources:
        raise ValueError(
            "topic_understanding: لا توجد مادة خام (raw_input) ولا مصادر (sources) للفهم منها. "
            "لازم تُدخل فكرة أو نص أو ملف قبل ما نقدر نبدأ."
        )

    model_info = get_model(model_id)
    require_capability(model_id, "supports_structured_output")
    provider = get_provider(model_info.provider)

    primary_sources_text = "\n---\n".join(
        s.content for s in ctx.sources if s.is_primary and s.content
    )

    prompt = (
        f"المادة الخام من المستخدم:\n{ctx.raw_input or '(لا يوجد نص مباشر)'}\n\n"
        f"محتوى من مصادر أساسية مرفقة (لو وُجدت):\n{primary_sources_text or '(لا يوجد)'}\n\n"
        f"الجمهور اللي حدده المستخدم (لو حدد): {ctx.audience or 'غير محدد بعد'}\n"
        f"المدة المستهدفة: {ctx.duration_minutes or 'غير محددة'} دقيقة"
    )

    request = GenerationRequest(
        prompt=prompt,
        system=_SYSTEM_PROMPT,
        model_id=model_id,
        structured_schema=_TOPIC_SCHEMA,
        temperature=0.4,
    )
    result = provider.generate(request)

    import json
    data = result.structured_output or json.loads(result.text)

    ctx.topic_understanding = data
    if not ctx.audience and data.get("audience_hint"):
        ctx.audience = data["audience_hint"]

    ctx.log_run(engine="topic_understanding", skill=None, model_id=model_id, status="passed",
                tokens_in=result.tokens_in, tokens_out=result.tokens_out)
