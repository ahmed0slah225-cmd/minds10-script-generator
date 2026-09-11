import os
import re
from dataclasses import asdict

import streamlit as st

from core.context import (
    ModelConfig, PipelineContext, ProjectSettings, ResearchConfig,
)
from core.model_registry import model_registry, DEFAULT_MODEL_ID
from core.orchestrator import Orchestrator
from core.pipeline import PIPELINE_STAGES
from providers.gemini import GeminiProvider
from engines.input_engine import InputEngine
from engines.topic_engine import TopicEngine
from engines.research_engine import ResearchEngine
from engines.knowledge_engine import KnowledgeEngine
from engines.audience_engine import AudienceEngine
from engines.strategy_engine import StrategyEngine
from engines.story_engine import StoryEngine
from engines.hook_engine import HookEngine
from engines.script_engine import ScriptEngine
from engines.humanize_engine import HumanizeEngine
from engines.anti_slop_engine import AntiSlopEngine
from engines.retention_engine import RetentionEngine
from engines.final_editor_engine import FinalEditorEngine
import skills  # noqa: F401 (يُسجّل الـSkills)
from services.storage import list_projects, load_project, save_project


st.set_page_config(page_title="Minds10 — مولّد السيناريو", layout="wide")

# -------- CSS عربي بسيط --------
st.markdown(
    """
    <style>
    html, body, [class*="css"] { direction: rtl; text-align: right; }
    .stTextArea textarea { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; }
    .stTextInput input { direction: rtl; text-align: right; }
    h1, h2, h3 { text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎬 Minds10 — مولّد السيناريو")

# -------- Sidebar --------
with st.sidebar:
    st.header("⚙️ إعدادات المشروع")

    project_name = st.text_input("اسم المشروع", value="مشروعي")
    duration = st.number_input("مدة الفيديو (دقيقة)", min_value=1, max_value=120, value=15)
    audience = st.text_input("الجمهور", value="شباب مصري 18-35")
    language = st.selectbox("لغة الإخراج", ["ar-EG"], index=0)
    output_format = st.selectbox("شكل الفيديو", ["youtube-long-form"], index=0)

    st.divider()
    st.subheader("🧠 اختيار الموديل")

    models = model_registry.list_enabled()
    model_display = {m.id: f"{m.display_name} ({m.id})" for m in models}
    default_index = 0
    if DEFAULT_MODEL_ID in model_display:
        default_index = list(model_display.keys()).index(DEFAULT_MODEL_ID)
    selected_model = st.selectbox(
        "نموذج المشروع",
        options=list(model_display.keys()),
        index=default_index,
        format_func=lambda x: model_display[x],
    )

    st.caption(f"📌 الموديل الافتراضي: {model_registry.get(DEFAULT_MODEL_ID).display_name}")

    st.divider()
    st.subheader("🔍 البحث على الويب")

    web_research = st.checkbox("تفعيل البحث على الويب", value=False,
                               help="لو مقفولة، النظام يعتمد على مدخلاتك فقط.")

    research_depth = st.selectbox(
        "عمق البحث",
        ["basic", "standard", "deep"],
        index=1,
        disabled=not web_research,
    )
    if not web_research:
        st.caption("🔴 البحث مغلق — لا يتم أي اتصال خارجي.")

    st.divider()
    st.subheader("🎙️ Voice DNA")
    voice_dna_choice = st.selectbox(
        "اختر Voice DNA",
        ["(لا يوجد)"],
        index=0,
    )

# -------- Main --------
tab1, tab2, tab3 = st.tabs(["📝 إدخال ومولّد", "📋 السجل", "💾 محفوظاتي"])

with tab1:
    st.subheader("📥 المادة الخام")
    raw_input = st.text_area(
        "اكتب المادة الخام (نص، فكرة، سكريبت خاطئ، ...)",
        height=220,
        placeholder="اكتب هنا الفكرة أو النص اللي عايز تحوله لسكريبت YouTube...",
    )

    uploaded_pdf = st.file_uploader("أو ارفع PDF (اختياري)", type=["pdf"])

    col_run, col_clear = st.columns([1, 1])
    run_clicked = col_run.button("🚀 ابدأ التوليد", type="primary", use_container_width=True)
    clear_clicked = col_clear.button("🧹 مسح النتيجة", use_container_width=True)

    if clear_clicked:
        st.session_state.pop("last_ctx", None)
        st.rerun()

    if run_clicked:
        if not raw_input.strip() and not uploaded_pdf:
            st.error("لازم تدخل نص أو ترفع PDF.")
        else:
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key:
                st.warning("⚠️ GEMINI_API_KEY غير مضبوط. اضبطه في متغيرات البيئة.")

            project_settings = ProjectSettings(
                project_name=project_name,
                duration_minutes=int(duration),
                audience=audience,
                language=language,
                output_format=output_format,
                voice_dna_id=None if voice_dna_choice == "(لا يوجد)" else voice_dna_choice,
            )
            research_config = ResearchConfig(
                enabled=bool(web_research),
                depth=research_depth if web_research else "standard",
            )
            model_config = ModelConfig(
                default_model=selected_model,
                engine_overrides={},  # مبدئيًا لا overrides
            )

            ctx = PipelineContext(
                project_settings=project_settings,
                raw_input=raw_input,
                source_type="text",
                research_config=research_config,
                model_config=model_config,
            )

            # ملاحظة: هنا ممكن نضيف معالجة PDF (pypdf) — بسيطة
            if uploaded_pdf is not None:
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(uploaded_pdf)
                    pages_text = []
                    for i, page in enumerate(reader.pages):
                        pages_text.append(page.extract_text() or "")
                    ctx.raw_input = (ctx.raw_input or "") + "\n\n" + "\n".join(pages_text)
                    ctx.source_type = "pdf"
                except Exception as e:
                    st.error(f"فشل قراءة الـPDF: {e}")

            # Provider
            try:
                provider = GeminiProvider(api_key=api_key or None)
            except Exception as e:
                st.error(f"فشل تهيئة الموديل: {e}")
                st.stop()

            # Orchestrator + Engines
            orch = Orchestrator(provider)
            orch.register("input", InputEngine())
            orch.register("topic", TopicEngine())
            orch.register("research", ResearchEngine())
            orch.register("knowledge", KnowledgeEngine())
            orch.register("audience", AudienceEngine())
            orch.register("strategy", StrategyEngine())
            orch.register("story", StoryEngine())
            orch.register("hook", HookEngine())
            orch.register("script", ScriptEngine())
            orch.register("humanize", HumanizeEngine())
            orch.register("anti_slop", AntiSlopEngine())
            orch.register("retention_review", RetentionEngine())
            orch.register("final_editor", FinalEditorEngine())

            progress = st.progress(0.0)
            status = st.empty()

            def on_progress(stage, idx, total):
                pct = idx / total
                progress.progress(pct)
                status.info(f"⏳ المرحلة {idx}/{total}: **{stage}**")

            with st.spinner("جاري التوليد..."):
                ctx = orch.run(ctx, on_progress=on_progress)

            progress.progress(1.0)
            status.success("✅ انتهى التوليد.")
            st.session_state["last_ctx"] = ctx

    # عرض النتيجة
    ctx = st.session_state.get("last_ctx")
    if ctx:
        if ctx.errors:
            with st.expander("⚠️ أخطاء/تحذيرات"):
                for e in ctx.errors:
                    st.warning(e)

        with st.expander("🧭 تحليل الموضوع", expanded=False):
            st.json(ctx.topic_analysis or {})

        if ctx.research_config.enabled:
            with st.expander("🔎 نتائج البحث الخارجي", expanded=False):
                st.json(ctx.research_results or [])

        with st.expander("📚 قاعدة المعرفة", expanded=False):
            st.json([asdict(k) for k in ctx.knowledge_base])

        with st.expander("👥 الجمهور", expanded=False):
            st.json(ctx.audience_profile or {})

        with st.expander("🎯 الاستراتيجية", expanded=False):
            st.json(ctx.strategy or {})

        with st.expander("📖 القصة", expanded=False):
            st.json(ctx.story or {})

        with st.expander("🪝 الـHook", expanded=False):
            st.write(ctx.hook or "(لا يوجد)")

        with st.expander("📝 مسودة السكريبت", expanded=False):
            st.write(ctx.draft or "(لا يوجد)")

        with st.expander("🧍 بعد Humanize", expanded=False):
            st.write(ctx.humanized or "(لا يوجد)")

        with st.expander("🧪 تقرير Anti-Slop", expanded=False):
            st.json(ctx.slop_report or {})

        with st.expander("⏱️ تقرير الاحتفاظ", expanded=False):
            st.json(ctx.retention_report or {})

        st.subheader("🎉 السكريبت النهائي")
        st.text_area("النص النهائي", value=ctx.final_script or "", height=400)
        st.download_button(
            "⬇️ تنزيل السكريبت",
            data=(ctx.final_script or "").encode("utf-8"),
            file_name=f"{ctx.project_settings.project_name}.txt",
            mime="text/plain",
        )

        col_a, col_b = st.columns(2)
        if col_a.button("💾 احفظ المشروع", use_container_width=True):
            path = save_project(ctx.project_settings.project_name, {
                "project_settings": ctx.project_settings,
                "raw_input": ctx.raw_input,
                "model_config": ctx.model_config,
                "research_config": ctx.research_config,
                "topic_analysis": ctx.topic_analysis,
                "knowledge_base": [asdict(k) for k in ctx.knowledge_base],
                "audience_profile": ctx.audience_profile,
                "strategy": ctx.strategy,
                "story": ctx.story,
                "hook": ctx.hook,
                "draft": ctx.draft,
                "humanized": ctx.humanized,
                "slop_report": ctx.slop_report,
                "retention_report": ctx.retention_report,
                "final_script": ctx.final_script,
                "run_log": ctx.run_log,
            })
            st.success(f"✅ اتحدف: {path}")

        if col_b.button("📌 اعرض سجل التشغيل", use_container_width=True):
            st.json(ctx.run_log)

with tab2:
    st.subheader("📋 سجل التشغيل لكل نداء Model")
    ctx = st.session_state.get("last_ctx")
    if not ctx:
        st.info("لسه مفيش تشغيل.")
    else:
        st.dataframe(ctx.run_log, use_container_width=True)

with tab3:
    st.subheader("💾 المشاريع المحفوظة")
    projects = list_projects()
    if not projects:
        st.info("مفيش مشاريع محفوظة بعد.")
    else:
        chosen = st.selectbox("اختر مشروع", projects)
        if st.button("📂 تحميل"):
            data = load_project(chosen)
            st.session_state["loaded_project"] = data
        if "loaded_project" in st.session_state:
            st.json(st.session_state["loaded_project"])