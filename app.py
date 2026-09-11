from __future__ import annotations
import json
import streamlit as st

from config import APP_TITLE, APP_TAGLINE, MIN_DURATION_MINUTES, MAX_DURATION_MINUTES, AppConfig
from core.models import Project, Source, PipelineState, new_id
from core.documents import extract_pdf_pages, select_page_range, fetch_url
from core.gemini_client import GeminiClient
from core.serialization import state_payload
from engines.pipeline import Pipeline
from engines.voice import VoiceEngine
from persistence.db import Database

st.set_page_config(page_title=APP_TITLE, page_icon="🎬", layout="wide")


def init():
    st.session_state.setdefault("db", Database())
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("active_project", None)
    st.session_state.setdefault("state", None)


def css():
    st.markdown("""<style>
    .block-container{padding-top:1.2rem;max-width:1400px}
    .m-card{padding:1rem 1.1rem;border:1px solid #2a2f3a;border-radius:14px;background:#161a22;margin-bottom:.8rem}
    .muted{color:#9ca3af;font-size:.92rem}
    .stage{display:inline-block;padding:.2rem .55rem;border-radius:999px;background:#252a36}
    </style>""", unsafe_allow_html=True)


def save_state(state):
    db = st.session_state.db
    db.upsert_project(state.project)
    db.save_stage(state.project.id, "snapshot", state_payload(state))


def restore_project(project_id: str):
    row = st.session_state.db.latest_stage_payload(project_id)
    if not row:
        return None
    payload = json.loads(row[1])
    p = payload.get("project", {})
    project = Project(**p)
    state = PipelineState(**{
        "project": project,
        "raw_input": payload.get("raw_input", project.request),
        "sources": [Source(**x) for x in payload.get("sources", [])],
        "topic": payload.get("topic", {}), "research": payload.get("research", {}),
        "knowledge": payload.get("knowledge", {}), "audience": payload.get("audience", {}),
        "strategy": payload.get("strategy", {}), "story": payload.get("story", {}),
        "retention": payload.get("retention", {}), "hook": payload.get("hook", {}),
        "script": payload.get("script", ""), "humanized_script": payload.get("humanized_script", ""),
        "anti_slop": payload.get("anti_slop", {}), "retention_review": payload.get("retention_review", {}),
        "repetition_review": payload.get("repetition_review", {}), "egyptian_edit": payload.get("egyptian_edit", {}),
        "voice_dna": payload.get("voice_dna", {}), "final_review": payload.get("final_review", {}),
        "final_script": payload.get("final_script", ""), "citations": payload.get("citations", []),
        "stage_outputs": payload.get("stage_outputs", {}),
    })
    return state


def create_project(title, request, duration, audience):
    project = Project(id=new_id(), title=title, request=request, duration_minutes=duration, audience=audience)
    state = PipelineState(project=project, raw_input=request)
    st.session_state.active_project = project.id
    st.session_state.state = state
    st.session_state.page = "Workspace"
    save_state(state)


def sidebar():
    with st.sidebar:
        st.title("Minds10")
        st.caption("Content Intelligence Studio")
        for item in ["Dashboard", "Projects", "Voice DNA", "Settings"]:
            if st.button(item, use_container_width=True, type="secondary" if st.session_state.page != item else "primary"):
                st.session_state.page = item
                st.rerun()
        st.divider()
        st.caption("Workflow")
        st.caption("فهم → بحث → معرفة → استراتيجية → قصة → احتفاظ → Hook → كتابة → Humanize → Reviews → تحرير")


def dashboard():
    st.title("🎬 Minds10 Script Studio")
    st.write(APP_TAGLINE)
    c1,c2,c3 = st.columns(3)
    projects = st.session_state.db.list_projects()
    c1.metric("Projects", len(projects))
    c2.metric("Skills", 9)
    c3.metric("Storage", "Turso / SQLite")
    st.divider()
    with st.form("new_project"):
        title = st.text_input("اسم المشروع", placeholder="قرارك اليوم ممكن يغير مستقبلك المالي")
        request = st.text_area("المادة الخام / الطلب", height=180, placeholder="اكتب الفكرة، السؤال، الملاحظات، أو النص الذي ستبدأ منه")
        a,b = st.columns(2)
        duration = a.slider("مدة الفيديو (دقيقة)", MIN_DURATION_MINUTES, MAX_DURATION_MINUTES, 10)
        audience = b.text_input("الجمهور", value="مشاهد مصري مهتم بالموضوع، مبتدئ نسبيًا")
        submitted = st.form_submit_button("ابدأ المشروع", type="primary", use_container_width=True)
        if submitted:
            if not title.strip() or not request.strip():
                st.error("اكتب اسم المشروع والمادة الخام أولًا.")
            else:
                create_project(title.strip(), request.strip(), duration, audience.strip())
                st.rerun()


def projects_page():
    st.title("المشاريع")
    rows = st.session_state.db.list_projects()
    if not rows:
        st.info("لسه مفيش مشاريع محفوظة.")
        return
    for row in rows:
        with st.container(border=True):
            a,b,c = st.columns([4,2,1])
            a.subheader(row[1])
            a.caption(f"المرحلة: {row[2]} · آخر تحديث: {row[3]}")
            if c.button("فتح", key=f"open_{row[0]}"):
                restored = restore_project(row[0])
                st.session_state.active_project = row[0]
                st.session_state.page = "Workspace"
                st.session_state.state = restored or PipelineState(project=Project(id=row[0], title=row[1], request="", duration_minutes=10), raw_input="")
                st.rerun()


