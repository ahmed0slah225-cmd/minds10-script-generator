"""
app.py
======
واجهة Streamlit لمولد السيناريو.

البحث على الويب يعمل تلقائيًا عبر DuckDuckGo ولا يحتاج checkbox أو API key.
ولو توقفت المهمة بسبب نفاد رصيد/مفتاح Gemini، يظهر زر لاستكمالها من المرحلة
التي فشلت مع الاحتفاظ بكل نواتج المراحل السابقة داخل جلسة Streamlit.
"""

from __future__ import annotations

import uuid

import streamlit as st

from core.bootstrap import bootstrap, configure_provider
from core.context import ModelSelection, PipelineContext, ResearchConfig, ResearchDepth
from core.model_registry import DEFAULT_MODEL_ID, list_available_models
from core.orchestrator import Orchestrator, StageStatus

st.set_page_config(page_title="Minds10 — مولد السيناريو", layout="wide")
bootstrap()

if "project_ctx" not in st.session_state:
    st.session_state.project_ctx = None

if "last_results" not in st.session_state:
    st.session_state.last_results = []

if "failed_stage" not in st.session_state:
    st.session_state.failed_stage = None


def run_pipeline(ctx: PipelineContext, *, start_from: str | None = None):
    orchestrator = Orchestrator()
    with st.spinner(
        "جاري تشغيل خط الإنتاج من البداية..."
        if start_from is None
        else f"جاري الاستكمال من مرحلة: {start_from}..."
    ):
        results = orchestrator.run(ctx, start_from=start_from)

    st.session_state.project_ctx = ctx
    st.session_state.last_results = results

    failed = next((r for r in results if r.status == StageStatus.FAILED), None)
    st.session_state.failed_stage = failed.stage_name if failed else None

    return results


def render_results(ctx: PipelineContext, results) -> None:
    if results:
        st.subheader("حالة المراحل")
        for r in results:
            icon = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⏭️",
                "running": "🔄",
                "pending": "⏳",
            }[r.status.value]
            st.write(f"{icon} **{r.stage_name}** — {r.detail}")

    if st.session_state.failed_stage:
        st.warning(
            f"المهمة توقفت عند مرحلة **{st.session_state.failed_stage}**. "
            "غيّر مفتاح Gemini من الشريط الجانبي، ثم اضغط «استكمال المهمة» "
            "لتشغيل هذه المرحلة وما بعدها فقط."
        )

    if ctx.topic_understanding:
        with st.expander("فهم الموضوع (topic_understanding)"):
            st.json(ctx.topic_understanding)

    if ctx.strategy:
        with st.expander("الاستراتيجية"):
            st.json(ctx.strategy)

    if ctx.story:
        with st.expander("القصة"):
            st.json(ctx.story)

    if ctx.outline:
        with st.expander("مسار الاحتفاظ / الهيكل (outline)"):
            st.json(ctx.outline)

    if ctx.hooks:
        with st.expander("خيارات الهوك"):
            for h in ctx.hooks:
                st.markdown(f"**[{h.get('technique')}]** {h.get('text')}")
                st.caption(f"يفي بالوعد عبر: {h.get('fulfills_promise')}")

    if ctx.draft_script:
        st.subheader("المسودة الأولى")
        st.text_area(
            "draft_script",
            value=ctx.draft_script,
            height=250,
            label_visibility="collapsed",
        )

    if ctx.humanized_script:
        st.subheader("بعد الأنسنة + تحرير العامية")
        st.text_area(
            "humanized_script",
            value=ctx.humanized_script,
            height=250,
            label_visibility="collapsed",
        )

    if ctx.final_script:
        st.subheader("النص النهائي")
        st.text_area(
            "final_script",
            value=ctx.final_script,
            height=300,
            label_visibility="collapsed",
        )

    if ctx.review_notes:
        with st.expander(f"ملاحظات المراجعة ({len(ctx.review_notes)})"):
            st.json(ctx.review_notes)


st.title("Minds10 — مولد السيناريو")
st.caption("منصة إنتاج سكريبتات YouTube — فهم أولًا، ثم كتابة.")

