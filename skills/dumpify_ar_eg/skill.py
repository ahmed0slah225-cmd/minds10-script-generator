"""
skills/dumpify_ar_eg/skill.py
================================
مهارة "البكم" (Dumpify) — القسم 18. تبسيط دون تسطيح.

مهارة اختيارية غير مربوطة بمرحلة إجبارية في الـPipeline الحالي — تُستدعى
يدويًا (مثلاً من المحرر النهائي) على مقطع بعينه يبان معقّد على الجمهور،
مش على السكريبت كله دفعة واحدة.
"""

from __future__ import annotations

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext
from core.model_registry import get_model
from providers.base import GenerationRequest, get_provider

_SYSTEM_PROMPT = (
    "أنت محرر تبسيط متخصص. مهمتك تبسيط النص المُعطى للجمهور المحدد، لكن "
    "بدون: حذف التعقيد الضروري لفهم الفكرة، تسطيح الموضوع، أو جعل كل "
    "الجمل بنفس الطول القصير. التبسيط الحقيقي يحافظ على العمق ويقرّبه، "
    "مش يشيله."
)


class DumpifySkill:
    manifest = SkillManifest(
        name="dumpify_ar_eg",
        version="1.0.0",
        purpose="تبسيط مقطع معقد دون تسطيحه أو حذف تعقيده الضروري.",
        kind=SkillKind.REWRITE,
        stage=PipelineStage.POST_WRITE,
        scope_in=("specific_complex_passage",),
        scope_out=("removing_necessary_complexity", "uniform_short_sentences"),
        required_inputs=("draft_script", "audience"),
        produced_outputs=("simplified_text",),
        constraints=("لا يحذف تعقيدًا ضروريًا", "لا يسطّح الموضوع"),
        requires_llm=True,
    )

    def validate_input(self, ctx: PipelineContext) -> None:
        if not ctx.constraints.get("dumpify_target_passage"):
            raise ValueError(
                "dumpify_ar_eg: لازم تحدد المقطع المطلوب تبسيطه صراحة "
                "(constraints['dumpify_target_passage'])."
            )

    def run(self, ctx: PipelineContext) -> SkillResult:
        model_id = ctx.model_selection.model_for("dumpify_ar_eg")
        model_info = get_model(model_id)
        provider = get_provider(model_info.provider)

        passage = ctx.constraints["dumpify_target_passage"]
        prompt = f"الجمهور: {ctx.audience or 'غير محدد'}\n\nالمقطع:\n{passage}"
        request = GenerationRequest(prompt=prompt, system=_SYSTEM_PROMPT, model_id=model_id, temperature=0.5)
        result = provider.generate(request)

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"simplified_text": result.text}, model_used=model_id,
            tokens_in=result.tokens_in, tokens_out=result.tokens_out,
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        if not result.output.get("simplified_text"):
            raise ValueError("dumpify_ar_eg: الناتج يجب أن يحتوي simplified_text.")
