"""
skills/anti_slop_ar_eg/skill.py
================================
مهارة "مكافحة الانزلاق" — نسخة معمّقة.

مبنية بعد دراسة فعلية لمصدرين حقيقيين وتكييف مبادئهم (مش نسخ):
  - hardikpandya/stop-slop: كتالوج 8 فئات أنماط + rubric تقييم 5 أبعاد
  - conorbronsdon/avoid-ai-writing: نظام tiers للمفردات + أولوية P0/P1/P2
    + القاعدة الحاسمة: لا تخترع تفاصيل دقيقة لسد فجوة غموض، بلّغ عنها.

راجع references/patterns_ar_eg.md للتفاصيل الكاملة والمصادر.

هذه مهارة REVIEW حتمية بالكامل (require_llm=False) — تكتشف ولا تكتب،
بنفس ترتيب القسم 13: تحليل → نتيجة → تحديد المشاكل → شرح → اقتراح
إصلاحات. التطبيق الفعلي يحصل لاحقًا في engines/editor/engine.py
(final_edit) للإصلاحات عالية الثقة فقط.
"""

from __future__ import annotations

import re

from core.contracts import PipelineStage, SkillKind, SkillManifest, SkillResult
from core.context import PipelineContext

# ---------------------------------------------------------------------------
# 1) فتح كلام فاضي / حشو — Throat-clearing openers (stop-slop فئة 1)
# ---------------------------------------------------------------------------
_THROAT_CLEARING = [
    (r"\bفي الحقيقة\b", "فتحة جملة حشو متكررة — لو الجملة حقيقية بالفعل، الحشو ده مش لازم."),
    (r"\bالحقيقة إن\b", "نفس نمط 'في الحقيقة' — احذفها وابدأ بالفكرة مباشرة."),
    (r"\bالمهم جدًا هنا إن\b", "صياغة رسمية تخبر المشاهد بدل ما تُشركه."),
    (r"\bفي عالم اليوم\b", "افتتاحية عمومية جاهزة، من أوضح علامات الكتابة الآلية."),
    (r"\bفي النهاية\b", "خاتمة جاهزة/آلية — فكّر في إنهاء مرتبط فعليًا بالمحتوى."),
    (r"\bفي الختام\b", "خاتمة جاهزة/آلية."),
    (r"\bدعونا نتعمق\b|\bيلا بينا نتعمق\b", "انتقال آلي شائع في نصوص الذكاء الاصطناعي."),
    (r"\bزي ما قلنا\b|\bزي ما ذكرنا\b", "إحالة لكلام سابق — تأكد إنه فعلاً اتقال قبل كده مش حشو."),
]

# ---------------------------------------------------------------------------
# 2) تباين ثنائي جاهز — Binary contrasts (stop-slop فئة 2)
# ---------------------------------------------------------------------------
_BINARY_CONTRASTS = [
    (r"مش كده[،,]?\s*لكن كده", "قالب تباين ثنائي جاهز (Not X. But Y) — بديل: قول الفكرة مباشرة."),
    (r"مبقاش\s+\S+[،,]?\s*بقى\s+\S+", "قالب 'stops being X and starts being Y' — كرره مرتين يبقى نمط آلي."),
]

# ---------------------------------------------------------------------------
# 3) الوكالة الزائفة — False agency (مفاهيم مجردة بتعمل أفعال بشرية)
# ---------------------------------------------------------------------------
_FALSE_AGENCY = [
    (r"\bالمشكلة\s+بتحل\s+نفسها\b", "وكالة زائفة: مفهوم مجرد (المشكلة) بيعمل فعل بشري (يحل). مين اللي بيحلها فعليًا؟"),
    (r"\bالفكرة\s+بتوصلك\s+لوحدها\b", "وكالة زائفة مشابهة — حدد مين/إيه اللي بيوصّل الفكرة فعليًا."),
]

