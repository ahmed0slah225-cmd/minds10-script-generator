"""
pages/5_🕘_History.py
========================
عرض كل النسخ (Snapshots) المحفوظة للمشروع النشط من project_versions —
التطبيق الفعلي لمبدأ "المشروع قابل للاستكمال والرجوع لأي نقطة قديمة".
"""

from __future__ import annotations

import streamlit as st

from config import APP_TITLE, STAGE_LABELS_AR
from engine.models import ProjectContext
from persistence.db import get_db
from utils.ui_common import ensure_session_defaults, load_active_context

st.set_page_config(page_title=f"{APP_TITLE} · History", layout="wide")
ensure_session_defaults()
st.title("🕘 History")

ctx = load_active_context()
if ctx is None:
    st.info("مفيش مشروع مفتوح. افتح مشروع من صفحة Projects الأول.")
    st.stop()

db = get_db()
rows = db.execute(
    "SELECT id, stage, created_at FROM project_versions WHERE project_id = ? ORDER BY created_at DESC",
    (ctx.project_id,),
)

st.subheader(f"تاريخ مشروع: {ctx.title}")
st.caption(f"{len(rows)} نسخة محفوظة")

for row in rows:
    label = STAGE_LABELS_AR.get(row["stage"], row["stage"])
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        c1.write(f"**{label}** — {row['created_at']}")
        if c2.button("عرض هذه النسخة", key=f"view_{row['id']}"):
            snapshot_rows = db.execute(
                "SELECT context_json FROM project_versions WHERE id = ?", (row["id"],)
            )
            old_ctx = ProjectContext.from_json(snapshot_rows[0]["context_json"])
            st.session_state[f"snapshot_view_{row['id']}"] = old_ctx.to_json()

    view_key = f"snapshot_view_{row['id']}"
    if view_key in st.session_state:
        with st.expander("محتوى هذه النسخة", expanded=True):
            st.json(st.session_state[view_key])
