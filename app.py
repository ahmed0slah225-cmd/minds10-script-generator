"""
app.py
========
نقطة الدخول الرئيسية لتطبيق Streamlit. الصفحة دي هي الـDashboard —
عرض عام للمشاريع + بدء مشروع جديد. باقي الصفحات موجودة في مجلد pages/
وبتظهر تلقائيًا في القائمة الجانبية (نظام Streamlit Multi-page القياسي).
"""

from __future__ import annotations

import streamlit as st

from config import APP_TITLE, APP_TAGLINE, APP_ICON
from persistence.db import get_db

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")


def _ensure_session_defaults() -> None:
    """
    القاعدة هنا: أي حالة UI مؤقتة (زي التاب المفتوح) تروح في
    st.session_state، وأي حالة مشروع فعلية (السكريبت، المعرفة، المراجعات)
    تتحفظ في قاعدة البيانات عن طريق ProjectContext — مش العكس.
    """
    st.session_state.setdefault("active_project_id", None)
    st.session_state.setdefault("writer_id", "default")


def main() -> None:
    _ensure_session_defaults()
    db = get_db()

    st.title(f"{APP_ICON} {APP_TITLE}")
    st.caption(APP_TAGLINE)

    st.divider()

    col_new, col_list = st.columns([1, 2])

    with col_new:
        st.subheader("مشروع جديد")
        st.write("ابدأ مشروع سكريبت جديد من صفحة **Projects** في القائمة الجانبية.")
        if st.button("➕ إنشاء مشروع جديد", type="primary", use_container_width=True):
            st.switch_page("pages/2_📁_Projects.py")

    with col_list:
        st.subheader("مشاريعك الأخيرة")
        projects = db.list_projects(user_id=st.session_state["writer_id"])
        if not projects:
            st.info("لسه مفيش مشاريع. ابدأ واحد جديد من الزرار على الشمال.")
        else:
            for p in projects:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    c1.markdown(f"**{p['title']}**")
                    c2.caption(f"المرحلة الحالية: {p['current_stage']}")
                    if c3.button("افتح", key=f"open_{p['id']}"):
                        st.session_state["active_project_id"] = p["id"]
                        st.switch_page("pages/2_📁_Projects.py")


if __name__ == "__main__":
    main()
