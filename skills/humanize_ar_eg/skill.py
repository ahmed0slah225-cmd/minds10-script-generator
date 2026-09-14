"""
skills/humanize_ar_eg/skill.py
================================
مهارة "الأنسنة" — نسخة معمّقة بعد دراسة فعلية لـ harshaneel/humanize.

راجع references/nine_levers_ar_eg.md للتفاصيل الكاملة والتكييف.

أهم شيئين اتاخدوا من المصدر الأصلي فعليًا (مش بس إلهام عام):

1) الروافع التسعة اتحولت لتعليمات صريحة في الـsystem prompt (مش قائمة
   عامة "اكتب طبيعي") — كل رافعة بندها الخاص.

2) **التحقق يحصل بقراءة فعلية للنص الناتج، مش بالثقة في التزام الموديل
   وقت الكتابة** — عشان كده الدالة دلوقتي فيها خطوة `_self_audit` تستدعي
   نفس الموديل تاني كـ"مراجع" يقرأ نتيجته هو بالظبط ويرجّع تقرير التزام،
   مش يعتمد على كونه "كتب صح من الأول".

القيود الصارمة اتفقت عليها المصدرين (harshaneel/humanize والمواصفات
الأصلية للمشروع، القسم 45/64) بشكل مستقل: **ممنوع اختراع تفاصيل دقيقة
لسد فجوة غموض** — لو التفصيل مش موجود، يتعلّم كفجوة صراحة، مش يُخترع.
"""

from __future__ import annotations

import json
import re

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext
from core.model_registry import get_model
from providers.base import GenerationRequest, get_provider

_SYSTEM_PROMPT = (
    "أنت محرر أنسنة متخصص في نصوص يوتيوب بالعامية المصرية المنطوقة. "
    "مهمتك تحسين النص المُعطى فقط — لا تكتبه من جديد ولا تغيّر معناه. "
    "طبّق الروافع التسعة دي بالظبط:\n"
    "1) تجنّب القوالب الجاهزة والصياغات المتوقعة — نوّع اختيار الكلمات.\n"
    "2) نوّع طول الجمل بعنف: جملة قصيرة قوية، بعدها جملة أطول بتتمدد على فكرة.\n"
    "3) شيل عبارات التحوّط الزيادة ('من الممكن أن'، 'قد يكون') لو المعلومة "
    "مؤكدة فعلاً — لكن لو المعلومة غير مؤكدة، سيبها 'غير مؤكد' صراحة "
    "(القاعدة دي أعلى أولوية من أي رافعة تانية).\n"
    "4) فكّك أي بنية شكلية (نقاط معدودة، تعداد جامد) لكلام متصل طبيعي — "
    "محدش بيتكلم بنقاط أمام الكاميرا.\n"
    "5) ممنوع منعًا باتًا اختراع أي رقم أو اسم أو تفصيل دقيق غير موجود في "
    "النص الأصلي أو المعرفة المتاحة — لو ناقص، سيبه غامض أو علّمه.\n"
    "6) طابق درجة العامية ومستوى الرسمية مع سمات صوت الكاتب المرفقة.\n"
    "7) امسح أي أداة ربط رسمية ('علاوة على ذلك'، 'بالإضافة إلى ذلك') — "
    "الربط الطبيعي بيكون بسؤال أو إشارة للي فات.\n"
    "8) علامات الترقيم دلالة نبرة للتسجيل الصوتي فقط — نقطة = وقفة، فاصلة "
    "= استمرار، من غير شرطات طويلة درامية.\n"
    "9) خلي للنص رأي وموقف واضح يخدم القصة، مش نبرة محايدة متوازنة "
    "طول الوقت.\n\n"
    "ممنوع منعًا باتًا أيضًا: اختراع تجارب شخصية، اختراع مصادر أو "
    "اقتباسات، حذف أدلة أو أمثلة مهمة، أو تغيير أي حقيقة واردة في النص."
)

_AUDIT_SYSTEM_PROMPT = (
    "أنت مراجع جودة أنسنة. هتاخد نص أصلي ونص بعد الأنسنة، وتتحقق فعليًا "
    "(بالقراءة الفعلية للنص الناتج، مش بالافتراض) من: هل اتحذفت أي حقيقة "
    "أو رقم أو اسم كان موجود في الأصلي؟ هل انضاف أي تفصيل دقيق (رقم/اسم) "
    "مش موجود في الأصلي؟ هل النص لسه فيه أي أداة ربط رسمية زي 'علاوة على "
    "ذلك'؟ أعد النتيجة JSON فقط: "
    '{"deleted_facts": [...], "invented_specifics": [...], '
    '"remaining_formal_transitions": [...], "passed": true|false}'
)

_AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "deleted_facts": {"type": "array", "items": {"type": "string"}},
        "invented_specifics": {"type": "array", "items": {"type": "string"}},
        "remaining_formal_transitions": {"type": "array", "items": {"type": "string"}},
        "passed": {"type": "boolean"},
    },
    "required": ["passed"],
}


