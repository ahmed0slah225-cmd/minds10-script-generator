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

if "rerun_stage" not in st.session_state:
    st.session_state.rerun_stage = None

if "rerun_from_stage" not in st.session_state:
    st.session_state.rerun_from_stage = None


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


STAGES = [
    ("input_understanding", "فهم المدخلات", "تحويل الفكرة الخام إلى مدخل واضح للمشروع."),
    ("topic_understanding", "فهم الموضوع", "فهم المشكلة، السؤال، الرسالة، والفجوات المعرفية."),
    ("source_analysis", "تحليل المصادر", "قراءة المادة التي قدمها المستخدم واستخراج ما يفيد السكريبت."),
    ("research", "البحث", "البحث التلقائي عبر DuckDuckGo وتجميع المصادر المرتبطة بالفكرة."),
    ("knowledge", "بناء المعرفة", "ترتيب المعلومات والأدلة التي سيُبنى عليها المحتوى."),
    ("audience", "فهم الجمهور", "تحديد ما يهم الجمهور وكيف نخاطبه بدون محاضرة."),
    ("strategy", "الاستراتيجية", "اختيار زاوية الفيديو والرسالة وطريقة تقديمها."),
    ("story", "القصة", "تحويل الأفكار إلى أمثلة وحكاية ومسار إنساني."),
    ("retention_planning", "تخطيط الاحتفاظ", "توزيع الفضول وتغيير الزوايا حتى لا يصبح الفيديو مسطحًا."),
    ("hook", "الـ Hook", "بناء بداية قوية لأول ثواني بدون مقدمات ميتة."),
    ("script", "كتابة السكريبت", "تحويل الخطة إلى نص كامل بالمصري."),
    ("humanize", "الأنسنة", "جعل النص طبيعيًا كأن شخصًا يتكلم مع شخص أمامه."),
    ("anti_slop_review", "مراجعة الـ AI Slop", "اكتشاف الجمل العامة والتكرار والنبرة الآلية."),
    ("retention_review", "مراجعة الاحتفاظ", "فحص الإيقاع والفضول ونقاط الهبوط."),
    ("repetition_review", "مراجعة التكرار", "منع إعادة نفس الفكرة أو المثال بصيغ مختلفة."),
    ("egyptian_arabic_edit", "تحرير المصري", "ضبط العامية والإيقاع ليكون الكلام طبيعيًا."),
    ("voice_dna_check", "فحص الصوت", "التأكد من اتساق النص مع أسلوب القناة."),
    ("fact_check", "تدقيق الحقائق", "مراجعة الادعاءات والمعلومات مقابل المصادر المتاحة."),
    ("final_edit", "النسخة النهائية", "تجميع التعديلات وإخراج النسخة الجاهزة."),
]


def _stage_status_map(results):
    return {r.stage_name: r for r in results}


