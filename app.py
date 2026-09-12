"""
app.py
======
نقطة الدخول لواجهة Streamlit.

أهم نقطتين حسب طلب المستخدم مباشرة:

1) مربع اختيار صريح لتفعيل/إيقاف البحث المباشر من الإنترنت.
   - لو المستخدم *لم* يختره → القيمة False → محرك البحث لا يتصل
     بالإنترنت إطلاقًا (راجع engines/research/engine.py).
   - لو اختاره → True → يعمل البحث فعليًا (بحسب دعم الموديل المختار).

2) قائمة اختيار موديل بين Gemini 3.6 Flash و Gemini 3.7 Flash فقط حاليًا،
   مع جعل Gemini 3.6 Flash هو الموديل الافتراضي/الأساسي عند فتح المشروع
   لأول مرة (ما لم يغيّره المستخدم بنفسه).

الواجهة هنا "سميكة بما يكفي لتشتغل" وليست تصميمًا نهائيًا — الهدف إثبات
أن core/model_registry.py و core/context.py و core/orchestrator.py
تتكامل معًا فعليًا، تنفيذًا لقاعدة المشروع: "لا تعتبر المهمة مكتملة
بمجرد إنشاء ملفات — بل عند اتصالها بسير عمل حقيقي".
"""

from __future__ import annotations

import uuid

import streamlit as st

from core.bootstrap import bootstrap
from core.context import ModelSelection, PipelineContext, ResearchConfig, ResearchDepth
from core.model_registry import DEFAULT_MODEL_ID, list_available_models
from core.orchestrator import Orchestrator, StageStatus

st.set_page_config(page_title="Minds10 — مولد السيناريو", layout="wide")
bootstrap()  # تسجيل الموفرين/المحركات/المهارات مرة واحدة عند الإقلاع

if "project_ctx" not in st.session_state:
    st.session_state.project_ctx = None  # PipelineContext الحالي، وليس مصدر الحقيقة الدائم
    # ملاحظة معمارية مهمة (القسم 51): session_state هنا يُستخدم فقط كحالة
    # واجهة مؤقتة أثناء الجلسة. الحفظ الدائم الفعلي (Turso) غير مُفعّل بعد
    # في هذا الإصدار الأولي — انظر db/schema.sql والـ TODO في core/context.py.

st.title("Minds10 — مولد السيناريو")
st.caption("منصة إنتاج سكريبتات YouTube — فهم أولًا، ثم كتابة.")

with st.sidebar:
    st.header("إعدادات المشروع")

    project_name = st.text_input("اسم المشروع", value="مشروع جديد")
    duration = st.number_input("مدة الفيديو (دقيقة)", min_value=1, max_value=180, value=15)
    audience = st.text_input("الجمهور المستهدف", value="")

    st.divider()
    st.subheader("الموديل")

    models = list_available_models()
    model_labels = {m.display_name: m.model_id for m in models}
    # يضمن ظهور Gemini 3.6 Flash كخيار افتراضي أول في القائمة
    ordered_labels = sorted(model_labels.keys(), key=lambda name: model_labels[name] != DEFAULT_MODEL_ID)
    default_index = 0  # DEFAULT_MODEL_ID دائمًا أول عنصر بعد الترتيب أعلاه

    selected_label = st.selectbox("اختر الموديل", ordered_labels, index=default_index)
    selected_model_id = model_labels[selected_label]
    st.caption(f"الموديل المستخدم فعليًا: `{selected_model_id}`")

    st.divider()
    st.subheader("البحث على الويب")

    web_research_enabled = st.checkbox(
        "تفعيل البحث المباشر من الإنترنت",
        value=False,  # افتراضيًا OFF دائمًا — القاعدة 21
        help="لو المربع فاضي: النظام لا يتصل بالإنترنت إطلاقًا ويعتمد فقط "
             "على كلامك والملفات والمصادر اللي انت مديها.",
    )

    research_depth = ResearchDepth.STANDARD
    if web_research_enabled:
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

        selected_model_capabilities = next(m for m in models if m.model_id == selected_model_id).capabilities
        if not selected_model_capabilities.supports_search:
            st.warning(
                f"الموديل '{selected_label}' لا يدعم البحث المباشر. "
                f"اختر موديلًا آخر يدعمه، أو أوقف تفعيل البحث."
            )
    else:
        st.caption("البحث متوقف — لن يحدث أي اتصال بالإنترنت لهذا المشروع.")

    st.divider()
    raw_input = st.text_area("المادة الخام / الفكرة", height=150)

    start_clicked = st.button("ابدأ التوليد", type="primary", use_container_width=True)

if start_clicked:
    ctx = PipelineContext(
        project_id=str(uuid.uuid4()),
        project_name=project_name,
        raw_input=raw_input,
        duration_minutes=int(duration),
        audience=audience or None,
        research=ResearchConfig(enabled=web_research_enabled, depth=research_depth),
        model_selection=ModelSelection(project_default=selected_model_id),
    )
    st.session_state.project_ctx = ctx

    orchestrator = Orchestrator()
    with st.spinner("جاري تشغيل خط الإنتاج..."):
        results = orchestrator.run(ctx)

    st.subheader("حالة المراحل")
    for r in results:
        icon = {"passed": "✅", "failed": "❌", "skipped": "⏭️", "running": "🔄", "pending": "⏳"}[r.status.value]
        st.write(f"{icon} **{r.stage_name}** — {r.detail}")

    if ctx.draft_script:
        st.subheader("المسودة الأولى")
        st.text_area("draft_script", value=ctx.draft_script, height=300, label_visibility="collapsed")

ctx = st.session_state.project_ctx
if ctx and not start_clicked:
    st.info(f"مشروع محمّل في الجلسة: **{ctx.project_name}** — البحث: "
            f"{'مفعّل' if ctx.research.enabled else 'متوقف'} — "
            f"الموديل: `{ctx.model_selection.project_default}`")
