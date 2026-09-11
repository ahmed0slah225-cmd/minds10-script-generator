"""
engine/pipeline.py
----------------------
المايسترو. الترتيب هنا لازم يفضل مطابق تمامًا لـ config.WORKFLOW_STAGES.
كل دالة `run_<stage>` بتاخد الـ Project وترجعه بعد ما تحدّث الحقول
الخاصة بيها، وتنادي `project.log_stage(...)` وتحفظ فورًا — عشان لو
المستخدم قفل الجلسة في نص الطريق، يقدر يرجع يكمل من نفس المرحلة
بالظبط (المشروع قابل للاستكمال، مش بيبدأ من الصفر).

ملاحظة عن التكلفة والتكرار (طبقًا لمتطلبات المستخدم):
- كل مرحلة مراجعة (anti_slop / retention / repetition / voice_consistency)
  بتتنفذ *مرة واحدة* لكل تشغيل، مش في لوب. لو المستخدم عايز إعادة
  المراجعة يدويًا بعد تعديل، يستدعي الدالة تاني بنفسه من الواجهة.
- الـ Editor يطبّق كل نتائج المراجعات في *نداء واحد*، مش نداء منفصل لكل
  تقرير، عشان نتجنب إعادة كتابة السكريبت عدة مرات بلا فائدة.
"""

from __future__ import annotations
from typing import Optional

from engine.models import Project, VoiceProfile
from engine.persistence import backend
from engine.engines import (
    input_understanding,
    research,
    knowledge,
    audience,
    strategy,
    story,
    hook,
    script_writer,
    review,
    editor,
)


def _save(project: Project):
    backend().save_project(project)


def _knowledge_summary(project: Project) -> str:
    if not project.knowledge_base:
        return "لا توجد عناصر معرفة موثقة حتى الآن."
    lines = []
    for item in project.knowledge_base:
        conf = item.get("confidence", "")
        lines.append(f"- [{conf}] {item.get('claim', '')} — {item.get('evidence', '')}")
    return "\n".join(lines)


def run_input_understanding(project: Project) -> Project:
    project.topic_understanding = input_understanding.understand_input(
        project.original_request, project.audience, project.duration_minutes
    )
    project.log_stage("input_understanding", "تم تحليل المدخل الخام")
    _save(project)
    return project


def run_research(project: Project, sources_text: str, web_search_allowed: bool) -> Project:
    project.research_notes = research.run_research(
        project.topic_understanding, sources_text, web_search_allowed
    )
    project.log_stage("research", "تم استخراج المعلومات المفيدة للفكرة")
    _save(project)
    return project


def run_knowledge(project: Project) -> Project:
    project.knowledge_base = knowledge.build_knowledge_base(project.research_notes)
    project.log_stage("knowledge", f"تم بناء قاعدة معرفة من {len(project.knowledge_base)} عنصر")
    _save(project)
    return project


def run_audience(project: Project) -> Project:
    project.audience_insight = audience.analyze_audience(
        project.topic_understanding, project.audience, project.duration_minutes,
        _knowledge_summary(project),
    )
    project.log_stage("audience", "تم تحديد سبب اهتمام المشاهد")
    _save(project)
    return project


def run_strategy(project: Project) -> Project:
    project.strategy = strategy.build_strategy(
        project.topic_understanding, project.audience_insight,
        _knowledge_summary(project), project.duration_minutes,
    )
    project.log_stage("strategy", "تم بناء الاستراتيجية وخطة الاحتفاظ بالمشاهد")
    _save(project)
    return project


def run_story(project: Project) -> Project:
    project.story_architecture = story.build_story_architecture(
        project.topic_understanding, project.audience_insight,
        project.strategy, _knowledge_summary(project),
    )
    project.log_stage("story_architecture", "تم بناء الهيكل الحكائي")
    _save(project)
    return project


