"""
pages/4_🎙️_Voice_DNA.py
===========================
إضافة عيّنات كتابة سابقة للكاتب، واستخراج/عرض بصمته الصوتية. البصمة
دي بتتحفظ لكل writer_id مرة واحدة، وتتستخدم تلقائيًا في كل مشاريعه
الجاية (راجع engine/voice_engine.py).
"""

from __future__ import annotations

import streamlit as st

from config import APP_TITLE
from engine.gemini_client import GeminiClient
from engine.voice_engine import VoiceEngine
from persistence.db import get_db
from utils.ui_common import ensure_session_defaults

st.set_page_config(page_title=f"{APP_TITLE} · Voice DNA", layout="wide")
ensure_session_defaults()
st.title("🎙️ Voice DNA")
st.caption("النظام بيتعلم أسلوبك من كتاباتك السابقة، ويستخدمه في كل مشاريعك الجاية.")

db = get_db()
writer_id = st.text_input("معرّف الكاتب (writer_id)", value=st.session_state["writer_id"])
st.session_state["writer_id"] = writer_id

existing = db.load_voice_profile(writer_id)
samples = db.list_voice_samples(writer_id)

st.divider()
st.subheader("إضافة عيّنة كتابة جديدة")
with st.form("add_sample"):
    sample = st.text_area(
        "سكريبت قديم / منشور / تفريغ فيديو / أي نص كتبته إنت بنفسك",
        height=150,
    )
    if st.form_submit_button("أضف العيّنة") and sample.strip():
        engine = VoiceEngine(db, GeminiClient())
        profile = engine.add_sample_and_refresh(writer_id, sample.strip())
        if profile:
            st.success("اتضافت العيّنة واتحدّثت البصمة الصوتية.")
        else:
            st.info("اتضافت العيّنة. محتاج عيّنة واحدة كمان على الأقل عشان نستخرج البصمة.")
        st.rerun()

st.divider()
st.subheader(f"العيّنات المسجّلة ({len(samples)})")
for i, s in enumerate(samples, 1):
    with st.expander(f"عيّنة {i}"):
        st.write(s)

st.divider()
st.subheader("البصمة الصوتية المستخرجة")
if existing and existing.traits:
    for key, value in existing.traits.items():
        st.write(f"**{key}:** {value}")
    if existing.notes:
        st.caption(existing.notes)
else:
    st.info("لسه مفيش بصمة مستخرجة. ضيف عيّنتين على الأقل عشان تتستخرج تلقائيًا.")
