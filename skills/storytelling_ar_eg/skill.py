"""
skills/storytelling_ar_eg/skill.py
=====================================
مهارة رواية القصص — القسم 16.

تبني هيكل: الوضع → سؤال → التوتر → اكتشاف → شرح → تعقيد → إنسايت → المردود.
أي جزء افتراضي (سيناريو غير حقيقي) لازم يتحدد صراحة بحقل is_hypothetical
بدل ما يتقدم كأنه حدث واقعي — التزامًا الصارم بالقسم 16 و45 (لا هلوسة).
"""

from __future__ import annotations

import json

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext
from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, get_provider

_SCHEMA = {
    "type": "object",
    "properties": {
        "arc": {
            "type": "object",
            "properties": {
                "situation": {"type": "string"},
                "question": {"type": "string"},
                "tension": {"type": "string"},
                "discovery": {"type": "string"},
                "explanation": {"type": "string"},
                "complication": {"type": "string"},
                "insight": {"type": "string"},
                "payoff": {"type": "string"},
            },
        },
        "is_hypothetical": {"type": "boolean"},
        "hypothetical_label": {"type": "string"},  # مثال: "سيناريو افتراضي" لو is_hypothetical=true
    },
    "required": ["arc", "is_hypothetical"],
}

_SYSTEM_PROMPT = (
    "أنت كاتب قصص لفيديوهات يوتيوب طويلة بالعامية المصرية. ابنِ هيكل قصة "
    "بالمسار: وضع، سؤال، توتر، اكتشاف، شرح، تعقيد، إنسايت، مردود — بناءً "
    "*فقط* على المعرفة والاستراتيجية المُعطاة. لو احتجت مثالًا أو سيناريو "
    "غير موثّق كحدث حقيقي، حدد is_hypothetical=true واكتب تصنيفًا واضحًا "
    "له (مثال/سيناريو/حالة افتراضية) — ممنوع تقديمه كأنه واقعة حقيقية."
)


class StorytellingSkill:
    manifest = SkillManifest(
        name="storytelling_ar_eg",
        version="1.0.0",
        purpose="بناء هيكل قصة يخدم الفيديو دون اختلاق وقائع حقيقية.",
        kind=SkillKind.GENERATION,
        stage=PipelineStage.PLANNING,
        scope_in=("story_arc",),
        scope_out=("presenting_hypothetical_as_real",),
        required_inputs=("topic_understanding", "knowledge_base", "strategy"),
        produced_outputs=("story",),
        constraints=("لا يقدّم سيناريو افتراضي كحدث حقيقي", "لا يخترع حقائق تخالف المعرفة المتاحة"),
        requires_llm=True,
    )

    def validate_input(self, ctx: PipelineContext) -> None:
        if not ctx.strategy:
            raise ValueError("storytelling_ar_eg: لا توجد استراتيجية (strategy) للبناء عليها.")

    def run(self, ctx: PipelineContext) -> SkillResult:
        model_id = ctx.model_selection.model_for("storytelling_ar_eg")
        model_info = get_model(model_id)
        require_capability(model_id, "supports_structured_output")
        provider = get_provider(model_info.provider)

        prompt = (
            f"الاستراتيجية:\n{ctx.strategy}\n\n"
            f"فهم الموضوع:\n{ctx.topic_understanding}\n\n"
            f"عناصر معرفة متاحة (بذور قصص محتملة ضمنها):\n{ctx.knowledge_base[:15]}"
        )
        request = GenerationRequest(prompt=prompt, system=_SYSTEM_PROMPT, model_id=model_id,
                                     structured_schema=_SCHEMA, temperature=0.6)
        result = provider.generate(request)
        data = result.structured_output or json.loads(result.text)

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"story": data}, model_used=model_id,
            tokens_in=result.tokens_in, tokens_out=result.tokens_out,
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        story = result.output.get("story", {})
        if story.get("is_hypothetical") and not story.get("hypothetical_label"):
            raise ValueError(
                "storytelling_ar_eg: عنصر افتراضي بدون تصنيف صريح (hypothetical_label) — "
                "مخالف للقاعدة 16/45."
            )
