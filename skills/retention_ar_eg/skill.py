"""
skills/retention_ar_eg/skill.py
==================================
مهارة الاحتفاظ — نسخة معمّقة. القسم 12 + مبدأ "إيقاع الاحتفاظ" (راجع
references/retention_rhythm_ar_eg.md): الاحتفاظ مش حدث واحد في البداية،
هو إيقاع متكرر — نقطة تجديد اهتمام (re-hook) كل 2-3 دقايق تقريبًا.

- plan(): تبني outline بحيث كل قسم يؤدي للي بعده، **وتحسب فعليًا** هل
  المسافة بين نقاط تجديد الاهتمام معقولة (~260-450 كلمة) بناءً على مدة
  الفيديو المستهدفة، مش تكتفي بطلب "احتفاظ" عام من الموديل.
- review(): تتحقق: هل كل Open Loop اتقفل؟ فيه Clickbait؟ وكمان: هل فيه
  فجوات طويلة بين نقاط تجديد الاهتمام فعليًا في outline؟
"""

from __future__ import annotations

import json
import re

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext
from core.model_registry import get_model, require_capability
from providers.base import GenerationRequest, get_provider

# معدل كلام تقريبي بالعامية المصرية أمام كاميرا (كلمة/دقيقة) — يُستخدم
# فقط لتقدير حجم القسم المتوقع بالكلمات، مش رقمًا نهائيًا دقيقًا.
_WORDS_PER_MINUTE = 140
_REHOOK_MIN_MINUTES = 2
_REHOOK_MAX_MINUTES = 3

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
                    "estimated_word_count": {"type": "integer"},
                    "is_rehook_point": {"type": "boolean"},
                },
            },
        }
    },
}

_PLAN_SYSTEM_PROMPT = (
    "أنت مخطط احتفاظ (Retention) لفيديوهات يوتيوب طويلة. ابنِ ترتيب "
    "أقسام بحيث كل قسم يؤدي منطقيًا للي بعده، وكل سؤال مهم يُفتح، يُغلق "
    "بمردود واضح لاحقًا. مبدأ أساسي: الاحتفاظ إيقاع متكرر، مش حدث واحد "
    "في البداية — لازم نقطة تجديد اهتمام حقيقية (سؤال جديد أو كشف جزئي "
    "نابع من المحتوى نفسه، مش تشويق فارغ) كل 2-3 دقايق تقريبًا. لكل قسم "
    "قدّر عدد كلماته التقريبي وحدد صراحة هل هو نقطة تجديد اهتمام "
    "(is_rehook_point). ممنوع تمامًا: Clickbait، فضول فارغ، 'استنى لحد "
    "الآخر' بلا سبب حقيقي، أو Open Loops بلا إغلاق."
)

_CLICKBAIT_PATTERNS = [
    r"\bاستنى لحد الآخر\b", r"\bهتتصدم\b",
    r"\bمحدش قال لك ال?حقيقة\b", r"\bخليك لحد النهاية\b",
]


class RetentionSkill:
    manifest = SkillManifest(
        name="retention_ar_eg",
        version="2.0.0",
        purpose="بناء ومراجعة مسار احتفاظ حقيقي بإيقاع محسوب (re-hook كل 2-3 دقايق)، لا كليك بيت.",
        kind=SkillKind.PLANNING,
        stage=PipelineStage.PLANNING,
        scope_in=("outline_structure", "open_loops", "rehook_rhythm"),
        scope_out=("clickbait", "empty_curiosity"),
        required_inputs=("story", "strategy", "duration_minutes"),
        produced_outputs=("outline", "review_notes"),
        constraints=("لا Clickbait", "كل Open Loop لازم يتقفل", "لا تشويق فارغ بلا محتوى فعلي وراه"),
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

        target_words = (ctx.duration_minutes or 10) * _WORDS_PER_MINUTE
        rehook_window = f"{_REHOOK_MIN_MINUTES * _WORDS_PER_MINUTE}-{_REHOOK_MAX_MINUTES * _WORDS_PER_MINUTE} كلمة"

        prompt = (
            f"القصة:\n{ctx.story}\n\nالاستراتيجية:\n{ctx.strategy}\n\n"
            f"المدة المستهدفة: {ctx.duration_minutes or 'غير محددة'} دقيقة "
            f"(≈{target_words} كلمة إجمالاً)\n"
            f"نافذة إعادة الهوك المستهدفة: نقطة تجديد اهتمام كل {rehook_window} تقريبًا."
        )
        request = GenerationRequest(prompt=prompt, system=_PLAN_SYSTEM_PROMPT, model_id=model_id,
                                     structured_schema=_PLAN_SCHEMA, temperature=0.5)
        result = provider.generate(request)
        data = result.structured_output or json.loads(result.text)

        # فحص حتمي إضافي (بدون استدعاء LLM جديد): هل فعلاً في outline
        # المُرجَع فجوات كبيرة بين نقاط تجديد الاهتمام المُعلَّمة؟
        rhythm_warnings = self._check_rehook_rhythm(data.get("sections", []))

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"outline": data}, model_used=model_id,
            warnings=rhythm_warnings,
            tokens_in=result.tokens_in, tokens_out=result.tokens_out,
        )

    def _check_rehook_rhythm(self, sections: list[dict]) -> list[str]:
        """يتحقق حتميًا (بدون LLM) إن مفيش فجوة كلمات كبيرة بين نقطتين
        متتاليتين معلَّمتين is_rehook_point، بناءً على estimated_word_count
        اللي رجّعها الموديل نفسه — تحقق فعلي على أرقام حقيقية، مش ثقة عمياء."""
        warnings = []
        max_gap_words = _REHOOK_MAX_MINUTES * _WORDS_PER_MINUTE * 1.5  # هامش تسامح 50%
        running_gap = 0
        for section in sections:
            running_gap += section.get("estimated_word_count", 0) or 0
            if section.get("is_rehook_point"):
                running_gap = 0
            elif running_gap > max_gap_words:
                warnings.append(
                    f"فجوة كبيرة (~{running_gap} كلمة) من غير نقطة تجديد اهتمام قبل قسم "
                    f"'{section.get('title', '؟')}' — راجع إيقاع الاحتفاظ هنا."
                )
        return warnings

    def review(self, ctx: PipelineContext) -> SkillResult:
        text = ctx.humanized_script or ctx.draft_script or ""
        issues = []

        for pattern in _CLICKBAIT_PATTERNS:
            for m in re.finditer(pattern, text):
                issues.append({
                    "type": "clickbait_phrase", "match": m.group(0),
                    "reason": "عبارة تشويق فارغ بدون مردود محدد بعدها.",
                    "priority": "high",
                })

        open_questions = [s.get("opens_question") for s in ctx.outline.get("sections", []) if s.get("opens_question")]
        for q in open_questions:
            keywords = [w for w in re.findall(r"\w+", q) if len(w) > 3][:3]
            if keywords and not any(kw in text for kw in keywords):
                issues.append({
                    "type": "unclosed_open_loop", "match": q,
                    "reason": "سؤال اتفتح في الـoutline لكن مفيش إشارة واضحة لإغلاقه في النص.",
                    "priority": "high",
                })

        rhythm_warnings = self._check_rehook_rhythm(ctx.outline.get("sections", []))
        for w in rhythm_warnings:
            issues.append({"type": "rehook_rhythm_gap", "match": "", "reason": w, "priority": "medium"})

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"review_notes": issues}, warnings=[i["reason"] for i in issues],
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        if "outline" not in result.output and "review_notes" not in result.output:
            raise ValueError("retention_ar_eg: الناتج يجب أن يحتوي outline أو review_notes.")
