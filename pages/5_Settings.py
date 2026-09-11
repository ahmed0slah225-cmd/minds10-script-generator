"""
pages/5_Settings.py
-----------------------
حالة الاتصال بالمفاتيح (Gemini / Turso) + أعلام تشغيل يمكن التحكم فيها
وقت التشغيل (زي تفعيل البحث الخارجي أو تعطيل مراجعة معينة مؤقتًا).
"""

import streamlit as st

from config import (
    APP_ICON, GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MODEL_DEEP,
    TURSO_DATABASE_URL, LOCAL_SQLITE_FALLBACK, DEFAULT_RUNTIME_FLAGS,
)

st.set_page_config(page_title="Settings", page_icon=APP_ICON, layout="wide")
st.title("⚙️ Settings")

st.subheader("حالة الاتصال")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Gemini**")
    st.write("✅ المفتاح موجود" if GEMINI_API_KEY else "❌ GEMINI_API_KEY غير موجود")
    st.write(f"الموديل الافتراضي: `{GEMINI_MODEL}`")
    st.write(f"الموديل العميق: `{GEMINI_MODEL_DEEP}`")
with c2:
    st.markdown("**التخزين**")
    if TURSO_DATABASE_URL:
        st.write("✅ Turso متظبط (سيُستخدم لو المكتبة مثبتة، وإلا رجوع تلقائي لـ SQLite)")
    else:
        st.write(f"ℹ️ Turso غير متظبط — يُستخدم SQLite محلي: `{LOCAL_SQLITE_FALLBACK}`")

st.divider()
st.subheader("أعلام التشغيل (لهذه الجلسة فقط)")
st.session_state.setdefault("runtime_flags", DEFAULT_RUNTIME_FLAGS)
flags = st.session_state["runtime_flags"]

flags.web_search_enabled = st.toggle("السماح بالبحث الخارجي افتراضيًا", value=flags.web_search_enabled)
flags.deep_model_enabled = st.toggle("استخدام الموديل العميق في مراحل التحليل الثقيلة", value=flags.deep_model_enabled)
flags.allow_humanization = st.toggle("تفعيل مهارة Humanize", value=flags.allow_humanization)
flags.allow_anti_slop = st.toggle("تفعيل مراجعة Anti-Slop", value=flags.allow_anti_slop)
flags.allow_retention_review = st.toggle("تفعيل مراجعة الاحتفاظ بالمشاهد", value=flags.allow_retention_review)
flags.max_review_passes = st.number_input("أقصى عدد لإعادة المراجعة التلقائية", min_value=1, max_value=3, value=flags.max_review_passes)

st.session_state["runtime_flags"] = flags
st.success("الإعدادات محفوظة لهذه الجلسة.")

st.divider()
with st.expander("📄 كيف تضيف المفاتيح؟"):
    st.markdown(
        """
**محليًا:** أنشئ ملف `.env` (انسخ من `.env.example`) وحط فيه:
```
GEMINI_API_KEY=your_key_here
```

**على Streamlit Community Cloud:** من صفحة التطبيق → **⋮ Manage app** →
**Settings → Secrets**، وضيف:
```toml
GEMINI_API_KEY = "your_key_here"
TURSO_DATABASE_URL = "libsql://your-db.turso.io"
TURSO_AUTH_TOKEN = "your_token_here"
```
لو سبت TURSO_DATABASE_URL فاضي، المشروع هيشتغل بـ SQLite محلي تلقائيًا
(هيفقد البيانات لما الجلسة على Streamlit Cloud تتجدد، لذلك Turso ضروري
للاستخدام الجاد على السحابة).
        """
    )
