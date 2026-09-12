"""
engines/common.py
==================
دالة مساعدة مشتركة تستخدمها كل الـ Engines لاستدعاء الـ LLMProvider، حتى لا
يكرر كل Engine منطق اختيار الموديل والتسجيل (logging) بنفسه.
"""

from __future__ import annotations
import time
from typing import Optional, Dict, Any

from core.context import PipelineContext
from core import model_registry
from providers.base import LLMProvider, LLMRequest, LLMResponse


def call_llm(
    ctx: PipelineContext,
    provider: LLMProvider,
    engine_name: str,
    system_prompt: str,
    user_prompt: str,
    allow_web_search: bool = False,
    thinking_level: str = "medium",
    response_schema: Optional[Dict[str, Any]] = None,
) -> LLMResponse:
    model_id = ctx.model_for(engine_name)

    # البحث لا يعمل أبدًا إلا لو المستخدم فعّله صراحة على مستوى المشروع (بند 22)
    effective_search = allow_web_search and ctx.research_config.enabled

    request = LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model_id=model_id,
        enable_web_search=effective_search,
        thinking_level=thinking_level,
        response_schema=response_schema,
    )

    start = time.time()
    response = provider.generate(request)
    duration = time.time() - start

    ctx.log(
        engine_name,
        "error" if not response.ok else "ok",
        {
            "model_id": model_id,
            "duration_sec": round(duration, 2),
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "used_web_search": response.used_web_search,
            "error": response.error,
        },
    )
    if not response.ok:
        ctx.warnings.append(f"[{engine_name}] {response.error}")

    return response


EGYPTIAN_ARABIC_STYLE_GUIDE = """
قواعد اللغة الإلزامية للمخرجات:
- عامية مصرية طبيعية قابلة للنطق أمام الكاميرا، وليست فصحى ولا عامية مفتعلة.
- نوّع طول الجمل: جمل قصيرة وأخرى أطول، بإيقاع كلام حقيقي.
- استخدم أسئلة حقيقية توجَّه للمشاهد بين الحين والآخر.
- أمثلة محسوسة ومواقف يومية بدل الكلام النظري المجرد.
- انتقالات طبيعية بين الأفكار، بدون عبارات ربط جاهزة ومكررة (زي "وفي النهاية"، "بس المفاجأة إن").
- ممنوع الحشو، العموميات، الكلام العميق الفارغ، والصياغة الآلية.
- لا تخترع معلومة أو مصدرًا أو اقتباسًا أو تجربة شخصية غير موجودة في السياق المُعطى.
- إذا لم تكن متأكدًا من معلومة: اكتب "غير مؤكد" أو "يحتاج تحقق" بدل اختلاقها.
"""
