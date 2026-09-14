"""
اختبارات المنطق العميق المُضاف للمهارات بعد دراسة المصادر الحقيقية
(stop-slop, avoid-ai-writing, harshaneel/humanize, أنماط retention rhythm،
بنية content-skills للـ writing/audit modes).
"""

from skills.anti_slop_ar_eg.skill import AntiSlopSkill
from skills.retention_ar_eg.skill import RetentionSkill
from skills.viral_hooks_ar_eg.skill import ViralHooksSkill
from skills.storytelling_ar_eg.skill import StorytellingSkill
from core.context import PipelineContext


def test_anti_slop_catches_binary_contrast_and_false_agency():
    ctx = PipelineContext(project_id="p1", project_name="t")
    ctx.draft_script = "مش كده، لكن كده. المشكلة بتحل نفسها في الآخر."
    skill = AntiSlopSkill()
    result = skill.run(ctx)
    types = {i["type"] for i in result.output["anti_slop_report"]["issues"]}
    assert "filler_phrase" in types


def test_anti_slop_scoring_below_35_flags_needs_revision():
    ctx = PipelineContext(project_id="p1", project_name="t")
    ctx.draft_script = (
        "في الحقيقة في عالم اليوم كل حاجة دايمًا بتتغير. في الحقيقة كل حاجة "
        "دايمًا بتتغير. محدش فاهم حاجة. في النهاية كل حاجة دايمًا بتتغير."
    )
    result = AntiSlopSkill().run(ctx)
    scores = result.output["anti_slop_report"]["scores"]
    assert scores["needs_revision"] is True
    assert scores["total_over_50"] < 35


def test_retention_rhythm_flags_long_gap_between_rehooks():
    skill = RetentionSkill()
    sections = [
        {"title": "مقدمة", "estimated_word_count": 100, "is_rehook_point": True},
        {"title": "قسم طويل بلا تجديد", "estimated_word_count": 900, "is_rehook_point": False},
    ]
    warnings = skill._check_rehook_rhythm(sections)
    assert len(warnings) == 1
    assert "قسم طويل بلا تجديد" in warnings[0]


def test_retention_rhythm_no_warning_when_rehooks_frequent_enough():
    skill = RetentionSkill()
    sections = [
        {"title": "مقدمة", "estimated_word_count": 100, "is_rehook_point": True},
        {"title": "قسم قصير", "estimated_word_count": 200, "is_rehook_point": True},
        {"title": "قسم تاني قصير", "estimated_word_count": 200, "is_rehook_point": True},
    ]
    assert skill._check_rehook_rhythm(sections) == []


def test_viral_hooks_deterministic_check_catches_generic_opener():
    skill = ViralHooksSkill()
    warnings = skill._quick_deterministic_check("في الفيديو ده هنتكلم عن حاجات كتير")
    assert len(warnings) >= 1


def test_viral_hooks_deterministic_check_clean_for_specific_hook():
    skill = ViralHooksSkill()
    warnings = skill._quick_deterministic_check("ليه فلوسك بتخلص قبل آخر الشهر بيومين؟")
    assert warnings == []


def test_storytelling_audit_flags_flat_arc_without_tension():
    skill = StorytellingSkill()
    flat_arc = {
        "situation": "الوضع كذا", "tension": "", "complication": "شوية",
        "insight": "حاجة", "payoff": "الوضع كذا",
    }
    warnings = skill.audit(flat_arc)
    assert len(warnings) >= 3  # tension فاضي + تطابق situation/payoff + قصر العناصر