# ---------------------------------------------------------------------------
# 4) صدق مصطنع — Performed candor
# ---------------------------------------------------------------------------
_PERFORMED_CANDOR = [
    (r"\bخليني أكون صريح معاك\b", "صدق مُعلَن بدل صدق فعلي — احذفها واخلي المحتوى نفسه صريح."),
    (r"\bبصراحة كده\b", "نفس النمط — لو الكلام صريح فعلاً، مش محتاج إعلان."),
]

# ---------------------------------------------------------------------------
# 5) كلمات مطلقة + مكثّفات AI — Absolute words / AI intensifiers
# ---------------------------------------------------------------------------
_ABSOLUTE_WORDS = [r"\bدايمًا\b", r"\bأبدًا\b", r"\bكل الناس\b", r"\bمحدش\b", r"\bكل حاجة\b"]
_AI_INTENSIFIERS = [r"\bعميقًا\b", r"\bجذريًا\b", r"\bحرفيًا\b", r"\bبشكل كبير جدًا\b"]

_ALL_FILLER_PATTERNS: list[tuple[str, str]] = (
    _THROAT_CLEARING
    + [(p, "تباين ثنائي جاهز يقرأ كقالب آلي.") for p, _ in _BINARY_CONTRASTS]
    + _FALSE_AGENCY
    + _PERFORMED_CANDOR
)


def _find_filler(text: str) -> list[dict]:
    issues = []
    for pattern, reason in _ALL_FILLER_PATTERNS:
        for m in re.finditer(pattern, text):
            issues.append({
                "type": "filler_phrase", "match": m.group(0), "position": m.start(),
                "reason": reason,
                "suggested_fix": "احذف العبارة أو استبدلها بانتقال طبيعي مبني على المحتوى نفسه.",
                "priority": "medium",
            })
    return issues


def find_repetition_issues(text: str) -> list[dict]:
    """واجهة عامة يُعاد استخدامها من engines/review/engine.py لمرحلة
    repetition_review المنفصلة، بدل تكرار نفس منطق كشف التكرار."""
    return _find_repetitive_sentences(text)


def _find_repetitive_sentences(text: str) -> list[dict]:
    sentences = [s.strip() for s in re.split(r"[.!؟\n]", text) if s.strip()]
    issues = []
    seen: dict[str, int] = {}
    for idx, sentence in enumerate(sentences):
        key = sentence[:30]
        if key in seen and len(key) > 10:
            issues.append({
                "type": "repetition", "match": sentence, "position": idx,
                "reason": "جملة تكاد تكرر جملة سابقة بنفس المعنى تقريبًا.",
                "suggested_fix": "ادمج الفكرتين أو احذف التكرار مع الحفاظ على المعلومة الأهم.",
                "priority": "low",
            })
        seen[key] = idx
    return issues


def _find_tripling(sentences: list[str]) -> list[dict]:
    """كشف التثليث الآلي (Rule of three) — القسم من stop-slop: 3 عناصر
    متتالية بنفس الصياغة النحوية تقريبًا (نفس عدد الكلمات ± 1) هي علامة
    قالب جاهز، مش تنوع طبيعي."""
    issues = []
    lengths = [len(s.split()) for s in sentences]
    for i in range(len(sentences) - 2):
        trio = lengths[i:i + 3]
        if all(trio) and max(trio) - min(trio) <= 1 and min(trio) >= 3:
            issues.append({
                "type": "rule_of_three", "match": " | ".join(sentences[i:i + 3])[:120],
                "position": i,
                "reason": "3 جمل متتالية بنفس الطول تقريبًا — قد يكون تثليث آلي بدل تنوع طبيعي.",
                "suggested_fix": "غيّر طول واحدة منهم أو ادمج اتنين، بشرط الجملة تستاهل فعلاً 3 عناصر.",
                "priority": "low",
            })
    return issues


