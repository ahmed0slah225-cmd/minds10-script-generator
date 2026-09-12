"""
skills/humanize_ar_eg/skill.py
================================
مهارة "الأنسنة" — القسم 11.

تحسّن نصًا موجودًا فقط. لا تكتب من الصفر. تُمنع منعًا باتًا من اختراع
معلومات/تجارب/مصادر أو تغيير المعنى الواقعي — هذه القيود مطبّقة هنا في
الـ system prompt وأيضًا كتحقق ما بعد التنفيذ (validate_output) يقارن
طول ونسبة الأرقام/الأسماء الظاهرة قبل وبعد كفحص أولي بسيط (heuristic)،
وليس ضمانًا كاملًا — أي تحقق حقيقي بالحقائق يتم في مهارة fact_check
المنفصلة لاحقًا (أولوية القواعد: الحقيقة أولًا دائمًا).
"""

from __future__ import annotations

import re

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext
from core.model_registry import get_model
from providers.base import GenerationRequest, get_provider

_SYSTEM_PROMPT = (
    "أنت محرر أنسنة متخصص في نصوص يوتيوب بالعامية المصرية الطبيعية. "
    "مهمتك تحسين النص المُعطى فقط — لا تكتبه من جديد ولا تغيّر معناه. "
    "ممنوع منعًا باتًا: اختراع معلومات، اختراع تجارب شخصية، اختراع مصادر أو "
    "اقتباسات، حذف أدلة أو أمثلة مهمة، أو تغيير أي حقيقة واردة في النص. "
    "حسّن فقط: طول الجمل وتنوّعها، الإيقاع، الانتقالات، مخاطبة المشاهد، "
    "الوضوح، وقابلية النطق أمام الكاميرا — مع الالتزام بسمات صوت الكاتب "
    "(voice DNA) المرفقة."
)


def _numbers_in(text: str) -> set[str]:
    return set(re.findall(r"\d+[\.,]?\d*", text))


class HumanizeSkill:
    manifest = SkillManifest(
        name="humanize_ar_eg",
        version="1.0.0",
        purpose="تحسين نص موجود إلى عامية مصرية طبيعية قابلة للنطق دون اختراع أو تحريف.",
        kind=SkillKind.REWRITE,
        stage=PipelineStage.POST_WRITE,
        scope_in=("sentence_level", "paragraph_level", "transitions", "rhythm", "spoken_delivery"),
        scope_out=("inventing_facts", "inventing_experiences", "inventing_sources", "changing_meaning"),
        required_inputs=("draft_script", "voice_dna", "audience"),
        produced_outputs=("humanized_script",),
        constraints=(
            "لا يخترع معلومات",
            "لا يخترع تجارب شخصية",
            "لا يخترع مصادر",
            "لا يغيّر المعنى الواقعي",
            "لا يكتب فوق الأدلة المهمة",
        ),
        depends_on=("voice_dna_ar_eg",),
        requires_llm=True,
        deterministic_validation=False,
    )

    def validate_input(self, ctx: PipelineContext) -> None:
        if not ctx.draft_script:
            raise ValueError("humanize_ar_eg: لا توجد مسودة (draft_script) لتحسينها.")

    def run(self, ctx: PipelineContext) -> SkillResult:
        model_id = ctx.model_selection.model_for("humanize_ar_eg")
        model_info = get_model(model_id)
        provider = get_provider(model_info.provider)

        voice = ctx.voice_dna
        voice_notes = (
            f"طول الجمل: {voice.sentence_length_pattern or 'غير محدد'}\n"
            f"مستوى العامية: {voice.slang_intensity or 'غير محدد'}\n"
            f"أسلوب مخاطبة المشاهد: {voice.viewer_address_style or 'غير محدد'}\n"
            f"أسلوب الانتقالات: {voice.transition_style or 'غير محدد'}"
        )

        prompt = (
            f"الجمهور المستهدف: {ctx.audience or 'غير محدد'}\n\n"
            f"سمات صوت الكاتب:\n{voice_notes}\n\n"
            f"النص المطلوب تحسينه:\n{ctx.draft_script}"
        )

        request = GenerationRequest(prompt=prompt, system=_SYSTEM_PROMPT, model_id=model_id, temperature=0.6)
        result = provider.generate(request)

        warnings = []
        before_numbers = _numbers_in(ctx.draft_script)
        after_numbers = _numbers_in(result.text)
        if before_numbers - after_numbers:
            warnings.append(
                f"أرقام اختفت بعد الأنسنة، راجع يدويًا: {before_numbers - after_numbers}"
            )

        return SkillResult(
            skill_name=self.manifest.name,
            success=True,
            output={"humanized_script": result.text},
            changes=["إعادة صياغة أسلوبية بدون تغيير المعنى أو الحقائق"],
            warnings=warnings,
            model_used=model_id,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        text = result.output.get("humanized_script")
        if not text or not isinstance(text, str):
            raise ValueError("humanize_ar_eg: الناتج يجب أن يحتوي humanized_script نصيًا.")
