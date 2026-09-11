"""
pages/1_Project_Workspace.py
--------------------------------
الصفحة الرئيسية للعمل على مشروع واحد. كل مرحلة من WORKFLOW_STAGES ليها
زرار تشغيل مستقل، عشان المستخدم يقدر يراجع مخرج كل مرحلة قبل ما يكمل
للي بعدها، ويقدر يوقف ويرجع يكمل بعدين (المشروع محفوظ أول بأول).
"""

import streamlit as st

from config import APP_ICON, WEB_SEARCH_ENABLED, AUDIENCE_PRESETS
from engine.persistence import backend
from engine.models import Project, VoiceProfile
from engine import pipeline

st.set_page_config(page_title="Project Workspace", page_icon=APP_ICON, layout="wide")
st.title("🗂️ Project Workspace")

active_id = st.session_state.get("active_project_id")
projects_list = backend().list_projects()

if not projects_list:
    st.info("معندكش مشاريع لسه. ارجع للصفحة الرئيسية وأنشئ مشروع جديد.")
    st.stop()

id_to_title = {p["id"]: p["title"] for p in projects_list}
default_index = list(id_to_title.keys()).index(active_id) if active_id in id_to_title else 0
selected_id = st.selectbox(
    "اختر المشروع", options=list(id_to_title.keys()),
    format_func=lambda x: id_to_title[x], index=default_index,
)
st.session_state["active_project_id"] = selected_id

project: Project = backend().load_project(selected_id)
if project is None:
    st.error("المشروع مش موجود.")
    st.stop()

voice_profiles = backend().list_voice_profiles()
voice_map = {"بدون بصمة صوتية": None}
voice_map.update({vp.name: vp for vp in voice_profiles})
chosen_voice_name = st.sidebar.selectbox("🎙️ بصمة الكاتب المستخدمة", list(voice_map.keys()))
active_voice: VoiceProfile = voice_map[chosen_voice_name]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**المرحلة الحالية:** `{project.current_stage}`")
st.sidebar.markdown(f"**الحالة:** {project.status}")
web_search_allowed = st.sidebar.checkbox("السماح بالبحث الخارجي على الويب", value=WEB_SEARCH_ENABLED)
simplify_for_beginners = project.audience == "مبتدئين تمامًا في الموضوع"

st.subheader(f"📌 {project.title}")
with st.expander("المدخل الخام / الجمهور / المدة", expanded=False):
    st.write(f"**المدخل:** {project.original_request}")
    st.write(f"**الجمهور:** {project.audience}")
    st.write(f"**المدة:** {project.duration_minutes} دقيقة")

st.divider()


def stage_block(number, key, label, output_attr, run_fn, help_text=""):
    """يبني كتلة UI موحدة لكل مرحلة: زرار تشغيل + عرض المخرج الحالي."""
    with st.container(border=True):
        st.markdown(f"### {number}. {label}")
        if help_text:
            st.caption(help_text)
        current_output = getattr(project, output_attr, None)
        col_run, col_status = st.columns([1, 3])
        run_clicked = col_run.button(f"تشغيل / إعادة تشغيل", key=f"run_{key}")
        if run_clicked:
            with st.spinner(f"جاري تنفيذ: {label} ..."):
                try:
                    run_fn()
                    st.rerun()
                except Exception as e:  # noqa: BLE001
                    st.error(f"حصل خطأ أثناء تنفيذ المرحلة: {e}")
        if current_output:
            col_status.success("تم تنفيذ هذه المرحلة ✅")
        else:
            col_status.info("لسه متنفذتش")
        if current_output:
            with st.expander("عرض المخرج", expanded=False):
                if isinstance(current_output, (dict, list)):
                    st.json(current_output)
                else:
                    st.markdown(current_output)


# --- المستوى الأول: فهم المدخل ---
stage_block(
    1, "input_understanding", "فهم المدخل الخام", "topic_understanding",
    lambda: pipeline.run_input_understanding(project),
)

