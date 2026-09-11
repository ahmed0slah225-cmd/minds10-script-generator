"""
pages/2_Sources.py
----------------------
إضافة مصادر للمشروع النشط: نص حر، رابط، أو PDF مع نطاق صفحات محدد.
كل المصادر بتتجمع في نص واحد (`sources_text_<project_id>`) يُستخدم في
مرحلة البحث (Research) داخل Project Workspace.
"""

import os
import streamlit as st

from config import APP_ICON, MAX_SOURCES_PER_PROJECT
from engine.persistence import backend
from engine.models import SourceDoc
from engine.engines import pdf_engine

st.set_page_config(page_title="Sources", page_icon=APP_ICON, layout="wide")
st.title("📚 Sources — مصادر المشروع")

active_id = st.session_state.get("active_project_id")
projects_list = backend().list_projects()
if not projects_list:
    st.info("معندكش مشاريع لسه.")
    st.stop()

id_to_title = {p["id"]: p["title"] for p in projects_list}
default_index = list(id_to_title.keys()).index(active_id) if active_id in id_to_title else 0
selected_id = st.selectbox("المشروع", options=list(id_to_title.keys()),
                            format_func=lambda x: id_to_title[x], index=default_index)
st.session_state["active_project_id"] = selected_id

existing_sources = backend().list_sources(selected_id)

tab_text, tab_url, tab_pdf = st.tabs(["📝 نص حر", "🔗 رابط", "📄 PDF"])

with tab_text:
    with st.form("add_text_source", clear_on_submit=True):
        title = st.text_input("عنوان المصدر")
        raw_text = st.text_area("النص", height=200)
        if st.form_submit_button("إضافة"):
            if len(existing_sources) >= MAX_SOURCES_PER_PROJECT:
                st.error(f"وصلت للحد الأقصى ({MAX_SOURCES_PER_PROJECT} مصدر لكل مشروع).")
            elif raw_text.strip():
                src = SourceDoc(project_id=selected_id, kind="text", title=title or "نص بدون عنوان",
                                 raw_text=raw_text.strip(), extracted_text=raw_text.strip())
                backend().save_source(src)
                st.success("تمت إضافة المصدر.")
                st.rerun()

with tab_url:
    with st.form("add_url_source", clear_on_submit=True):
        title = st.text_input("عنوان مختصر للرابط")
        url = st.text_input("الرابط (URL)")
        note = st.text_area(
            "ملخص/محتوى الرابط (الصقه هنا يدويًا)", height=150,
            help="النظام هنا لا يزحف تلقائيًا على الروابط؛ الصق المحتوى المهم منه هنا عشان يُستخدم كمصدر موثوق.",
        )
        if st.form_submit_button("إضافة"):
            if url.strip():
                src = SourceDoc(project_id=selected_id, kind="url", title=title or url,
                                 url=url.strip(), extracted_text=note.strip())
                backend().save_source(src)
                st.success("تمت إضافة المصدر.")
                st.rerun()

with tab_pdf:
    uploaded = st.file_uploader("ارفع PDF نصي", type=["pdf"])
    if uploaded is not None:
        tmp_path = os.path.join("/tmp", uploaded.name)
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        try:
            info = pdf_engine.inspect_pdf(tmp_path)
            st.info(f"عدد الصفحات: {info['total_pages']} | نص قابل للاستخراج: {'نعم' if info['has_extractable_text'] else 'لا — قد يكون PDF ممسوح ضوئيًا'}")
            c1, c2 = st.columns(2)
            start_page = c1.number_input("من صفحة", min_value=1, max_value=info["total_pages"], value=1)
            end_page = c2.number_input("إلى صفحة", min_value=1, max_value=info["total_pages"], value=min(20, info["total_pages"]))
            if st.button("استخراج النطاق وإضافته كمصدر"):
                extracted_text, pages_with_text = pdf_engine.extract_page_range(tmp_path, int(start_page), int(end_page))
                src = SourceDoc(
                    project_id=selected_id, kind="pdf", title=f"{uploaded.name} (ص {start_page}-{end_page})",
                    file_path=tmp_path, page_start=int(start_page), page_end=int(end_page),
                    extracted_text=extracted_text,
                )
                backend().save_source(src)
                st.success(f"تم استخراج {len(pages_with_text)} صفحة فيها نص وإضافتها كمصدر.")
                st.rerun()
        except Exception as e:  # noqa: BLE001
            st.error(f"مش قادر أقرأ الملف: {e}")

st.divider()
st.subheader("المصادر الحالية")
if not existing_sources:
    st.info("لسه معندكش مصادر لهذا المشروع.")
else:
    combined = []
    for s in existing_sources:
        with st.container(border=True):
            st.markdown(f"**{s['title']}** — نوع: {s['kind']}")
            preview = (s.get("extracted_text") or "")[:400]
            st.caption(preview + ("..." if len(s.get("extracted_text") or "") > 400 else ""))
            if st.button("حذف", key=f"del_src_{s['id']}"):
                backend().delete_source(s["id"])
                st.rerun()
        if s.get("extracted_text"):
            combined.append(f"### مصدر: {s['title']}\n{s['extracted_text']}")

    st.session_state[f"sources_text_{selected_id}"] = "\n\n".join(combined)
    st.success("كل المصادر دي هتتحقن تلقائيًا في مرحلة البحث بصفحة Project Workspace.")
