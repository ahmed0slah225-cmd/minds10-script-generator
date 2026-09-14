"""
core/contracts.py
==================
العقود الأساسية (Contracts) التي يلتزم بها أي Engine أو Skill في المشروع.

القاعدة الذهبية:
    Skill حقيقية = معرفة + قواعد + منطق + قيود + عقد إدخال + عقد إخراج
                  + سياسة تنفيذ + تحقق من الصحة + تكامل + اختبارات.

هذا الملف لا يحتوي على أي منطق أعمال (business logic) — فقط الأشكال
(shapes) التي يجب أن يلتزم بها كل Engine/Skill حتى يستطيع الـ Orchestrator
التعامل معهم بشكل موحّد دون معرفة تفاصيلهم الداخلية.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# تصنيف نوع المهارة (القاعدة 5: المهارات ليست كلها من نفس النوع)
# ---------------------------------------------------------------------------
class SkillKind(str, Enum):
    GENERATION = "generation"      # مهارة جيل (تنتج محتوى جديد)
    PLANNING = "planning"          # مهارة تخطيط (استراتيجية/هيكلة)
    ANALYSIS = "analysis"          # مهارة تحليل (بحث/استخراج)
    REVIEW = "review"              # مهارة مراجعة (تكتشف مشاكل، لا تكتب)
    REWRITE = "rewrite"            # مهارة إعادة كتابة (تعدل نصًا موجودًا)
    GUIDANCE = "guidance"          # مهارة توجيه (تنتج قواعد/تعليمات لمهارة أخرى)
    PROFILE = "profile"            # مهارة ملف شخصي (مثل Voice DNA)
    VALIDATION = "validation"      # مهارة تحقق (حتمية غالبًا، بدون LLM)


class PipelineStage(str, Enum):
    """متى تعمل المهارة داخل الـ Pipeline."""
    PLANNING = "planning"
    WRITING = "writing"
    POST_WRITE = "post_write"
    REVIEW = "review"
    EDITING = "editing"
    FINAL_REVIEW = "final_review"


# ---------------------------------------------------------------------------
# عقد المهارة (Skill Contract) — القسم 3 و 40 و 41 من المواصفات
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SkillManifest:
    """
    البيان الرسمي (Manifest) لأي Skill في المشروع.
    كل Skill جديدة *يجب* أن تُعرّف واحدًا من هذه قبل تسجيلها في SkillRegistry.
    مجرد وجود ملف SKILL.md لا يُعتبر تنفيذًا — راجع القاعدة 60.
    """
    name: str                       # اسم فريد، مثال: "humanize_ar_eg"
    version: str                    # semver، مثال: "1.0.0"
    purpose: str                    # ما المشكلة التي تحلها؟
    kind: SkillKind
    stage: PipelineStage
    scope_in: tuple[str, ...]       # ما الذي *تعدّله*
    scope_out: tuple[str, ...]      # ما الذي *لا* تعدّله أبدًا
    required_inputs: tuple[str, ...]        # مفاتيح متوقعة من PipelineContext
    produced_outputs: tuple[str, ...]       # مفاتيح تُكتب في PipelineContext
    constraints: tuple[str, ...]            # قيود صارمة (ممنوعات)
    depends_on: tuple[str, ...] = ()        # أسماء Skills/Engines أخرى مطلوبة قبلها
    conflicts_with: tuple[str, ...] = ()    # Skills لا يجوز تشغيلها معًا بلا ترتيب واضح
    requires_llm: bool = True               # القاعدة 38: ليس كل Skill تحتاج LLM
    deterministic_validation: bool = False  # هل يوجد تحقق حتمي (regex/قواعد) لنتيجتها؟


@runtime_checkable
class Skill(Protocol):
    """الواجهة (Interface) التي يجب أن يلتزم بها أي كائن Skill قابل للتنفيذ."""

    manifest: SkillManifest

    def validate_input(self, ctx: "PipelineContext") -> None:
        """يرفع استثناء واضح لو المدخلات ناقصة أو غير متوافقة مع العقد."""
        ...

    def run(self, ctx: "PipelineContext") -> "SkillResult":
        """التنفيذ الفعلي. يُفترض أن validate_input تم استدعاؤها قبله."""
        ...

    def validate_output(self, ctx: "PipelineContext", result: "SkillResult") -> None:
        """تحقق ما بعد التنفيذ: هل فعلاً حافظت على القواعد (الحقيقة، الصوت، ...)؟"""
        ...


@dataclass
class SkillResult:
    """ناتج تنفيذ أي Skill — موحّد الشكل حتى يفهمه الـ Orchestrator دائمًا."""
    skill_name: str
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    changes: list[str] = field(default_factory=list)       # وصف التغييرات المُجراة
    warnings: list[str] = field(default_factory=list)
    quality_metrics: dict[str, float] = field(default_factory=dict)
    model_used: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    duration_ms: int = 0
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# ترتيب أولوية القواعد عند التعارض — القسم 44 و 45 (مبدأ حاكم، غير قابل للكسر)
# ---------------------------------------------------------------------------
RULE_PRIORITY: tuple[str, ...] = (
    "truth",            # 1. الحقيقة
    "source_integrity",  # 2. سلامة المصدر
    "meaning",           # 3. المعنى
    "clarity",           # 4. الوضوح
    "voice_dna",         # 5. الحمض النووي الصوتي
    "human_naturalness",  # 6. الطبيعة البشرية
    "retention",         # 7. الاحتفاظ
    "style_polish",      # 8. طلاء النمط
)
