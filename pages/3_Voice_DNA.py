"""
pages/3_Voice_DNA.py
------------------------
إدارة بصمات الكاتب الصوتية: إضافة عينات كتابة سابقة، استخراج البصمة،
وعرض البصمات المحفوظة لاختيارها لاحقًا في Project Workspace.
"""

import streamlit as st

from config import APP_ICON
from engine.persistence import backend
from engine.engines import voice_dna

st.set_page_config(page_title="Voice DNA", page_icon=APP_ICON, layout="wide")
st.title("🎙️ Voice DNA — بصمة الكاتب الصوتية")

st.caption(
    "ألصق عينات من كتاباتك السابقة (سكريبتات، مقالات، منشورات، تفريغ "
    "فيديوهات) عشان النظام يستخرج أنماط أسلوبك، مش عشان ينسخها حرفيًا."
)

with st.form("new_voice_profile"):
    name = st.text_input("اسم البصمة", placeholder="مثال: بصمتي في فيديوهات التطوير الذاتي")
    samples_raw = st.text_area(
        "عينات الكتابة (افصل بين كل عينة وتانية بسطر فيه ===)",
        height=300,
        placeholder="عينة 1...\n===\nعينة 2...\n===\nعينة 3...",
    )
    submitted = st.form_submit_button("استخراج البصمة", type="primary")
    if submitted:
        samples = [s.strip() for s in samples_raw.split("===") if s.strip()]
        if not name.strip() or not samples:
            st.error("لازم اسم للبصمة، وعينة كتابة واحدة على الأقل.")
        else:
            with st.spinner("جاري تحليل العينات واستخراج البصمة..."):
                try:
                    profile = voice_dna.extract_voice_profile(name.strip(), samples)
                    backend().save_voice_profile(profile)
                    st.success("تم استخراج البصمة وحفظها ✅")
                except Exception as e:  # noqa: BLE001
                    st.error(f"حصل خطأ أثناء الاستخراج: {e}")

st.divider()
st.subheader("البصمات المحفوظة")
profiles = backend().list_voice_profiles()
if not profiles:
    st.info("معندكش أي بصمة محفوظة لسه.")
else:
    for p in profiles:
        with st.expander(f"🎙️ {p.name}"):
            st.markdown(f"**ملخص عام:** {p.raw_traits_summary}")
            cols = st.columns(3)
            fields = [
                ("طول الجمل", p.avg_sentence_length), ("الإيقاع", p.pacing),
                ("استخدام الأسئلة", p.question_usage), ("المفردات", p.vocabulary_notes),
                ("درجة العامية", p.slang_level), ("درجة العاطفة", p.emotion_level),
                ("طريقة الشرح", p.explanation_style), ("طريقة الأمثلة", p.example_style),
                ("الانتقالات", p.transition_style),
            ]
            for i, (label, value) in enumerate(fields):
                cols[i % 3].markdown(f"**{label}:** {value or '—'}")