def render_pipeline(ctx: PipelineContext | None, results) -> None:
    """واجهة Workflow على شكل Automation Graph، مع تشغيل حقيقي لكل Node."""
    status_map = _stage_status_map(results or [])

    st.subheader("⚡ Automation Workflow")
    st.caption(
        "كل مربع هنا Node حقيقي في خط الإنتاج. الأسهم توضح مسار التنفيذ، "
        "والحالة تتحدث حسب نتيجة الـOrchestrator."
    )

    st.markdown(
        """
        <style>
        .wf-node {
            border: 1px solid rgba(255,255,255,.18);
            border-radius: 12px;
            padding: 11px 12px;
            min-height: 112px;
            background: linear-gradient(145deg, rgba(255,255,255,.08), rgba(255,255,255,.025));
            box-shadow: 0 4px 14px rgba(0,0,0,.14);
        }
        .wf-node-title {font-size:15px;font-weight:750;line-height:1.25;}
        .wf-node-meta {font-size:11px;opacity:.65;margin-top:5px;}
        .wf-node-desc {font-size:11px;opacity:.78;margin-top:7px;line-height:1.45;}
        .wf-arrow {display:flex;align-items:center;justify-content:center;height:100%;font-size:22px;opacity:.6;}
        .wf-row-label {font-size:11px;opacity:.5;margin:5px 0 8px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # أربع Nodes في كل صف حتى يظل الشكل قريبًا من أدوات الـAutomation
    # بدل قائمة عمودية طويلة.
    row_size = 4
    for row_start in range(0, len(STAGES), row_size):
        row = STAGES[row_start:row_start + row_size]
        row_num = row_start // row_size + 1
        st.markdown(f'<div class="wf-row-label">FLOW {row_num}</div>', unsafe_allow_html=True)

        layout = []
        for _ in row:
            layout.extend([1, 0.18])
        layout = layout[:-1]

        cols = st.columns(layout)
        col_index = 0

        for local_index, (stage_name, label, description) in enumerate(row):
            result = status_map.get(stage_name)

            if result is None:
                icon, state = "⚪", "WAITING"
                detail = "لم تبدأ"
            elif result.status == StageStatus.PASSED:
                icon, state = "🟢", "DONE"
                detail = result.detail or "اكتملت بنجاح"
            elif result.status == StageStatus.FAILED:
                icon, state = "🔴", "FAILED"
                detail = result.detail or "توقفت هنا"
            elif result.status == StageStatus.SKIPPED:
                icon, state = "⚪", "SKIPPED"
                detail = result.detail or "تم تجاوزها"
            else:
                icon, state = "🔵", "RUNNING"
                detail = result.detail or "قيد التنفيذ"

            with cols[col_index]:
                st.markdown(
                    f'''
                    <div class="wf-node">
                        <div class="wf-node-title">{icon} {row_start + local_index + 1}. {label}</div>
                        <div class="wf-node-meta">{state} · {stage_name}</div>
                        <div class="wf-node-desc">{description}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )

                if ctx is not None:
                    a, b = st.columns(2)
                    if a.button(
                        "▶ تشغيل",
                        key=f"node_run_{stage_name}",
                        use_container_width=True,
                        help="تشغيل هذه المرحلة فقط.",
                    ):
                        st.session_state.rerun_stage = stage_name
                        st.rerun()

                    if b.button(
                        "⟳ من هنا",
                        key=f"node_from_{stage_name}",
                        use_container_width=True,
                        help="إعادة تشغيل هذه المرحلة وكل ما بعدها.",
                    ):
                        st.session_state.rerun_from_stage = stage_name
                        st.rerun()

                with st.expander("تفاصيل المرحلة", expanded=False):
                    current_instruction = ctx.stage_instructions.get(stage_name, "") if ctx else ""
                    instruction = st.text_area(
                        "تعليماتك لهذه المرحلة",
                        value=current_instruction,
                        height=130,
                        key=f"instruction_{stage_name}",
                        placeholder="اكتب بالتفصيل المطلوب، وما يجب التركيز عليه، وما الممنوع في هذه المرحلة...",
                    )
                    if ctx is not None:
                        ctx.stage_instructions[stage_name] = instruction

                    st.write(f"**الحالة:** {state}")
                    st.write(f"**وصف المرحلة:** {description}")
                    st.write(f"**آخر نتيجة:** {detail}")

                    if stage_name == "research" and ctx is not None:
                        st.markdown("### 🔎 مصادر البحث التي تختارها أنت")
                        st.caption("سطر لكل مصدر: العنوان | الرابط | أهم نقطة أو ملاحظة")
                        existing_sources = [
                            s for s in ctx.research.sources
                            if s.get("origin") == "user_provided"
                        ]
                        source_text = st.text_area(
                            "المصادر والروابط والمقالات",
                            value="\\n".join(
                                " | ".join([
                                    str(s.get("title", "")),
                                    str(s.get("url", "")),
                                    str(s.get("notes", "")),
                                ])
                                for s in existing_sources
                            ),
                            height=190,
                            key="manual_research_sources",
                            placeholder="كتاب / دراسة | https://... | استخدم هذه النقطة في السكريبت",
                        )

                        manual_sources = []
                        for line in source_text.splitlines():
                            line = line.strip()
                            if not line:
                                continue
                            parts = [p.strip() for p in line.split("|", 2)]
                            manual_sources.append({
                                "origin": "user_provided",
                                "title": parts[0] if parts else "",
                                "url": parts[1] if len(parts) > 1 else "",
                                "notes": parts[2] if len(parts) > 2 else "",
                                "snippet": parts[2] if len(parts) > 2 else "",
                            })

                        ctx.research.sources = manual_sources
                        from core.context import SourceRef
                        ctx.sources = [
                            s for s in ctx.sources
                            if s.origin != "user_provided_link"
                        ]
                        for source in manual_sources:
                            content = "\\n".join(
                                x for x in [
                                    source["title"],
                                    source["notes"],
                                    f"URL: {source['url']}" if source["url"] else "",
                                ] if x
                            )
                            ctx.sources.append(SourceRef(
                                origin="user_provided_link",
                                content=content,
                                is_primary=True,
                                trust_level="user_selected",
                            ))

                        st.info("البحث الآلي متوقف. الـPipeline سيعتمد على المصادر التي تدخلها أنت.")

                    if result and result.status == StageStatus.PASSED:
                        if stage_name == "topic_understanding" and ctx and ctx.topic_understanding:
                            st.json(ctx.topic_understanding)
                        elif stage_name == "strategy" and ctx and ctx.strategy:
                            st.json(ctx.strategy)
                        elif stage_name == "story" and ctx and ctx.story:
                            st.json(ctx.story)
                        elif stage_name == "retention_planning" and ctx and ctx.outline:
                            st.json(ctx.outline)
                        elif stage_name == "hook" and ctx and ctx.hooks:
                            for h in ctx.hooks:
                                st.markdown(f"**[{h.get('technique', 'Hook')}]** {h.get('text', '')}")
                        elif stage_name == "script" and ctx and ctx.draft_script:
                            st.text_area("ناتج المرحلة", value=ctx.draft_script, height=220, key=f"stage_{stage_name}")
                        elif stage_name == "humanize" and ctx and ctx.humanized_script:
                            st.text_area("ناتج المرحلة", value=ctx.humanized_script, height=220, key=f"stage_{stage_name}")
                        elif stage_name == "final_edit" and ctx and ctx.final_script:
                            st.text_area("ناتج المرحلة", value=ctx.final_script, height=280, key=f"stage_{stage_name}")
                        elif stage_name in {"anti_slop_review", "retention_review", "repetition_review", "fact_check"} and ctx and ctx.review_notes:
                            st.json(ctx.review_notes)

            col_index += 1
            if local_index < len(row) - 1:
                with cols[col_index]:
                    st.markdown('<div class="wf-arrow">→</div>', unsafe_allow_html=True)
                col_index += 1

        if row_start + row_size < len(STAGES):
            st.markdown(
                '<div class="wf-arrow" style="height:34px;">↓</div>',
                unsafe_allow_html=True,
            )

def render_results(ctx: PipelineContext, results) -> None:
    render_pipeline(ctx, results)

    if st.session_state.failed_stage:
        st.warning(
            f"المهمة توقفت عند مرحلة **{st.session_state.failed_stage}**. "
            "غيّر مفتاح Gemini من الشريط الجانبي، ثم اضغط «استكمال المهمة» "
            "لتشغيل هذه المرحلة وما بعدها فقط."
        )

    if ctx.draft_script and not any(name == "script" for name, _, _ in STAGES):
        st.subheader("المسودة الأولى")
        st.text_area("draft_script", value=ctx.draft_script, height=250, label_visibility="collapsed")

    if ctx.final_script:
        st.subheader("النص النهائي")
        st.text_area("final_script", value=ctx.final_script, height=300, label_visibility="collapsed")

st.title("Minds10 — مولد السيناريو")
st.caption("منصة إنتاج سكريبتات YouTube — خط إنتاج مرئي من الفكرة إلى النسخة النهائية.")

# الـPipeline هو الواجهة الرئيسية من أول لحظة، وليس مجرد نتائج تظهر بعد التوليد.
# ده يخلي شكل الموقع مختلف فعليًا عن الفورم القديم، ويخلي المستخدم شايف رحلة السكريبت كاملة.
if st.session_state.project_ctx is None:
    render_pipeline(None, [])

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
    st.subheader("البحث والمصادر")
    st.info("أنت تختار وتكتب مصادر البحث والروابط والمقالات داخل Node البحث.")
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

    # الاستكمال يظهر في الصفحة الرئيسية أيضًا، وليس داخل الـSidebar فقط.
    resume_clicked = False


# إعادة تشغيل مرحلة واحدة فقط.
if st.session_state.project_ctx is not None and st.session_state.rerun_stage:
    rerun_stage = st.session_state.rerun_stage
    st.session_state.rerun_stage = None
    ctx = st.session_state.project_ctx
    with st.spinner(f"جاري إعادة تشغيل مرحلة: {rerun_stage}..."):
        rerun_result = Orchestrator().run_one_stage(ctx, rerun_stage)

    st.session_state.project_ctx = ctx
    current_results = [r for r in (st.session_state.last_results or []) if r.stage_name != rerun_stage]
    current_results.append(rerun_result)
    order = {name: i for i, (name, _, _) in enumerate(STAGES)}
    current_results.sort(key=lambda r: order.get(r.stage_name, 999))
    st.session_state.last_results = current_results
    if st.session_state.failed_stage == rerun_stage and rerun_result.status == StageStatus.PASSED:
        st.session_state.failed_stage = None

    if rerun_result.status == StageStatus.PASSED:
        st.success(f"تمت إعادة مرحلة **{rerun_stage}** فقط بنجاح. المراحل السابقة واللاحقة لم تُشغّل.")
    else:
        st.error(f"المرحلة **{rerun_stage}** ما زالت متوقفة: {rerun_result.detail}")
    st.rerun()


# إعادة التشغيل من مرحلة معينة وحتى نهاية الـPipeline، مع الحفاظ على كل ما قبلها.
if st.session_state.project_ctx is not None and st.session_state.rerun_from_stage:
    rerun_from_stage = st.session_state.rerun_from_stage
    st.session_state.rerun_from_stage = None
    ctx = st.session_state.project_ctx
    with st.spinner(f"جاري إعادة الـPipeline من مرحلة: {rerun_from_stage}..."):
        partial_results = Orchestrator().run(ctx, start_from=rerun_from_stage)

    st.session_state.project_ctx = ctx
    stage_order = {name: i for i, (name, _, _) in enumerate(STAGES)}
    start_index = stage_order.get(rerun_from_stage, 0)
    previous_results = [
        r for r in (st.session_state.last_results or [])
        if stage_order.get(r.stage_name, 999) < start_index
    ]
    rerun_results_only = [
        r for r in partial_results
        if stage_order.get(r.stage_name, 999) >= start_index
    ]
    st.session_state.last_results = previous_results + rerun_results_only
    failed = next((r for r in rerun_results_only if r.status == StageStatus.FAILED), None)
    st.session_state.failed_stage = failed.stage_name if failed else None
    st.rerun()


if st.session_state.project_ctx is not None and st.session_state.rerun_stage:
    rerun_stage = st.session_state.rerun_stage
    st.session_state.rerun_stage = None
    ctx = st.session_state.project_ctx
    with st.spinner(f"جاري إعادة تشغيل مرحلة: {rerun_stage}..."):
        rerun_result = Orchestrator().run_one_stage(ctx, rerun_stage)

    st.session_state.project_ctx = ctx
    current_results = st.session_state.last_results or []
    current_results = [r for r in current_results if r.stage_name != rerun_stage]
    current_results.append(rerun_result)
    order = {name: i for i, (name, _, _) in enumerate(STAGES)}
    current_results.sort(key=lambda r: order.get(r.stage_name, 999))
    st.session_state.last_results = current_results

    if rerun_result.status == StageStatus.PASSED:
        st.success(f"تمت إعادة مرحلة **{rerun_stage}** بنجاح. المراحل الأخرى لم تُشغّل.")
    elif rerun_result.status == StageStatus.FAILED:
        st.error(f"المرحلة **{rerun_stage}** ما زالت متوقفة: {rerun_result.detail}")

    st.rerun()


# زر الاستكمال الرئيسي: يظهر بعد فشل أي مرحلة حتى لو كانت الـSidebar مخفية.
if st.session_state.project_ctx is not None and st.session_state.failed_stage:
    st.divider()
    st.warning(
        f"المشروع متوقف عند مرحلة **{st.session_state.failed_stage}**. "
        "بعد تغيير مفتاح Gemini من الـSidebar، اضغط الزر التالي. "
        "لن يعيد المراحل التي نجحت."
    )
    resume_clicked = st.button(
        f"▶️ استكمال المهمة من {st.session_state.failed_stage}",
        type="primary",
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
        research=ResearchConfig(enabled=False, depth=research_depth),
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
