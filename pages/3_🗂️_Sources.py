"""
pages/3_🗂️_Sources.py
========================
إضافة مصادر للمشروع النشط: نص مباشر، رابط، أو PDF مع تحديد نطاق صفحات
(مش الكتاب كله كنص متصل — راجع utils/pdf_utils.py).
"""

from __future__ import annotations

import tempfile

import streamlit as st

from config import APP_TITLE, MAX_PDF_SIZE_MB
from engine.input_router import classify_source
from engine.models import SourceItem, new_id
from persistence.db import get_db
from utils.pdf_utils import load_pdf
from utils.ui_common import ensure_session_defaults, load_active_context

st.set_page_config(page_title=f"{APP_TITLE} · Sources", layout="wide")
ensure_session_defaults()
st.title("🗂️ Sources")

ctx = load_active_context()
if ctx is None:
    st.info("مفيش مشروع مفتوح. افتح مشروع من صفحة Projects الأول.")
    st.stop()

db = get_db()
st.subheader(f"مصادر مشروع: {ctx.title}")

tab_text, tab_url, tab_pdf = st.tabs(["نص", "رابط", "PDF"])

with tab_text:
    with st.form("add_text_source"):
        text = st.text_area("نص/ملاحظات/مسودة", height=150)
        if st.form_submit_button("أضف كمصدر") and text.strip():
            ctx.sources.append(classify_source(raw_text=text.strip()))
            db.save_project_snapshot(ctx)
            st.success("اتضاف المصدر.")
            st.rerun()

with tab_url:
    with st.form("add_url_source"):
        url = st.text_input("رابط (مقال / دراسة / صفحة)")
        if st.form_submit_button("أضف كمصدر") and url.strip():
            ctx.sources.append(classify_source(url=url.strip()))
            db.save_project_snapshot(ctx)
            st.success("اتضاف الرابط.")
            st.rerun()

with tab_pdf:
    uploaded = st.file_uploader(f"ارفع PDF نصي (حد أقصى {MAX_PDF_SIZE_MB}MB)", type=["pdf"])
    if uploaded is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        try:
            doc = load_pdf(tmp_path)
            st.success(f"الكتاب فيه {doc.total_pages} صفحة.")
            c1, c2 = st.columns(2)
            start_page = c1.number_input("من صفحة", min_value=1, max_value=doc.total_pages, value=1)
            end_page = c2.number_input("لصفحة", min_value=1, max_value=doc.total_pages, value=min(20, doc.total_pages))
            if st.button("أضف النطاق ده كمصدر"):
                try:
                    range_text = doc.range_text(int(start_page), int(end_page))
                    ctx.sources.append(
                        SourceItem(
                            id=new_id("src"), kind="pdf", title=uploaded.name,
                            file_path=tmp_path, raw_text=range_text,
                            page_start=int(start_page), page_end=int(end_page),
                        )
                    )
                    db.save_project_snapshot(ctx)
                    st.success(f"اتضاف نطاق الصفحات {start_page}-{end_page}.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
        except ValueError as e:
            st.error(str(e))

st.divider()
st.subheader("المصادر الحالية")
if not ctx.sources:
    st.caption("لسه مفيش مصادر مضافة.")
for s in ctx.sources:
    with st.container(border=True):
        st.write(f"**{s.kind}** — {s.title or s.url or (s.raw_text[:60] + '...' if s.raw_text else '')}")
        if s.page_start:
            st.caption(f"صفحات {s.page_start}–{s.page_end}")
