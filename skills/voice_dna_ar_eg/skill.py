"""
skills/voice_dna_ar_eg/skill.py
=================================
مهارة "الحمض النووي الصوتي" — القسم 9/10.

تُستخرج السمات الأسلوبية من عينات المستخدم عبر LLM (تحليل، وليس توليد
محتوى جديد)، وتُحفظ كـ VoiceDNAProfile دائم يُمرَّر لاحقًا لمحركات:
Hook, Story, Script, Humanize, المحرر النهائي — كطبقة "تأثير ثابت
وليس جامد" (القسم 10).

مهم: هذه المهارة لا تُنتج نصًا يُستخدم مباشرة في السكريبت — فقط ملف
سمات (profile). أي محاولة لإعادة استخدام نص العينات حرفيًا تُعتبر خرقًا
لعقد هذه المهارة (انظر scope_out في manifest.yaml).
"""

from __future__ import annotations

import json

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext, VoiceDNAProfile
from core.model_registry import require_capability
from providers.base import GenerationRequest, get_provider
from core.model_registry import get_model

_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "sentence_length_pattern": {"type": "string"},
        "rhythm_notes": {"type": "string"},
        "vocabulary_level": {"type": "string"},
        "slang_intensity": {"type": "string"},
        "question_usage": {"type": "string"},
        "viewer_address_style": {"type": "string"},
        "emotion_style": {"type": "string"},
        "explanation_style": {"type": "string"},
        "example_style": {"type": "string"},
        "storytelling_style": {"type": "string"},
        "transition_style": {"type": "string"},
        "curiosity_building": {"type": "string"},
        "metaphor_style": {"type": "string"},
        "idea_closing_style": {"type": "string"},
        "formality_level": {"type": "string"},
        "spontaneity_level": {"type": "string"},
    },
}

_SYSTEM_PROMPT = (
    "أنت محلّل أسلوبي متخصص في العامية المصرية المنطوقة على يوتيوب. "
    "مهمتك الوحيدة هي استخراج السمات الأسلوبية (وليس المحتوى أو الأفكار) "
    "من العينات المُعطاة. لا تنسخ جملًا من العينات، وصف الأسلوب فقط. "
    "أعد النتيجة كـ JSON مطابق تمامًا للمخطط المُعطى."
)


class VoiceDNASkill:
    manifest = SkillManifest(
        name="voice_dna_ar_eg",
        version="1.0.0",
        purpose="استخراج ملف سمات أسلوبية دائم من عينات المستخدم.",
        kind=SkillKind.PROFILE,
        stage=PipelineStage.PLANNING,
        scope_in=("voice_samples",),
        scope_out=("verbatim_text_reuse",),
        required_inputs=("voice_dna",),  # عينات تُمرَّر عبر constraints أو حقل مخصص
        produced_outputs=("voice_dna",),
        constraints=(
            "لا يعيد استخدام جمل العينات حرفيًا",
            "يستخرج سمات أسلوبية فقط، وليس أفكارًا أو حقائق من العينات",
        ),
        depends_on=(),
        requires_llm=True,
        deterministic_validation=False,
    )

    def validate_input(self, ctx: PipelineContext) -> None:
        samples = ctx.constraints.get("voice_samples")
        if not samples:
            raise ValueError("voice_dna_ar_eg: لا توجد عينات صوتية (voice_samples) للتحليل.")

    def run(self, ctx: PipelineContext) -> SkillResult:
        samples: list[str] = ctx.constraints.get("voice_samples", [])
        model_id = ctx.model_selection.model_for("voice_dna_ar_eg")
        require_capability(model_id, "supports_structured_output")

        model_info = get_model(model_id)
        provider = get_provider(model_info.provider)

        joined_samples = "\n---\n".join(samples)
        request = GenerationRequest(
            prompt=f"حلّل أسلوب الكاتب في العينات التالية:\n\n{joined_samples}",
            system=_SYSTEM_PROMPT,
            model_id=model_id,
            structured_schema=_EXTRACTION_SCHEMA,
            temperature=0.2,
        )
        result = provider.generate(request)

        try:
            data = result.structured_output or json.loads(result.text)
        except json.JSONDecodeError:
            return SkillResult(
                skill_name=self.manifest.name,
                success=False,
                error="فشل تحليل استجابة الموديل كـ JSON صالح.",
            )

        profile = VoiceDNAProfile(name=ctx.voice_dna.name or "default", **{
            k: v for k, v in data.items() if k in VoiceDNAProfile.__dataclass_fields__
        })
        ctx.voice_dna = profile

        return SkillResult(
            skill_name=self.manifest.name,
            success=True,
            output={"voice_dna": profile},
            model_used=model_id,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        if result.success and not isinstance(result.output.get("voice_dna"), VoiceDNAProfile):
            raise ValueError("voice_dna_ar_eg: الناتج يجب أن يكون VoiceDNAProfile صالحًا.")
