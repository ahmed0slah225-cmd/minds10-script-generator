"""
pages/6_⚙️_Settings.py
=========================
إعدادات التشغيل: حالة مفتاح Gemini، تفعيل/تعطيل البحث الخارجي، وعرض
إعدادات قاعدة البيانات الحالية (Turso أو SQLite محلي).
"""

from __future__ import annotations

import streamlit as st

from config import (
    APP_TITLE, GEMINI_MODEL_NAME, TURSO_DATABASE_URL, LOCAL_SQLITE_PATH,
    MIN_DURATION_MINUTES, MAX_DURATION_MINUTES,
)
from engine.gemini_client import _read_api_key
from utils.ui_common import ensure_session_defaults

st.set_page_config(page_title=f"{APP_TITLE} · Settings", layout="wide")
ensure_session_defaults()
st.title("⚙️ Settings")

st.subheader("حالة الاتصال")
api_key = _read_api_key()
if api_key:
    st.success(f"✅ GEMINI_API_KEY موجود. الموديل الحالي: `{GEMINI_MODEL_NAME}`")
else:
    st.error(
        "❌ GEMINI_API_KEY مش موجود. ضيفه في `.streamlit/secrets.toml` (محليًا) "
        "أو في إعدادات الـSecrets على Streamlit Community Cloud."
    )

if TURSO_DATABASE_URL:
    st.success("✅ متصل بـ Turso (إنتاج).")
else:
    st.warning(f"⚠️ مفيش إعدادات Turso — شغال حاليًا على SQLite محلي: `{LOCAL_SQLITE_PATH}`")

st.divider()
st.subheader("البحث الخارجي")
st.session_state["web_research_enabled"] = st.toggle(
    "فعّل البحث على الويب أثناء مرحلة Research",
    value=st.session_state.get("web_research_enabled", False),
    help="لسه محتاج توصيل دالة web_search_fn فعلية في engine/pipeline.py حسب "
         "خطة Gemini/Google AI Studio المستخدمة عندك.",
)

st.divider()
st.subheader("حدود عامة")
st.write(f"مدة الفيديو المسموحة: من {MIN_DURATION_MINUTES} لـ{MAX_DURATION_MINUTES} دقيقة.")