with st.sidebar:
    st.header("إعدادات المشروع")

    st.subheader("مفتاح Gemini API")
    api_key_input = st.text_input(
        "GEMINI_API_KEY",
        type="password",
        value=st.session_state.get("gemini_api_key", ""),
        help=(
            "مفتاح Gemini مطلوب للمراحل التي تستدعي الموديل. "
            "البحث على الويب لا يحتاج المفتاح لأنه يتم مباشرة عبر DuckDuckGo."
        ),
    )
    st.session_state["gemini_api_key"] = api_key_input
    configure_provider(api_key=api_key_input or None)

    if not api_key_input:
        st.caption("⚠️ حط مفتاح Gemini قبل تشغيل المراحل التي تحتاج الموديل.")

    st.divider()

    project_name = st.text_input("اسم المشروع", value="مشروع جديد")
    duration = st.number_input("مدة الفيديو (دقيقة)", min_value=1, max_value=180, value=15)
    audience = st.text_input("الجمهور المستهدف", value="")

    st.divider()
    st.subheader("الموديل")

    models = list_available_models()
    model_labels = {m.display_name: m.model_id for m in models}
    ordered_labels = sorted(
        model_labels.keys(),
        key=lambda name: model_labels[name] != DEFAULT_MODEL_ID,
    )
    default_index = 0

    selected_label = st.selectbox("اختر الموديل", ordered_labels, index=default_index)
    selected_model_id = model_labels[selected_label]
    st.caption(f"الموديل المستخدم فعليًا: `{selected_model_id}`")

    st.divider()
    st.subheader("البحث على الويب")
    st.success("البحث يعمل تلقائيًا عبر DuckDuckGo — لا يوجد مربع إذن.")
    depth_choice = st.select_slider(
        "عمق البحث",
        options=["أساسي", "معيار", "عميق"],
        value="معيار",
    )
    research_depth = {
        "أساسي": ResearchDepth.BASIC,
        "معيار": ResearchDepth.STANDARD,
        "عميق": ResearchDepth.DEEP,
    }[depth_choice]

    st.divider()
    raw_input = st.text_area("المادة الخام / الفكرة", height=150)

    st.divider()
    st.subheader("مصدر PDF (اختياري)")
    uploaded_pdf = st.file_uploader("ارفع ملف PDF", type=["pdf"])
    pdf_page_start, pdf_page_end = None, None
    if uploaded_pdf is not None:
        col_a, col_b = st.columns(2)
        pdf_page_start = col_a.number_input("من صفحة", min_value=1, value=1, step=1)
        pdf_page_end = col_b.number_input("إلى صفحة", min_value=1, value=20, step=1)
        st.caption("النظام هيقرأ النطاق ده بالظبط فقط، مش الملف كله.")

    start_clicked = st.button(
        "ابدأ التوليد",
        type="primary",
        use_container_width=True,
    )

    resume_clicked = False
    if st.session_state.project_ctx is not None and st.session_state.failed_stage:
        st.divider()
        st.info(f"المشروع متوقف عند: **{st.session_state.failed_stage}**")
        resume_clicked = st.button(
            "▶️ استكمال المهمة",
            type="secondary",
            use_container_width=True,
        )


if start_clicked:
    ctx = PipelineContext(
        project_id=str(uuid.uuid4()),
        project_name=project_name,
        raw_input=raw_input,
        duration_minutes=int(duration),
        audience=audience or None,
        # البحث أصبح تلقائيًا دائمًا.
        research=ResearchConfig(enabled=True, depth=research_depth),
        model_selection=ModelSelection(project_default=selected_model_id),
    )

    if uploaded_pdf is not None:
        import tempfile
        import os as _os

        tmp_dir = tempfile.mkdtemp()
        tmp_path = _os.path.join(tmp_dir, uploaded_pdf.name)
        with open(tmp_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        ctx.constraints["pdf_path"] = tmp_path
        ctx.constraints["page_range"] = (int(pdf_page_start), int(pdf_page_end))

    st.session_state.project_ctx = ctx
    st.session_state.failed_stage = None
    st.session_state.last_results = []

    results = run_pipeline(ctx)
    render_results(ctx, results)


elif resume_clicked:
    ctx = st.session_state.project_ctx
    failed_stage = st.session_state.failed_stage

    if ctx is not None and failed_stage:
        # configure_provider() سبق أن أخذ المفتاح الجديد من الـSidebar في هذا rerun.
        results = run_pipeline(ctx, start_from=failed_stage)
        render_results(ctx, results)


elif st.session_state.project_ctx is not None:
    ctx = st.session_state.project_ctx
    st.info(
        f"مشروع محمّل في الجلسة: **{ctx.project_name}** — "
        f"البحث: DuckDuckGo تلقائي — "
        f"الموديل: `{ctx.model_selection.project_default}`"
    )

    if st.session_state.last_results:
        render_results(ctx, st.session_state.last_results)