def _find_absolute_and_intensifiers(text: str) -> list[dict]:
    issues = []
    for pattern in _ABSOLUTE_WORDS:
        for m in re.finditer(pattern, text):
            issues.append({
                "type": "absolute_word", "match": m.group(0), "position": m.start(),
                "reason": "تعميم مطلق بلا دليل محدد — لو صح فعلاً، اذكر الدليل؛ لو مبالغة، خففها.",
                "suggested_fix": "استبدلها بوصف دقيق للحالة، أو اذكر الدليل اللي بيثبتها.",
                "priority": "low",
            })
    for pattern in _AI_INTENSIFIERS:
        for m in re.finditer(pattern, text):
            issues.append({
                "type": "ai_intensifier", "match": m.group(0), "position": m.start(),
                "reason": "مكثّف مستخدم كحشو بدل وصف دقيق.",
                "suggested_fix": "احذفه أو استبدله بتفصيل ملموس يوضح الحجم/العمق فعليًا.",
                "priority": "low",
            })
    return issues


def _score_dimension(issue_count: int, total_sentences: int, base: float = 10.0) -> float:
    if total_sentences == 0:
        return base
    ratio = issue_count / max(total_sentences, 1)
    return round(max(1.0, base - (ratio * 30)), 1)


class AntiSlopSkill:
    manifest = SkillManifest(
        name="anti_slop_ar_eg",
        version="2.0.0",
        purpose=(
            "اكتشاف علامات AI Slop في النص العربي المصري (حشو، تباين ثنائي جاهز، "
            "وكالة زائفة، تثليث آلي، كلمات مطلقة، صدق مصطنع) واقتراح إصلاحات دون "
            "تطبيقها — مبني على دراسة stop-slop وavoid-ai-writing."
        ),
        kind=SkillKind.REVIEW,
        stage=PipelineStage.POST_WRITE,
        scope_in=("draft_script",),
        scope_out=("rewriting_text_directly", "deleting_evidence_or_examples", "inventing_specifics_to_fix_vagueness"),
        required_inputs=("draft_script", "humanized_script"),
        produced_outputs=("anti_slop_report",),
        constraints=(
            "لا يحذف أدلة أو أمثلة مهمة",
            "لا يعيد كتابة النص مباشرة",
            "لا يخترع مشاكل غير موجودة فعليًا في النص",
            "لا يقترح إضافة تفاصيل دقيقة (أرقام/أسماء) غير موجودة أصلاً — يُعلِّم الفجوة فقط",
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

        issues = (
            _find_filler(text)
            + _find_repetitive_sentences(text)
            + _find_tripling(sentences)
            + _find_absolute_and_intensifiers(text)
        )

        total = max(len(sentences), 1)
        medium_high = [i for i in issues if i["priority"] in ("medium", "high")]
        repetition_issues = [i for i in issues if i["type"] == "repetition"]

        # القسم 14: نظام تقييم بـ5 أبعاد (مُكيَّف من stop-slop) — 1-10 لكل بُعد
        directness = _score_dimension(len([i for i in issues if i["type"] == "filler_phrase"]), total)
        rhythm = _score_dimension(len([i for i in issues if i["type"] == "rule_of_three"]), total)
        trust = _score_dimension(len([i for i in issues if i["type"] == "absolute_word"]), total)
        authenticity = _score_dimension(len(medium_high), total)
        density = _score_dimension(len(repetition_issues) + len([i for i in issues if i["type"] == "ai_intensifier"]), total)

        total_score = round(directness + rhythm + trust + authenticity + density, 1)

        report = {
            "issues": issues,
            "scores": {
                "directness": directness, "rhythm": rhythm, "trust": trust,
                "authenticity": authenticity, "density": density,
                "total_over_50": total_score,
                "needs_revision": total_score < 35,  # عتبة stop-slop: أقل من 35/50
            },
            "total_sentences": len(sentences),
        }

        return SkillResult(
            skill_name=self.manifest.name, success=True,
            output={"anti_slop_report": report}, changes=[],
            warnings=[i["reason"] for i in issues if i["priority"] == "medium"],
            quality_metrics=report["scores"],
        )

    def validate_output(self, ctx: PipelineContext, result: SkillResult) -> None:
        if "anti_slop_report" not in result.output:
            raise ValueError("anti_slop_ar_eg: الناتج يجب أن يحتوي anti_slop_report.")
        if result.changes:
            raise ValueError("anti_slop_ar_eg: هذه مهارة مراجعة فقط، يجب ألا تُنتج تغييرات مباشرة على النص.")
