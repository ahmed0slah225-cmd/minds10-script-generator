"""
app.py
======
واجهة Streamlit لمنصة Minds10 - مولد السيناريو.
حالة الواجهة (session_state) ≠ قاعدة البيانات. المشاريع تُحفظ في db/storage.py.
"""

from __future__ import annotations
import os
import tempfile

import streamlit as st

from core import model_registry
from core.context import PipelineContext, ResearchConfig, SourceMaterial, VoiceDNA
from core.pipeline import ScriptPipeline
from providers.gemini_provider import build_provider
from utils.pdf_reader import extract_pdf_text_range, get_pdf_page_count
from db import storage

st.set_page_config(page_title="Minds10 - مولد السيناريو", page_icon="🎬", layout="wide")
storage.init_db()

# ---------------------------------------------------------------------------
# اتجاه RTL بسيط للواجهة
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp, .stMarkdown, textarea, input { direction: rtl; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎬 Minds10 — مولد السيناريو")
st.caption("منصة ذكاء اصطناعي لإنتاج سكريبتات يوتيوب احترافية بالعامية المصرية")

# ---------------------------------------------------------------------------
# مفتاح Gemini API
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ الإعدادات العامة")
    api_key = st.text_input(
        "مفتاح Gemini API",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        help="يمكنك أيضًا وضعه في Secrets الخاصة بـ Streamlit باسم GEMINI_API_KEY",
    )
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            api_key = ""

    st.divider()
    st.subheader("📁 المشاريع المحفوظة")
    projects = storage.list_projects()
    project_names = {p["id"]: p["name"] for p in projects}
    selected_project_id = st.selectbox(
        "افتح مشروعًا سابقًا",
        options=[None] + list(project_names.keys()),
        format_func=lambda pid: "— مشروع جديد —" if pid is None else project_names[pid],
    )

# تحميل مشروع سابق في الـ session_state (حالة واجهة فقط، بند 51)
if selected_project_id and st.session_state.get("_loaded_project_id") != selected_project_id:
    loaded = storage.load_project(selected_project_id)
    if loaded:
        st.session_state["_loaded_project_id"] = selected_project_id
        st.session_state["_loaded_state"] = loaded["state"]
        st.session_state["_loaded_settings"] = loaded["settings"]

loaded_settings = st.session_state.get("_loaded_settings", {})
loaded_state = st.session_state.get("_loaded_state", {})

# ---------------------------------------------------------------------------
# إعدادات المشروع
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    project_name = st.text_input("اسم المشروع", value=loaded_settings.get("project_name", "مشروع بدون اسم"))
    duration_minutes = st.number_input(
        "مدة الفيديو (بالدقائق)", min_value=1, max_value=90,
        value=int(loaded_settings.get("duration_minutes", 10)),
    )
    audience = st.text_input(
        "الجمهور المستهدف", value=loaded_settings.get("audience", "شباب مصري 18-35"),
    )

with col2:
    available_models = model_registry.list_available_models()
    model_ids = [m.model_id for m in available_models]
    default_model = model_registry.get_default_model().model_id
    saved_model = loaded_settings.get("default_model_id", default_model)
    model_index = model_ids.index(saved_model) if saved_model in model_ids else model_ids.index(default_model)

    selected_model_id = st.selectbox(
        "الموديل",
        options=model_ids,
        index=model_index,
        format_func=lambda mid: next(m.display_name_ar for m in available_models if m.model_id == mid),
    )
    st.caption(next(m.notes_ar for m in available_models if m.model_id == selected_model_id))

    # مربع البحث على الويب - الحالة الافتراضية دائمًا: إيقاف (بند 21)
    web_research_enabled = st.checkbox(
        "☐ تفعيل البحث المباشر من الإنترنت",
        value=bool(loaded_settings.get("web_research_enabled", False)),
        help="لو ماكنش متفعّل، النظام لن يبحث في الإنترنت إطلاقًا، وسيعتمد فقط على كلامك وملفاتك.",
    )
    research_depth = "قياسي"
    if web_research_enabled:
        research_depth = st.select_slider(
            "عمق البحث", options=["أساسي", "قياسي", "عميق"],
            value=loaded_settings.get("research_depth", "قياسي"),
        )
        st.info("البحث مفعّل: النظام هيدوّر على معلومات من الإنترنت وقت الحاجة فقط.")
    else:
        st.warning("البحث متوقف: النظام هيعتمد بس على كلامك والملفات اللي هترفعها.")

st.divider()

# ---------------------------------------------------------------------------
# مصدر المحتوى
# ---------------------------------------------------------------------------
st.subheader("📥 المادة الخام")
source_kind = st.radio(
    "نوع المصدر", options=["موضوع/فكرة", "نص جاهز", "ملف PDF"], horizontal=True,
)

source_material: SourceMaterial | None = None
uploaded_pdf_path = None

if source_kind == "موضوع/فكرة":
    topic_text = st.text_area("اكتب الموضوع أو الفكرة", height=120, placeholder="مثلاً: ليه الناس بتسوف؟")
    if topic_text:
        source_material = SourceMaterial(kind="topic", raw_text=topic_text)

elif source_kind == "نص جاهز":
    raw_text = st.text_area("الصق النص هنا", height=200)
    if raw_text:
        source_material = SourceMaterial(kind="text", raw_text=raw_text)

else:
    pdf_file = st.file_uploader("ارفع ملف PDF", type=["pdf"])
    if pdf_file:
        tmp_dir = tempfile.gettempdir()
        uploaded_pdf_path = os.path.join(tmp_dir, pdf_file.name)
        with open(uploaded_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        try:
            total_pages = get_pdf_page_count(uploaded_pdf_path)
            st.caption(f"عدد صفحات الملف: {total_pages}")
        except Exception as e:
            total_pages = 1
            st.error(f"تعذّرت قراءة الملف: {e}")

        pcol1, pcol2 = st.columns(2)
        with pcol1:
            page_start = st.number_input("من صفحة", min_value=1, max_value=total_pages, value=1)
        with pcol2:
            page_end = st.number_input("إلى صفحة", min_value=1, max_value=total_pages, value=min(20, total_pages))

        if page_start > page_end:
            st.error("رقم صفحة البداية لازم يكون أصغر من أو يساوي النهاية.")
        else:
            extracted = extract_pdf_text_range(uploaded_pdf_path, int(page_start), int(page_end))
            source_material = SourceMaterial(
                kind="pdf", raw_text=extracted, pdf_path=uploaded_pdf_path,
                pdf_page_start=int(page_start), pdf_page_end=int(page_end),
            )
            with st.expander("معاينة النص المستخرج"):
                st.text(extracted[:3000] + ("..." if len(extracted) > 3000 else ""))

st.divider()

# ---------------------------------------------------------------------------
# الحمض النووي الصوتي (اختياري)
# ---------------------------------------------------------------------------
with st.expander("🎙️ الحمض النووي الصوتي (اختياري)"):
    voice_name = st.text_input("اسم البروفايل", value="افتراضي")
    voice_samples_text = st.text_area(
        "الصق عينات من كتابتك أو سكريبتات سابقة لك (كل عينة في سطر منفصل بفاصل ---)",
        height=120,
    )

st.divider()

# ---------------------------------------------------------------------------
# التشغيل
# ---------------------------------------------------------------------------
run_clicked = st.button("🚀 إنتاج السكريبت", type="primary", use_container_width=True)

if run_clicked:
    if not api_key:
        st.error("من فضلك أدخل مفتاح Gemini API في الشريط الجانبي أولاً.")
    elif not source_material or not (source_material.raw_text or "").strip():
        st.error("من فضلك أدخل مادة خام (موضوع أو نص أو ملف PDF) قبل التشغيل.")
    else:
        voice_samples = [s.strip() for s in voice_samples_text.split("---") if s.strip()] if voice_samples_text else []

        ctx = PipelineContext(
            project_name=project_name,
            duration_minutes=int(duration_minutes),
            audience=audience,
            default_model_id=selected_model_id,
            research_config=ResearchConfig(enabled=web_research_enabled, depth=research_depth),
            voice_dna=VoiceDNA(name=voice_name, sample_texts=voice_samples),
            source=source_material,
        )

        provider = build_provider(api_key)
        pipeline = ScriptPipeline()

        progress_placeholder = st.empty()
        progress_bar = st.progress(0)
        steps_done = {"n": 0}
        TOTAL_STEPS = 12

        def on_progress(label):
            steps_done["n"] += 1
            progress_placeholder.info(label)
            progress_bar.progress(min(steps_done["n"] / TOTAL_STEPS, 1.0))

        with st.spinner("جاري إنتاج السكريبت..."):
            outcomes = pipeline.run(ctx, provider, progress_cb=on_progress)

        progress_bar.progress(1.0)

        critical_failure = next((o for o in outcomes if o.critical and not o.ok), None)
        if critical_failure:
            st.error(f"فشلت مرحلة أساسية ({critical_failure.stage_name}): {critical_failure.error}")
        else:
            st.success("تم إنتاج السكريبت بنجاح ✅")

            settings_to_save = {
                "project_name": project_name,
                "duration_minutes": duration_minutes,
                "audience": audience,
                "default_model_id": selected_model_id,
                "web_research_enabled": web_research_enabled,
                "research_depth": research_depth,
            }
            state_to_save = {
                "topic_understanding": ctx.topic_understanding,
                "audience_profile": ctx.audience_profile,
                "strategy": ctx.strategy,
                "story": ctx.story,
                "hooks": ctx.hooks,
                "anti_slop_report": ctx.anti_slop_report,
                "final_script": ctx.final_script,
                "draft_script": ctx.draft_script,
            }
            saved_id = storage.save_project(selected_project_id, project_name, settings_to_save, state_to_save)
            storage.save_version(saved_id, "final", ctx.final_script)

            tabs = st.tabs(["📝 السكريبت النهائي", "🎣 الخطافات", "🔍 التحليل والاستراتيجية", "📊 تقرير الجودة", "⚠️ تحذيرات وسجلات"])

            with tabs[0]:
                st.text_area("السكريبت النهائي", value=ctx.final_script, height=500)
                st.download_button("⬇️ تحميل كملف نصي", data=ctx.final_script, file_name=f"{project_name}.txt")

            with tabs[1]:
                for i, h in enumerate(ctx.hooks, 1):
                    st.markdown(f"**خطاف {i}:** {h}")

            with tabs[2]:
                st.json(ctx.topic_understanding)
                st.json(ctx.audience_profile)
                st.json(ctx.strategy)
                st.json(ctx.story)

            with tabs[3]:
                if ctx.anti_slop_report:
                    st.json(ctx.anti_slop_report)
                else:
                    st.write("لا يوجد تقرير جودة.")

            with tabs[4]:
                if ctx.warnings:
                    for w in ctx.warnings:
                        st.warning(w)
                else:
                    st.write("لا توجد تحذيرات.")
                st.subheader("سجل تشغيل الموديلات")
                st.table(ctx.run_logs)
