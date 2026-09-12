"""
skills/retention_ar_eg/skill.py
==================================
مهارة الاحتفاظ — القسم 12. منظومة كاملة، مش Hook Skill بس.

- plan(): تبني outline (ترتيب أقسام) بحيث كل قسم يؤدي للي بعده، وكل سؤال
  مهم بيتفتح بياخد Payoff محدد قبل ما نقفل.
- review(): بتاخد سكريبت فعلي وتتحقق: هل كل Open Loop اتقفل؟ فيه Clickbait
  أو فضول فارغ؟ — وترجع تقرير مشاكل زي anti_slop تمامًا (تكتشف ولا تكتب).
"""

from __future__ import annotations

import json
import re

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext
from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, get_provider

_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "purpose": {"type": "string"},
                    "opens_question": {"type": "string"},
                    "closes_question": {"type": "string"},
                    "transition_out": {"type": "string"},
                },
            },
        }
    },
}

_PLAN_SYSTEM_PROMPT = (
    "أنت مخطط احتفاظ (Retention) لفيديوهات يوتيوب طويلة. ابنِ ترتيب "
    "أقسام بحيث كل قسم يؤدي منطقيًا للي بعده، وكل سؤال مهم يُفتح، يُغلق "
    "بمردود واضح لاحقًا (ممكن في قسم تانٍ، لكن لازم يتقفل). ممنوع تمامًا: "
    "Clickbait، فضول فارغ، 'استنى للآخر' بلا سبب حقيقي، أو Open Loops بلا "
    "إغلاق. الاحتفاظ = اكتشاف تدريجي، مش إثارة زائفة."
)

_CLICKBAIT_PATTERNS = [
    r"\bاستنى لحد الآخر\b",
    r"\bهتتصدم\b",
    r"\bمحدش قال لك ال?حقيقة\b",
    r"\bخليك لحد النهاية\b",
]


class RetentionSkill:
    manifest = SkillManifest(
        name="retention_ar_eg",
        version="1.0.0",
        purpose="بناء ومراجعة مسار احتفاظ حقيقي (اكتشاف تدريجي، لا كليك بيت).",
        kind=SkillKind.PLANNING,
        stage=PipelineStage.PLANNING,
        scope_in=("outline_structure", "open_loops"),
        scope_out=("clickbait", "empty_curiosity"),
        required_inputs=("story", "strategy"),
        produced_outputs=("outline", "review_notes"),
        constraints=("لا Clickbait", "كل Open Loop لازم يتقفل"),
        requires_llm=True,
    )

    def validate_input(self, ctx: PipelineContext) -> None:
        if not ctx.story and not ctx.strategy:
            raise ValueError("retention_ar_eg: لا توجد قصة ولا استراتيجية للتخطيط عليهم.")

    def run(self, ctx: PipelineContext) -> SkillResult:
        return self.plan(ctx)

    def plan(self, ctx: PipelineContext) -> SkillResult:
        model_id = ctx.model_selection.model_for("retention_ar_eg")
        model_info = get_model(model_id)
        require_capability(model_id, "supports_structured_output")
        provider = get_provider(model_info.provider)

        prompt = f"القصة:\n{ctx.story}\n\nالاستراتيجية:\n{ctx.strategy}"
        request = GenerationRequest(prompt=prompt, system=_PLAN_SYSTEM_PROMPT, model_id=model_id,
                                     structured_schema=_PLAN_SCHEMA, temperature=0.5)
        result = provider.generate(request)
        data = result.structured_output or json.loads(result.text)

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"outline": data}, model_used=model_id,
            tokens_in=result.tokens_in, tokens_out=result.tokens_out,
        )

    def review(self, ctx: PipelineContext) -> SkillResult:
        """مراجعة حتمية جزئيًا: تفحص كليشيهات كليك بيت بالـregex، وتتحقق
        من إغلاق الأسئلة المفتوحة المذكورة في outline بمقارنة بسيطة مع
        نص السكريبت النهائي."""
        text = ctx.humanized_script or ctx.draft_script or ""
        issues = []

        for pattern in _CLICKBAIT_PATTERNS:
            for m in re.finditer(pattern, text):
                issues.append({
                    "type": "clickbait_phrase",
                    "match": m.group(0),
                    "reason": "عبارة تشويق فارغ بدون مردود محدد بعدها.",
                    "priority": "high",
                })

        open_questions = [s.get("opens_question") for s in ctx.outline.get("sections", []) if s.get("opens_question")]
        for q in open_questions:
            # فحص تقريبي: هل فيه إشارة لإجابة/كلمات مرتبطة بالسؤال لاحقًا في النص؟
            keywords = [w for w in re.findall(r"\w+", q) if len(w) > 3][:3]
            if keywords and not any(kw in text for kw in keywords):
                issues.append({
                    "type": "unclosed_open_loop",
                    "match": q,
                    "reason": "سؤال اتفتح في الـoutline لكن مفيش إشارة واضحة لإغلاقه في النص.",
                    "priority": "high",
                })

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"review_notes": issues},
            warnings=[i["reason"] for i in issues],
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        if "outline" not in result.output and "review_notes" not in result.output:
            raise ValueError("retention_ar_eg: الناتج يجب أن يحتوي outline أو review_notes.")
