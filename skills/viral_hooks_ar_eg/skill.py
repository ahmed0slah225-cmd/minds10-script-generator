"""
skills/viral_hooks_ar_eg/skill.py
====================================
مهارة الهوك — القسم 17. تنتج عدة خيارات، كل واحد مربوط صراحة بـ"الوعد"
اللي هيتحقق فعلاً في الفيديو (viewer_promise من strategy) — تحقق ما بعد
التنفيذ (validate_output) يرفض أي هوك من غير كذا.
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
        "hooks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "technique": {
                        "type": "string",
                        "enum": ["موقف", "ألم", "سؤال", "مفارقة", "غموض", "اكتشاف", "وعد"],
                    },
                    "fulfills_promise": {"type": "string"},  # كيف الهوك ده مرتبط بوعد الفيديو فعلاً
                },
                "required": ["text", "technique", "fulfills_promise"],
            },
        }
    },
}

_SYSTEM_PROMPT = (
    "أنت كاتب هوكس (أول 15-30 ثانية) لفيديوهات يوتيوب مصرية طويلة. "
    "اكتب 3 خيارات هوك مختلفة، كل واحد يستخدم تقنية مختلفة (موقف/ألم/"
    "سؤال/مفارقة/غموض/اكتشاف/وعد). الشرط الصارم: كل هوك لازم يفي فعلًا "
    "بما يعد به — اكتب صراحة إزاي الهوك ده مرتبط بوعد الفيديو الحقيقي، "
    "ممنوع الوعد بحاجة الفيديو مش هيقدمها."
)


class ViralHooksSkill:
    manifest = SkillManifest(
        name="viral_hooks_ar_eg",
        version="1.0.0",
        purpose="توليد هوكس تفي فعليًا بوعد الفيديو، بدون كليك بيت.",
        kind=SkillKind.GENERATION,
        stage=PipelineStage.PLANNING,
        scope_in=("opening_15_30_seconds",),
        scope_out=("false_promises",),
        required_inputs=("strategy", "story", "outline"),
        produced_outputs=("hooks",),
        constraints=("كل هوك لازم يفي بوعد الفيديو فعليًا",),
        requires_llm=True,
    )

    def validate_input(self, ctx: PipelineContext) -> None:
        if not ctx.strategy.get("viewer_promise"):
            raise ValueError("viral_hooks_ar_eg: لا يوجد وعد واضح للمشاهد (strategy.viewer_promise).")

    def run(self, ctx: PipelineContext) -> SkillResult:
        model_id = ctx.model_selection.model_for("viral_hooks_ar_eg")
        model_info = get_model(model_id)
        require_capability(model_id, "supports_structured_output")
        provider = get_provider(model_info.provider)

        prompt = (
            f"وعد الفيديو: {ctx.strategy.get('viewer_promise')}\n"
            f"الزاوية: {ctx.strategy.get('final_angle')}\n"
            f"القصة:\n{ctx.story}"
        )
        request = GenerationRequest(prompt=prompt, system=_SYSTEM_PROMPT, model_id=model_id,
                                     structured_schema=_SCHEMA, temperature=0.7)
        result = provider.generate(request)
        data = result.structured_output or json.loads(result.text)

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"hooks": data.get("hooks", [])}, model_used=model_id,
            tokens_in=result.tokens_in, tokens_out=result.tokens_out,
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        for hook in result.output.get("hooks", []):
            if not hook.get("fulfills_promise"):
                raise ValueError(
                    f"viral_hooks_ar_eg: الهوك '{hook.get('text')}' بدون ربط واضح بوعد الفيديو — مرفوض."
                )
