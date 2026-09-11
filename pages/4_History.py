"""
pages/4_History.py
----------------------
عرض سجل مراحل كل مشروع (متى اتنفذت كل مرحلة)، لسهولة تتبع من فين ممكن
تكمل، أو لمراجعة تاريخ التعديلات.
"""

import datetime
import streamlit as st

from config import APP_ICON
from engine.persistence import backend

st.set_page_config(page_title="History", page_icon=APP_ICON, layout="wide")
st.title("🕒 History — سجل المشاريع")

projects = backend().list_projects()
if not projects:
    st.info("معندكش مشاريع لسه.")
    st.stop()

id_to_title = {p["id"]: p["title"] for p in projects}
selected_id = st.selectbox("اختر مشروع", options=list(id_to_title.keys()), format_func=lambda x: id_to_title[x])

project = backend().load_project(selected_id)
if project is None:
    st.error("المشروع مش موجود.")
    st.stop()

st.subheader(f"سجل مراحل: {project.title}")
if not project.stage_log:
    st.info("لسه معندهاش أي مراحل منفذة.")
else:
    for entry in reversed(project.stage_log):
        ts = datetime.datetime.fromtimestamp(entry["ts"]).strftime("%Y-%m-%d %H:%M")
        st.markdown(f"- `{ts}` — **{entry['stage']}** — {entry.get('summary', '')}")

st.divider()
if st.button("فتح هذا المشروع في Project Workspace", type="primary"):
    st.session_state["active_project_id"] = project.id
    st.switch_page("pages/1_Project_Workspace.py")