def workspace():
    state = st.session_state.state
    if not state:
        st.info("أنشئ مشروع من Dashboard.")
        return
    st.title(state.project.title)
    left,right = st.columns([2.8,1])
    with left:
        st.markdown(f"**المطلوب:** {state.raw_input or state.project.request}")
        st.markdown(f"`{state.project.duration_minutes} دقيقة` · `{state.project.audience}`")
    with right:
        st.metric("Current stage", state.project.current_stage)
    tabs = st.tabs(["Sources", "Voice DNA", "Run Workflow", "Outputs"])
    with tabs[0]:
        st.subheader("مصادر المشروع")
        url = st.text_input("إضافة رابط")
        if st.button("جلب الرابط") and url:
            try:
                title, text = fetch_url(url)
                src = Source(id=new_id(), project_id=state.project.id, kind="url", title=title, locator=url, content=text[:100000])
                state.sources.append(src); st.session_state.db.add_source(src)
                st.success("تمت إضافة المصدر.")
            except Exception as e:
                st.error(f"تعذر جلب الرابط: {e}")
        pdf = st.file_uploader("رفع PDF نصي", type=["pdf"])
        if pdf:
            start,end = st.slider("نطاق الصفحات", 1, 500, (1, min(20, 500)), key="pdf_range")
            if st.button("استخراج النطاق"):
                try:
                    pages = extract_pdf_pages(pdf.getvalue())
                    picked = select_page_range(pages, start, end)
                    content = "\n\n".join([f"[صفحة {p['page']}]\n{p['text']}" for p in picked])
                    src = Source(id=new_id(), project_id=state.project.id, kind="pdf", title=pdf.name, locator=f"pages:{start}-{end}", content=content,
                                 metadata={"page_start":start,"page_end":end,"page_count":len(pages)})
                    state.sources.append(src); st.session_state.db.add_source(src)
                    state.raw_input += f"\n\n[مادة PDF: {pdf.name}، الصفحات {start}-{end}]\n{content[:50000]}"
                    st.success(f"تم استخراج {len(picked)} صفحة.")
                except Exception as e:
                    st.error(f"تعذر قراءة PDF: {e}")
        for s in state.sources:
            st.markdown(f"- **{s.title}** · `{s.kind}` · `{s.locator}`")
    with tabs[1]:
        st.subheader("Voice DNA")
        samples_text = st.text_area("الصق عينات من كتابتك السابقة", height=220, help="كل عينة افصلها بسطر ---")
        if st.button("ابنِ Voice DNA"):
            samples = [x.strip() for x in samples_text.split("---") if x.strip()]
            if not samples: st.warning("أضف عينات أولًا.")
            else:
                try:
                    ai = GeminiClient(model=st.session_state.get("model", None))
                    state.voice_dna = VoiceEngine(ai).build_profile(samples)
                    st.success("تم بناء Voice DNA.")
                    st.json(state.voice_dna)
                except Exception as e: st.error(str(e))
        elif state.voice_dna:
            st.json(state.voice_dna)
    with tabs[2]:
        st.subheader("شغّل الـProfessional Workflow")
        use_web = st.toggle("استخدم Google Search أثناء البحث", value=True)
        if st.button("تشغيل من البداية", type="primary", use_container_width=True):
            try:
                ai = GeminiClient(web_research=use_web)
                pipe = Pipeline(ai)
                bar = st.progress(0)
                label = st.empty()
                def progress(p, stage):
                    bar.progress(p); label.info(f"يعمل الآن: {stage}")
                pipe.run(state, use_web=use_web, progress=progress, on_stage=lambda s, _: save_state(s))
                save_state(state)
                st.success("خلص الـworkflow وتم حفظ المشروع.")
            except Exception as e:
                st.exception(e)
    with tabs[3]:
        st.subheader("المخرجات")
        if state.final_script:
            st.download_button("تحميل السكريبت TXT", state.final_script, file_name=f"{state.project.title}.txt")
            st.text_area("Final Script", state.final_script, height=600)
        else:
            st.info("شغّل الـworkflow أولًا.")
        with st.expander("Stage data"):
            st.json(state.stage_outputs)


def voice_page():
    st.title("Voice DNA")
    st.write("التحليل الأسلوبي محفوظ كبيانات منظمة ويمكن تمريره إلى Hook / Story / Script / Humanization / Final Edit.")


def settings():
    st.title("Settings")
    st.write("المفاتيح السرية تُقرأ من Streamlit Secrets أو متغيرات البيئة، وليس من GitHub.")
    st.code("GEMINI_API_KEY = \"...\"\nGEMINI_MODEL = \"gemini-2.5-flash\"\nTURSO_DATABASE_URL = \"...\"\nTURSO_AUTH_TOKEN = \"...\"\nENABLE_WEB_RESEARCH = \"true\"")

init(); css(); sidebar()
page = st.session_state.page
if page == "Dashboard": dashboard()
elif page == "Projects": projects_page()
elif page == "Workspace": workspace()
elif page == "Voice DNA": voice_page()
elif page == "Settings": settings()
