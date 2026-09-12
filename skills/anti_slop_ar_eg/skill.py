"""
skills/anti_slop_ar_eg/skill.py
================================
مهارة "مكافحة الانزلاق" — تكتشف ولا تكتب. القسم 13/14/43.

هذه مهارة تصنيفها REVIEW ولا تحتاج LLM (require_llm=False) — تعتمد على
قواعد حتمية (قوائم عبارات، regex بسيطة) بدل استدعاء موديل لكل مراجعة،
تنفيذًا للقاعدة 38 (وفّر التكلفة والـ latency حيث لا حاجة فعلية لـ reasoning).

الترتيب الذي تفرضه القاعدة 13:
    تحليل → نتيجة → تحديد المشاكل → شرح المشاكل → اقتراح إصلاحات
    → (المحرر لاحقًا يطبّق الإصلاحات الصالحة فقط، وليس هذه المهارة)
"""

from __future__ import annotations

import re

from core.contracts import (
    PipelineStage,
    SkillKind,
    SkillManifest,
    SkillResult,
)
from core.context import PipelineContext

# عبارات حشو/انزلاق شائعة في النص العربي المولَّد بالذكاء الاصطناعي.
# قائمة قابلة للتوسّع — هذه بداية فقط، تُبنى فعليًا من دراسة stop-slop
# (المصدر 7 في المواصفات) بعد تكييفها للعربية المصرية.
_FILLER_PATTERNS: list[tuple[str, str]] = [
    (r"\bفي النهاية\b", "خاتمة جاهزة/آلية — فكّر في إنهاء مرتبط فعليًا بالمحتوى"),
    (r"\bفي عالم اليوم\b", "افتتاحية عمومية جاهزة"),
    (r"\bمن المهم جدًا أن نفهم\b", "صياغة رسمية زائدة تخبر المشاهد بدل ما تُشركه"),
    (r"\bدعونا نتعمق\b", "انتقال آلي شائع في نصوص AI"),
    (r"\bفي الختام\b", "خاتمة جاهزة/آلية"),
    (r"\bباختصار\b", "قد تكون علامة تلخيص فارغ — تحقق من وجود قيمة فعلية بعدها"),
]

_REPETITION_WINDOW = 40  # عدد الكلمات التي نبحث خلالها عن تكرار نفس الجملة تقريبًا


def _find_filler(text: str) -> list[dict]:
    issues = []
    for pattern, reason in _FILLER_PATTERNS:
        for m in re.finditer(pattern, text):
            issues.append({
                "type": "filler_phrase",
                "match": m.group(0),
                "position": m.start(),
                "reason": reason,
                "suggested_fix": "احذف العبارة أو استبدلها بانتقال طبيعي مبني على المحتوى نفسه.",
                "priority": "medium",
            })
    return issues


def _find_repetitive_sentences(text: str) -> list[dict]:
    sentences = [s.strip() for s in re.split(r"[.!؟\n]", text) if s.strip()]
    issues = []
    seen: dict[str, int] = {}
    for idx, sentence in enumerate(sentences):
        key = sentence[:30]
        if key in seen and len(key) > 10:
            issues.append({
                "type": "repetition",
                "match": sentence,
                "position": idx,
                "reason": "جملة تكاد تكرر جملة سابقة بنفس المعنى تقريبًا.",
                "suggested_fix": "ادمج الفكرتين أو احذف التكرار مع الحفاظ على المعلومة الأهم.",
                "priority": "low",
            })
        seen[key] = idx
    return issues


def _score_dimension(issue_count: int, total_sentences: int) -> float:
    """تقييم تقريبي حتمي من 1 إلى 10 — كلما قلّت نسبة المشاكل زاد السكور."""
    if total_sentences == 0:
        return 10.0
    ratio = issue_count / max(total_sentences, 1)
    score = max(1.0, 10.0 - (ratio * 30))
    return round(score, 1)


class AntiSlopSkill:
    manifest = SkillManifest(
        name="anti_slop_ar_eg",
        version="1.0.0",
        purpose="اكتشاف علامات AI Slop في النص العربي المصري واقتراح إصلاحات دون تطبيقها.",
        kind=SkillKind.REVIEW,
        stage=PipelineStage.POST_WRITE,
        scope_in=("draft_script",),
        scope_out=("rewriting_text_directly", "deleting_evidence_or_examples"),
        required_inputs=("draft_script", "humanized_script"),
        produced_outputs=("anti_slop_report",),
        constraints=(
            "لا يحذف أدلة أو أمثلة مهمة",
            "لا يعيد كتابة النص مباشرة",
            "لا يخترع مشاكل غير موجودة فعليًا في النص",
        ),
        requires_llm=False,
        deterministic_validation=True,
    )

    def validate_input(self, ctx: PipelineContext) -> None:
        text = ctx.humanized_script or ctx.draft_script
        if not text:
            raise ValueError("anti_slop_ar_eg: لا يوجد نص (draft_script/humanized_script) لمراجعته.")

    def run(self, ctx: PipelineContext) -> SkillResult:
        text = ctx.humanized_script or ctx.draft_script or ""
        sentences = [s for s in re.split(r"[.!؟\n]", text) if s.strip()]

        issues = _find_filler(text) + _find_repetitive_sentences(text)

        naturalness = _score_dimension(len(issues), len(sentences))
        repetition_issues = [i for i in issues if i["type"] == "repetition"]
        clarity = _score_dimension(len(repetition_issues), len(sentences))

        report = {
            "issues": issues,
            "scores": {
                "naturalness": naturalness,
                "clarity": clarity,
                # الأبعاد الأخرى (كثافة المعلومات، قوة اللغة، الإحساس بالـAI)
                "info_density": None,   # يحتاج تحليلًا دلاليًا أعمق — placeholder صريح
                "language_strength": None,
                "ai_feel": naturalness,
            },
            "total_sentences": len(sentences),
        }

        return SkillResult(
            skill_name=self.manifest.name,
            success=True,
            output={"anti_slop_report": report},
            changes=[],  # هذه المهارة لا تعدّل النص أبدًا
            warnings=[i["reason"] for i in issues if i["priority"] == "medium"],
            quality_metrics={"naturalness": naturalness, "clarity": clarity},
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        if "anti_slop_report" not in result.output:
            raise ValueError("anti_slop_ar_eg: الناتج يجب أن يحتوي anti_slop_report.")
        if result.changes:
            raise ValueError("anti_slop_ar_eg: هذه مهارة مراجعة فقط، يجب ألا تُنتج تغييرات مباشرة على النص.")