def run_hook(project: Project, voice_profile: Optional[VoiceProfile] = None) -> Project:
    hooks = hook.generate_hooks(project.story_architecture, project.audience_insight, voice_profile)
    project.hook_options = [h.get("text", "") for h in hooks if h.get("text")]
    if project.hook_options and not project.chosen_hook:
        project.chosen_hook = project.hook_options[0]
    project.log_stage("hook", f"تم توليد {len(project.hook_options)} مقترح هوك")
    _save(project)
    return project


def run_script_writing(project: Project, voice_profile: Optional[VoiceProfile] = None) -> Project:
    project.draft_script = script_writer.write_draft(
        project.chosen_hook, project.story_architecture, project.strategy,
        _knowledge_summary(project), project.duration_minutes, project.audience,
        voice_profile,
    )
    project.log_stage("script_writing", "تم كتابة المسودة الأولى")
    _save(project)
    return project


def run_humanization(project: Project, voice_profile: Optional[VoiceProfile] = None) -> Project:
    project.humanized_script = script_writer.humanize_draft(project.draft_script, voice_profile)
    project.log_stage("humanization", "تم تطبيق مهارة الإنسانية")
    _save(project)
    return project


def run_anti_slop_review(project: Project) -> Project:
    text = project.humanized_script or project.draft_script
    project.anti_slop_report = review.anti_slop_review(text)
    project.log_stage("anti_slop_review", "تم رصد علامات كلام الـ AI الفاضي")
    _save(project)
    return project


def run_retention_review(project: Project) -> Project:
    text = project.humanized_script or project.draft_script
    project.retention_report = review.retention_review(text)
    project.log_stage("retention_review", "تم فحص الاحتفاظ بالمشاهد")
    _save(project)
    return project


def run_repetition_review(project: Project) -> Project:
    text = project.humanized_script or project.draft_script
    project.repetition_report = review.repetition_review(text)
    project.log_stage("repetition_review", "تم فحص التكرار")
    _save(project)
    return project


def run_egyptian_arabic_editing(project: Project, simplify_for_beginners: bool = False) -> Project:
    text = project.humanized_script or project.draft_script
    project.egyptian_edited_script = editor.apply_editorial_pass(
        text, project.anti_slop_report, project.retention_report,
        project.repetition_report, project.voice_consistency_report,
        simplify_for_beginners,
    )
    project.log_stage("egyptian_arabic_editing", "تم تطبيق التحرير النهائي بناءً على التقارير")
    _save(project)
    return project


def run_voice_dna_consistency_check(project: Project, voice_profile: Optional[VoiceProfile] = None) -> Project:
    text = project.egyptian_edited_script or project.humanized_script or project.draft_script
    project.voice_consistency_report = review.voice_dna_consistency_check(text, voice_profile)
    project.log_stage("voice_dna_consistency_check", "تم فحص اتساق البصمة الصوتية")
    _save(project)
    return project


def run_final_human_review(project: Project) -> Project:
    text = project.egyptian_edited_script or project.humanized_script or project.draft_script
    result = review.final_human_review(text, project.chosen_hook)
    project.final_review_notes = [result]
    project.log_stage("final_human_review", "تمت المراجعة النهائية كمشاهد")
    _save(project)
    return project


def run_final_script(project: Project) -> Project:
    project.final_script = project.egyptian_edited_script or project.humanized_script or project.draft_script
    project.status = "completed"
    project.log_stage("final_script", "السكريبت النهائي جاهز")
    _save(project)
    return project


# ترتيب التنفيذ الكامل (مرجع فقط — الواجهة بتنادي كل مرحلة بمدخلاتها
# الخاصة لأن بعضها محتاج مدخلات إضافية زي sources_text أو voice_profile)
FULL_ORDER = [
    "input_understanding", "research", "knowledge", "audience", "strategy",
    "story_architecture", "hook", "script_writing", "humanization",
    "anti_slop_review", "retention_review", "repetition_review",
    "egyptian_arabic_editing", "voice_dna_consistency_check",
    "final_human_review", "final_script",
]
