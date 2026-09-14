"""
engines/script/engine.py
==========================
محرك كتابة السكريبت — يعمل *بعد* الفهم/البحث/المعرفة/الاستراتيجية/القصة/
الهوك، وليس قبلها (المبدأ الحاكم: لا تبدأ بالكتابة، ابدأ بالفهم).

هذا المحرك يكتب المسودة الأولى فقط (draft_script). التحسين الأسلوبي
(Voice DNA + Humanize) والمراجعة (Anti-Slop, Retention, تكرار...) تحدث
في مراحل لاحقة منفصلة — لا تُخلط هنا (القسم 6).
"""

from __future__ import annotations

from core.context import PipelineContext
from core.model_registry import get_model
from providers.base import GenerationRequest, get_provider

_SYSTEM_PROMPT = (
    "أنت كاتب سكريبتات يوتيوب طويلة بالعامية المصرية. اكتب بناءً *فقط* على "
    "الاستراتيجية والقصة والهيكل والمعرفة المُعطاة لك. لا تخترع معلومات أو "
    "مصادر أو اقتباسات غير موجودة فيما أُعطي لك. لو معلومة غير مؤكدة، اكتب "
    "'غير مؤكد' أو 'يحتاج تحقق' صراحة بدل اختراعها."
)


def run(ctx: PipelineContext, *, model_id: str) -> None:
    model_info = get_model(model_id)
    provider = get_provider(model_info.provider)

    prompt = (
        f"العنوان/الموضوع: {ctx.topic_understanding.get('title', ctx.project_name)}\n"
        f"الجمهور: {ctx.audience or 'غير محدد'}\n"
        f"المدة المستهدفة: {ctx.duration_minutes or 'غير محددة'} دقيقة\n\n"
        f"الاستراتيجية:\n{ctx.strategy}\n\n"
        f"القصة:\n{ctx.story}\n\n"
        f"الهيكل/الخطوط العريضة:\n{ctx.outline}\n\n"
        f"الهوك المختار:\n{ctx.hooks[0] if ctx.hooks else 'لا يوجد بعد'}\n\n"
        f"عناصر المعرفة المتاحة (يجب الالتزام بها حرفيًا وعدم اختراع غيرها):\n"
        f"{ctx.knowledge_base}"
    )

    request = GenerationRequest(prompt=prompt, system=_SYSTEM_PROMPT, model_id=model_id, temperature=0.7)
    result = provider.generate(request)

    ctx.draft_script = result.text
    ctx.log_run(engine="script", skill=None, model_id=model_id, status="draft_generated",
                tokens_in=result.tokens_in, tokens_out=result.tokens_out)