# --- المصادر (نص مجمّع من صفحة Sources) ---
sources_text = st.session_state.get(f"sources_text_{project.id}", "")
if not sources_text:
    st.caption("💡 لسه مضفتش مصادر لهذا المشروع. اذهب لصفحة **Sources** لإضافة نصوص/PDF/روابط (اختياري).")

stage_block(
    2, "research", "البحث", "research_notes",
    lambda: pipeline.run_research(project, sources_text, web_search_allowed),
    help_text="يعتمد على المصادر المضافة في صفحة Sources، وعلى البحث الخارجي لو مفعّل.",
)

stage_block(
    3, "knowledge", "بناء قاعدة المعرفة", "knowledge_base",
    lambda: pipeline.run_knowledge(project),
)

stage_block(
    4, "audience", "لماذا يهتم المشاهد", "audience_insight",
    lambda: pipeline.run_audience(project),
)

stage_block(
    5, "strategy", "الاستراتيجية (+ تخطيط الاحتفاظ بالمشاهد)", "strategy",
    lambda: pipeline.run_strategy(project),
)

stage_block(
    6, "story_architecture", "بناء الحكاية", "story_architecture",
    lambda: pipeline.run_story(project),
)

stage_block(
    7, "hook", "الهوك", "hook_options",
    lambda: pipeline.run_hook(project, active_voice),
)

if project.hook_options:
    st.markdown("**اختر الهوك اللي عايز تبدأ بيه (أو سيب الأول كافتراضي):**")
    project.chosen_hook = st.radio(
        "خيارات الهوك", project.hook_options,
        index=project.hook_options.index(project.chosen_hook) if project.chosen_hook in project.hook_options else 0,
        label_visibility="collapsed",
    )
    if st.button("حفظ الهوك المختار"):
        backend().save_project(project)
        st.success("تم حفظ الهوك المختار.")

stage_block(
    8, "script_writing", "كتابة المسودة", "draft_script",
    lambda: pipeline.run_script_writing(project, active_voice),
)

stage_block(
    9, "humanization", "الإنسانية (Humanize)", "humanized_script",
    lambda: pipeline.run_humanization(project, active_voice),
)

stage_block(
    10, "anti_slop_review", "مراجعة الـ AI Slop", "anti_slop_report",
    lambda: pipeline.run_anti_slop_review(project),
)

stage_block(
    11, "retention_review", "مراجعة الاحتفاظ بالمشاهد", "retention_report",
    lambda: pipeline.run_retention_review(project),
)

stage_block(
    12, "repetition_review", "مراجعة التكرار", "repetition_report",
    lambda: pipeline.run_repetition_review(project),
)

stage_block(
    13, "egyptian_arabic_editing", "التحرير النهائي (تطبيق كل المراجعات)", "egyptian_edited_script",
    lambda: pipeline.run_egyptian_arabic_editing(project, simplify_for_beginners),
)

stage_block(
    14, "voice_dna_consistency_check", "فحص اتساق البصمة الصوتية", "voice_consistency_report",
    lambda: pipeline.run_voice_dna_consistency_check(project, active_voice),
)

stage_block(
    15, "final_human_review", "المراجعة النهائية كمشاهد", "final_review_notes",
    lambda: pipeline.run_final_human_review(project),
)

st.divider()
st.markdown("### 🎬 السكريبت النهائي")
if st.button("إخراج السكريبت النهائي", type="primary"):
    with st.spinner("جاري تجميع النسخة النهائية..."):
        pipeline.run_final_script(project)
        st.rerun()

if project.final_script:
    st.success("السكريبت جاهز ✅")
    st.text_area("النص النهائي", project.final_script, height=500)
    st.download_button(
        "⬇️ تحميل السكريبت (txt)", project.final_script,
        file_name=f"{project.title}_final_script.txt",
    )