def _numbers_in(text: str) -> set[str]:
    return set(re.findall(r"\d+[\.,]?\d*", text))


class HumanizeSkill:
    manifest = SkillManifest(
        name="humanize_ar_eg",
        version="2.0.0",
        purpose="تحسين نص موجود إلى عامية مصرية طبيعية عبر 9 روافع أنسنة محددة، مع تدقيق ذاتي بعد الكتابة.",
        kind=SkillKind.REWRITE,
        stage=PipelineStage.POST_WRITE,
        scope_in=("sentence_level", "paragraph_level", "transitions", "rhythm", "spoken_delivery"),
        scope_out=("inventing_facts", "inventing_experiences", "inventing_sources", "changing_meaning"),
        required_inputs=("draft_script", "voice_dna", "audience"),
        produced_outputs=("humanized_script",),
        constraints=(
            "لا يخترع معلومات", "لا يخترع تجارب شخصية", "لا يخترع مصادر",
            "لا يغيّر المعنى الواقعي", "لا يكتب فوق الأدلة المهمة",
            "لا يخترع تفاصيل دقيقة (أرقام/أسماء) لسد فجوة غموض",
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
        humanized_text = result.text

        warnings = list(self._deterministic_checks(ctx.draft_script, humanized_text))

        # خطوة التدقيق الذاتي — القاعدة الأهم من harshaneel/humanize:
        # تحقّق بقراءة فعلية للناتج، مش افتراض التزام وقت الكتابة.
        audit_warnings, audit_tokens_in, audit_tokens_out = self._self_audit(
            provider, model_id, ctx.draft_script, humanized_text
        )
        warnings.extend(audit_warnings)

        return SkillResult(
            skill_name=self.manifest.name,
            success=True,
            output={"humanized_script": humanized_text},
            changes=["إعادة صياغة أسلوبية عبر 9 روافع أنسنة، بدون تغيير المعنى أو الحقائق"],
            warnings=warnings,
            model_used=model_id,
            tokens_in=result.tokens_in + audit_tokens_in,
            tokens_out=result.tokens_out + audit_tokens_out,
        )

    def _deterministic_checks(self, before: str, after: str):
        """فحوصات حتمية سريعة (بدون استدعاء إضافي) قبل حتى التدقيق بالـLLM."""
        before_numbers = _numbers_in(before)
        after_numbers = _numbers_in(after)
        if before_numbers - after_numbers:
            yield f"أرقام اختفت بعد الأنسنة، راجع يدويًا: {before_numbers - after_numbers}"
        if after_numbers - before_numbers:
            yield f"أرقام جديدة ظهرت بعد الأنسنة مش موجودة بالأصل — تحقق إنها مش مخترعة: {after_numbers - before_numbers}"

        formal_transitions = ["علاوة على ذلك", "بالإضافة إلى ذلك", "في الختام"]
        found = [t for t in formal_transitions if t in after]
        if found:
            yield f"أدوات ربط رسمية لسه موجودة بعد الأنسنة: {found}"

    def _self_audit(self, provider, model_id: str, original: str, humanized: str):
        """يستدعي نفس الموديل كـ'مراجع مستقل' يقرأ الناتج فعليًا (القاعدة
        الأهم من harshaneel/humanize: enforcement بالقراءة الفعلية للنص
        النهائي، مش بالثقة إن الكتابة التزمت وهي بتحصل)."""
        request = GenerationRequest(
            prompt=f"النص الأصلي:\n{original}\n\nالنص بعد الأنسنة:\n{humanized}",
            system=_AUDIT_SYSTEM_PROMPT,
            model_id=model_id,
            structured_schema=_AUDIT_SCHEMA,
            temperature=0.0,
        )
        try:
            result = provider.generate(request)
            data = result.structured_output or json.loads(result.text)
        except Exception:
            # التدقيق الذاتي اختياري — فشله ما ينفعش يوقف الأنسنة نفسها،
            # لكن لازم يتسجل كتحذير واضح بدل ما يتبلع بصمت
            return (["تعذّر إجراء التدقيق الذاتي بعد الأنسنة — راجع يدويًا."], 0, 0)

        warnings = []
        if data.get("deleted_facts"):
            warnings.append(f"التدقيق الذاتي رصد حقائق محذوفة: {data['deleted_facts']}")
        if data.get("invented_specifics"):
            warnings.append(f"التدقيق الذاتي رصد تفاصيل مخترعة محتملة: {data['invented_specifics']}")
        if data.get("remaining_formal_transitions"):
            warnings.append(f"التدقيق الذاتي رصد أدوات ربط رسمية متبقية: {data['remaining_formal_transitions']}")

        return (warnings, result.tokens_in, result.tokens_out)

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        text = result.output.get("humanized_script")
        if not text or not isinstance(text, str):
            raise ValueError("humanize_ar_eg: الناتج يجب أن يحتوي humanized_script نصيًا.")
