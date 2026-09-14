"""
skills/viral_hooks_ar_eg/skill.py
====================================
مهارة الهوك — نسخة معمّقة. القسم 17 + مبدأ "وضع كتابة + وضع تدقيق" لكل
مهارة (مُستخرج من دراسة بنية content-skills: كل مهارة كتابة عندها نمط
Writing mode للصياغة الجديدة، ونمط Audit mode لتقييم مسودة موجودة أصلاً
— بدل ما تكون المهارة قادرة بس على "الكتابة من الصفر").

- generate(): 3 هوكس مختلفة، كل واحد لازم يفي فعليًا بوعد الفيديو.
- audit(): تاخد هوك موجود بالفعل (من مسودة مكتوبة يدويًا أو من مرحلة
  سابقة) وتقيّمه ضد 4 أسباب شائعة لفشل الفتحات، بدل ما تفترض إنه كويس.
"""

from __future__ import annotations

import json

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext
from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, get_provider

_GEN_SCHEMA = {
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
                    "fulfills_promise": {"type": "string"},
                },
                "required": ["text", "technique", "fulfills_promise"],
            },
        }
    },
}

_GEN_SYSTEM_PROMPT = (
    "أنت كاتب هوكس (أول 15-30 ثانية) لفيديوهات يوتيوب مصرية طويلة. "
    "اكتب 3 خيارات هوك مختلفة، كل واحد يستخدم تقنية مختلفة (موقف/ألم/"
    "سؤال/مفارقة/غموض/اكتشاف/وعد). الشرط الصارم: كل هوك لازم يفي فعلًا "
    "بما يعد به — اكتب صراحة إزاي الهوك ده مرتبط بوعد الفيديو الحقيقي، "
    "ممنوع الوعد بحاجة الفيديو مش هيقدمها. تجنّب الأسباب الشائعة لفشل "
    "الفتحات: بداية بطيئة من غير أي مخاطر أو أهمية واضحة، وعد غامض مش "
    "محدد، افتتاحية عامة نمطية ('في الفيديو ده هنتكلم عن')، ودفن الفكرة "
    "الأهم بدل تقديمها فورًا."
)

# 4 أسباب شائعة لفشل فتحة فيديو — مُكيَّفة كأداة تدقيق حتمية جزئيًا
_OPENER_KILLERS = {
    "slow_start_no_stakes": {
        "check_keywords": ["في الفيديو ده", "هنتكلم عن", "النهاردة هنشوف"],
        "reason": "بداية عامة نمطية بلا مخاطر أو أهمية واضحة من أول جملة.",
    },
    "vague_promise": {
        "check_keywords": ["حاجات كتير", "أشياء مهمة", "معلومات مفيدة"],
        "reason": "وعد غامض مش محدد — المشاهد مش هيعرف هياخد إيه بالظبط.",
    },
    "generic_opener": {
        "check_keywords": ["أهلا بيكم", "إزيكم يا شباب", "welcome back"],
        "reason": "افتتاحية ترحيبية عامة بتاخد وقت قبل ما توصل للمحتوى الفعلي.",
    },
    "buried_lede": {
        "check_keywords": [],  # يحتاج حكم LLM، مش regex بسيط
        "reason": "الفكرة الأهم مدفونة بعد مقدمة طويلة بدل ما تتقدم فورًا.",
    },
}

_AUDIT_SYSTEM_PROMPT = (
    "أنت مدقق هوكس يوتيوب. هتاخد هوك موجود ووعد الفيديو، وتقيّمه ضد 4 "
    "أسباب فشل شائعة: (1) بداية بطيئة من غير مخاطر/أهمية واضحة، (2) وعد "
    "غامض غير محدد، (3) افتتاحية عامة نمطية، (4) دفن الفكرة الأهم بدل "
    "تقديمها فورًا. لكل سبب حدد هل موجود في الهوك ده (true/false) ولو "
    "موجود، اشرح باختصار وقدّم صياغة بديلة مباشرة. أعد JSON فقط."
)

_AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "slow_start_no_stakes": {"type": "boolean"},
        "vague_promise": {"type": "boolean"},
        "generic_opener": {"type": "boolean"},
        "buried_lede": {"type": "boolean"},
        "explanation": {"type": "string"},
        "suggested_rewrite": {"type": "string"},
        "passes_audit": {"type": "boolean"},
    },
    "required": ["passes_audit"],
}


class ViralHooksSkill:
    manifest = SkillManifest(
        name="viral_hooks_ar_eg",
        version="2.0.0",
        purpose="توليد هوكس تفي فعليًا بوعد الفيديو + تدقيق هوكس موجودة ضد 4 أسباب فشل شائعة.",
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
        return self.generate(ctx)

    def generate(self, ctx: PipelineContext) -> SkillResult:
        model_id = ctx.model_selection.model_for("viral_hooks_ar_eg")
        model_info = get_model(model_id)
        require_capability(model_id, "supports_structured_output")
        provider = get_provider(model_info.provider)

        prompt = (
            f"وعد الفيديو: {ctx.strategy.get('viewer_promise')}\n"
            f"الزاوية: {ctx.strategy.get('final_angle')}\n"
            f"القصة:\n{ctx.story}"
        )
        request = GenerationRequest(prompt=prompt, system=_GEN_SYSTEM_PROMPT, model_id=model_id,
                                     structured_schema=_GEN_SCHEMA, temperature=0.7)
        result = provider.generate(request)
        data = result.structured_output or json.loads(result.text)
        hooks = data.get("hooks", [])

        # تدقيق حتمي سريع (بدون استدعاء إضافي) على كل هوك مُولَّد —
        # علامات على أسباب الفشل الشائعة قبل حتى ما نعرضها كخيارات
        for hook in hooks:
            hook["deterministic_warnings"] = self._quick_deterministic_check(hook.get("text", ""))

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"hooks": hooks}, model_used=model_id,
            tokens_in=result.tokens_in, tokens_out=result.tokens_out,
        )

    def _quick_deterministic_check(self, hook_text: str) -> list[str]:
        warnings = []
        for killer_name, killer in _OPENER_KILLERS.items():
            if any(kw in hook_text for kw in killer["check_keywords"]):
                warnings.append(killer["reason"])
        return warnings

    def audit(self, ctx: PipelineContext, hook_text: str) -> SkillResult:
        """وضع التدقيق (Audit mode) — يقيّم هوك *موجود بالفعل* (يمكن مكتوب
        يدويًا أو من مصدر خارجي)، بدل الافتراض إن كل هوك مُولَّد كويس
        تلقائيًا. القسم 5: ممنوع تشغيل Generator كأنه Reviewer — عشان
        كده دي دالة منفصلة صراحة، مش جزء من generate()."""
        model_id = ctx.model_selection.model_for("viral_hooks_ar_eg")
        model_info = get_model(model_id)
        require_capability(model_id, "supports_structured_output")
        provider = get_provider(model_info.provider)

        prompt = f"وعد الفيديو: {ctx.strategy.get('viewer_promise')}\n\nالهوك المطلوب تدقيقه:\n{hook_text}"
        request = GenerationRequest(prompt=prompt, system=_AUDIT_SYSTEM_PROMPT, model_id=model_id,
                                     structured_schema=_AUDIT_SCHEMA, temperature=0.2)
        result = provider.generate(request)
        data = result.structured_output or json.loads(result.text)

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"hook_audit": data}, model_used=model_id,
            tokens_in=result.tokens_in, tokens_out=result.tokens_out,
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        for hook in result.output.get("hooks", []):
            if not hook.get("fulfills_promise"):
                raise ValueError(
                    f"viral_hooks_ar_eg: الهوك '{hook.get('text')}' بدون ربط واضح بوعد الفيديو — مرفوض."
                )
