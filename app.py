"""
app.py
------
نقطة الدخول الرئيسية. صفحة Dashboard: عرض المشاريع المحفوظة + إنشاء
مشروع جديد. باقي الصفحات في مجلد pages/ (Streamlit multipage تلقائيًا).
"""

import streamlit as st

from config import (
    APP_TITLE, APP_TAGLINE, APP_ICON,
    MIN_DURATION_MINUTES, MAX_DURATION_MINUTES, DEFAULT_DURATION_MINUTES,
    AUDIENCE_PRESETS, GEMINI_API_KEY,
)
from engine.models import Project
from engine.persistence import backend

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title(f"{APP_ICON} {APP_TITLE}")
st.caption(APP_TAGLINE)

if not GEMINI_API_KEY:
    st.warning(
        "⚠️ متغير GEMINI_API_KEY مش متظبط. النظام مش هيقدر يشغّل أي محرك "
        "لحد ما تضيفه في Environment Variables محليًا، أو في Secrets على "
        "Streamlit Community Cloud (Settings → Secrets).",
        icon="⚠️",
    )

st.divider()

col_new, col_list = st.columns([1, 2], gap="large")

with col_new:
    st.subheader("➕ مشروع جديد")
    with st.form("new_project_form", clear_on_submit=True):
        title = st.text_input("اسم المشروع (اختياري)")
        original_request = st.text_area(
            "المدخل الخام", height=160,
            placeholder="اكتب عنوان، فكرة، سؤال، أو ألصق نص... التفاصيل الكاملة ممكن تضيفها في المصادر بعد إنشاء المشروع.",
        )
        audience_choice = st.selectbox("الجمهور المستهدف", AUDIENCE_PRESETS)
        custom_audience = ""
        if audience_choice == "مخصص (اكتب وصف الجمهور بنفسك)":
            custom_audience = st.text_input("اوصف الجمهور بنفسك")
        duration = st.slider(
            "مدة الفيديو (دقائق)", MIN_DURATION_MINUTES, MAX_DURATION_MINUTES,
            DEFAULT_DURATION_MINUTES,
        )
        submitted = st.form_submit_button("إنشاء المشروع", type="primary", use_container_width=True)

        if submitted:
            if not original_request.strip():
                st.error("لازم تكتب المدخل الخام الأول.")
            else:
                audience_final = custom_audience.strip() or audience_choice
                project = Project(
                    title=title.strip() or (original_request.strip()[:40] + "..."),
                    original_request=original_request.strip(),
                    audience=audience_final,
                    duration_minutes=duration,
                )
                backend().save_project(project)
                st.session_state["active_project_id"] = project.id
                st.success(f"تم إنشاء المشروع: {project.title}")
                st.info("روح لصفحة **Project Workspace** من القائمة الجانبية عشان تبدأ التنفيذ.")

with col_list:
    st.subheader("📁 مشاريعك المحفوظة")
    projects = backend().list_projects()
    if not projects:
        st.info("لسه معندكش أي مشروع. ابدأ من الفورم على اليسار.")
    else:
        for p in projects:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.markdown(f"**{p['title']}**  \n`{p['id']}` — الحالة: {p['status']}")
                if c2.button("فتح", key=f"open_{p['id']}", use_container_width=True):
                    st.session_state["active_project_id"] = p["id"]
                    st.switch_page("pages/1_Project_Workspace.py")
                if c3.button("حذف", key=f"del_{p['id']}", use_container_width=True):
                    backend().delete_project(p["id"])
                    st.rerun()

st.divider()
st.caption(
    "Minds10 — نظام ذكاء اصطناعي لإنتاج محتوى يوتيوب: يفهم → يبحث → يبني "
    "المعرفة → يخطط → يبني الحكاية → يكتب → يجعل النص إنسانيًا → يراجع → "
    "يحرر → يخرج سكريبت نهائي جاهز للتسجيل بالعامية المصرية."
)
