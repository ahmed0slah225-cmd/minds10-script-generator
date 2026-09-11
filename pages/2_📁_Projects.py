"""
pages/2_📁_Projects.py
=========================
إنشاء مشروع جديد، اختيار مشروع موجود، وتشغيل الـWorkflow مرحلة بمرحلة
(أو دفعة واحدة). دي الصفحة اللي بتترجم "المشروع قابل للاستكمال" لواقع
فعلي: كل مرحلة بتتحفظ فور ما تخلص.
"""

from __future__ import annotations

import streamlit as st

from config import (
    APP_TITLE, MIN_DURATION_MINUTES, MAX_DURATION_MINUTES, DEFAULT_DURATION_MINUTES,
    DURATION_PRESETS, WORKFLOW_STAGES, STAGE_LABELS_AR,
)
from engine.models import ProjectContext
from persistence.db import get_db
from utils.ui_common import ensure_session_defaults, get_pipeline, load_active_context, stage_progress_bar

st.set_page_config(page_title=f"{APP_TITLE} · Projects", layout="wide")
ensure_session_defaults()

st.title("📁 Projects")

db = get_db()

# ---------------------------------------------------------------------------
# اختيار/إنشاء مشروع
# ---------------------------------------------------------------------------
with st.expander("➕ مشروع جديد", expanded=st.session_state["active_project_id"] is None):
    with st.form("new_project_form"):
        title = st.text_input("عنوان المشروع / الفكرة الأولية", placeholder="قرارك اليوم ممكن يغير مستقبلك المالي")
        audience = st.text_input("الجمهور المستهدف (اختياري)", placeholder="شاب في العشرينات بيشتغل")
        duration = st.select_slider(
            "مدة الفيديو (بالدقائق)", options=DURATION_PRESETS, value=DEFAULT_DURATION_MINUTES
        )
        raw_input = st.text_area(
            "المادة الخام: عنوان / فكرة / سؤال / نص",
            placeholder="عايز فيديو يشرح إزاي القرارات اليومية بتأثر على المسار المالي...",
            height=120,
        )
        submitted = st.form_submit_button("ابدأ المشروع", type="primary")
        if submitted:
            if not title.strip():
                st.error("لازم تكتب عنوان أو فكرة للمشروع الأول.")
            else:
                from engine.input_router import classify_source

                ctx = ProjectContext(
                    title=title.strip(),
                    audience=audience.strip(),
                    duration_minutes=duration,
                    writer_id=st.session_state["writer_id"],
                )
                if raw_input.strip():
                    ctx.sources.append(classify_source(raw_text=raw_input.strip()))
                db.save_project_snapshot(ctx)
                st.session_state["active_project_id"] = ctx.project_id
                st.success("اتعمل المشروع! انزل تحت عشان تشغّل المراحل.")
                st.rerun()

st.divider()

projects = db.list_projects(user_id=st.session_state["writer_id"])
if projects:
    options = {f"{p['title']} — {p['current_stage']}": p["id"] for p in projects}
    labels = list(options.keys())
    current_id = st.session_state.get("active_project_id")
    default_idx = next((i for i, pid in enumerate(options.values()) if pid == current_id), 0)
    chosen = st.selectbox("اختار مشروع", labels, index=default_idx)
    st.session_state["active_project_id"] = options[chosen]

ctx = load_active_context()
if ctx is None:
    st.stop()

st.divider()
st.subheader(f"🎬 {ctx.title}")
stage_progress_bar(ctx)

# ---------------------------------------------------------------------------
# تشغيل الـWorkflow
# ---------------------------------------------------------------------------
pipeline = get_pipeline()

col_run_one, col_run_all = st.columns(2)
with col_run_one:
    if st.button("▶️ شغّل المرحلة الجاية بس", use_container_width=True):
        try:
            with st.spinner(f"شغال على: {STAGE_LABELS_AR.get(ctx.current_stage, ctx.current_stage)}"):
                ctx = pipeline.run_stage(ctx, ctx.current_stage)
            st.success("خلصت المرحلة واتحفظت.")
            st.rerun()
        except Exception as e:
            st.error(f"حصل خطأ في المرحلة دي: {e}")

with col_run_all:
    if st.button("⏩ شغّل كل المراحل الباقية", type="primary", use_container_width=True):
        try:
            with st.spinner("شغال على كل مراحل الـWorkflow..."):
                ctx = pipeline.run_full_pipeline(ctx, start_from=ctx.current_stage)
            st.success("خلص المشروع بالكامل!")
            st.rerun()
        except Exception as e:
            st.error(f"حصل خطأ أثناء التشغيل: {e}")

st.divider()

# ---------------------------------------------------------------------------
# عرض الحالة الحالية للمشروع
# ---------------------------------------------------------------------------
tabs = st.tabs(["الملخص", "الهوك والاستراتيجية", "السكريبت", "المراجعات", "JSON خام"])

with tabs[0]:
    st.write(f"**الجمهور:** {ctx.audience or 'غير محدد'}")
    st.write(f"**المدة:** {ctx.duration_minutes} دقيقة")
    if ctx.topic_understanding:
        st.write(f"**الموضوع الظاهري:** {ctx.topic_understanding.get('surface_topic', '')}")
    if ctx.audience_pain_point:
        st.write(f"**ألم المشاهد:** {ctx.audience_pain_point}")

with tabs[1]:
    if ctx.strategy:
        st.write(f"**الزاوية:** {ctx.strategy.get('angle', '')}")
        st.write(f"**الوعد:** {ctx.strategy.get('promise_to_viewer', '')}")
    if ctx.hook_text:
        st.info(ctx.hook_text)
    if ctx.outline:
        st.write("**الهيكل:**")
        for item in ctx.outline:
            st.write(f"- {item}")

with tabs[2]:
    if ctx.final_script:
        st.text_area("السكريبت النهائي", ctx.final_script, height=400)
        st.download_button("⬇️ تحميل السكريبت (.txt)", ctx.final_script, file_name=f"{ctx.title}.txt")
    elif ctx.egyptian_final_script:
        st.text_area("السكريبت (بعد التحرير المصري، لسه مش نهائي)", ctx.egyptian_final_script, height=400)
    elif ctx.humanized_script:
        st.text_area("السكريبت (بعد الأنسنة)", ctx.humanized_script, height=400)
    elif ctx.draft_script:
        st.text_area("مسودة السكريبت", ctx.draft_script, height=400)
    else:
        st.caption("لسه مفيش سكريبت اتكتب.")

with tabs[3]:
    if ctx.reviews.get("anti_slop"):
        st.write("**Anti-Slop:**", ctx.reviews["anti_slop"].get("score"), "/ 50")
    if ctx.reviews.get("retention"):
        st.write("**Retention Score:**", ctx.reviews["retention"].get("retention_score"))
    if ctx.voice_dna_consistency:
        st.write("**Voice DNA Consistency:**", ctx.voice_dna_consistency.get("consistency_score"))
    if ctx.reviews.get("final_human"):
        st.write("**رأي المشاهد النهائي:**", ctx.reviews["final_human"].get("overall_verdict"))

with tabs[4]:
    st.json(ctx.to_json())
