"""
app.py
=======
واجهة Streamlit الرئيسية لمشروع minds10-script-generator.

3 أقسام:
1) الشريط الجانبي: قائمة المشاريع المحفوظة (Turso) + استكمال مشروع قديم.
2) نموذج مشروع جديد: عنوان/فكرة/سؤال/نص/PDF + مصادر + جمهور + مدة + عينات
   Voice DNA + تفعيل بحث الويب.
3) تشغيل الـ Workflow بالكامل مع عرض تقدم كل مرحلة، وعرض/تنزيل السكريبت
   النهائي.
"""

from __future__ import annotations

import streamlit as st

from config import APP_TITLE, APP_TAGLINE, MIN_DURATION_MINUTES, MAX_DURATION_MINUTES, DEFAULT_DURATION_MINUTES, MAX_SOURCE_CHARS
from core.context import ProjectContext, SourceRef
from core.workflow import run_workflow, STAGE_LABELS_AR, STAGES
from db.project_store import list_projects, load_project, save_project, delete_project
from skills.voice_dna import VoiceDnaSkill
from utils.pdf_utils import extract_pdf_text

st.set_page_config(page_title=APP_TITLE, page_icon="🎬", layout="wide")


def _sidebar():
    st.sidebar.title("📁 المشاريع المحفوظة")
    projects = list_projects()
    if not projects:
        st.sidebar.caption("لا توجد مشاريع محفوظة بعد.")
    for p in projects:
        label = f"{p['title']} — {p['status']}"
        cols = st.sidebar.columns([4, 1])
        if cols[0].button(label, key=f"open_{p['project_id']}", use_container_width=True):
            st.session_state["ctx"] = load_project(p["project_id"])
            st.rerun()
        if cols[1].button("🗑️", key=f"del_{p['project_id']}"):
            delete_project(p["project_id"])
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("➕ مشروع جديد", use_container_width=True):
        st.session_state.pop("ctx", None)
        st.rerun()


def _new_project_form():
    st.header("🎬 " + APP_TITLE)
    st.caption(APP_TAGLINE)

    with st.form("new_project"):
        title = st.text_input("عنوان المشروع", placeholder="مثلاً: قرارك اليوم ممكن يغير مستقبلك المالي")
        input_type = st.selectbox(
            "نوع المادة الخام",
            ["idea", "title", "question", "text", "book"],
            format_func=lambda x: {
                "idea": "فكرة بسيطة", "title": "عنوان فقط", "question": "سؤال",
                "text": "نص موجود", "book": "كتاب/PDF",
            }[x],
        )
        raw_text = st.text_area("المادة الخام (فكرة/سؤال/نص أساسي)", height=150)

        st.subheader("مصادر إضافية (اختياري)")
        urls_raw = st.text_area("روابط (رابط في كل سطر)", height=80)
        pdf_file = st.file_uploader("ملف PDF (كتاب أو مقال طويل)", type=["pdf"])
        pdf_pages = st.text_input("نطاق الصفحات المطلوب من الـ PDF (مثلاً 1-20، اتركه فاضي للكتاب كامل)")

        col1, col2 = st.columns(2)
        with col1:
            audience_description = st.text_input("وصف الجمهور المستهدف", placeholder="مثلاً: شباب 20-30 سنة مهتمين بالتطوير الذاتي")
        with col2:
            duration_minutes = st.slider("مدة الفيديو (دقيقة)", MIN_DURATION_MINUTES, MAX_DURATION_MINUTES, DEFAULT_DURATION_MINUTES)

        allow_web_search = st.checkbox("السماح بالبحث على الويب أثناء مرحلة Research")

        st.subheader("بصمتك الصوتية (Voice DNA) - اختياري")
        voice_samples_raw = st.text_area(
            "الصق عينات من كتاباتك السابقة (سكريبتات قديمة/منشورات/ملاحظات)، افصل بين كل عينة بسطر ---",
            height=120,
        )

        submitted = st.form_submit_button("🚀 ابدأ المشروع", use_container_width=True)

    if submitted:
        ctx = ProjectContext(
            title=title or raw_text[:60] or "مشروع بدون عنوان",
            raw_input_type=input_type,
            raw_input_text=raw_text,
            audience_description=audience_description,
            duration_minutes=duration_minutes,
            allow_web_search=allow_web_search,
        )

        for url in [u.strip() for u in urls_raw.splitlines() if u.strip()]:
            ctx.sources.append(SourceRef(kind="url", label=url, content=""))

        if pdf_file is not None:
            tmp_path = f"/tmp/{pdf_file.name}"
            with open(tmp_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            text, total_pages = extract_pdf_text(tmp_path, pdf_pages)
            ctx.sources.append(
                SourceRef(
                    kind="pdf", label=pdf_file.name,
                    content=text[:MAX_SOURCE_CHARS], pages=pdf_pages or f"1-{total_pages}",
                )
            )

        if voice_samples_raw.strip():
            samples = [s.strip() for s in voice_samples_raw.split("---") if s.strip()]
            with st.spinner("بنحلل بصمتك الصوتية..."):
                ctx.voice_dna_profile = VoiceDnaSkill().extract(samples)

        save_project(ctx)
        st.session_state["ctx"] = ctx
        st.rerun()


def _run_and_show_workflow(ctx: ProjectContext):
    st.header(f"🎬 {ctx.title}")
    st.caption(f"الحالة: {ctx.status} — آخر مرحلة: {STAGE_LABELS_AR.get(ctx.current_stage, ctx.current_stage) or '—'}")

    total = len(STAGES)
    progress = st.progress(len(ctx.completed_stages) / total if total else 0)
    status_box = st.empty()

    if ctx.status != "done":
        if st.button("▶️ شغّل / استكمل الـ Workflow", type="primary"):
            try:
                for stage_name, updated_ctx in run_workflow(ctx, resume=True):
                    ctx = updated_ctx
                    st.session_state["ctx"] = ctx
                    if stage_name != "done":
                        idx = [s for s, _ in STAGES].index(stage_name) + 1
                        progress.progress(idx / total)
                        status_box.info(f"✅ اكتملت مرحلة: {STAGE_LABELS_AR.get(stage_name, stage_name)}")
                st.success("🎉 اكتمل السكريبت النهائي!")
                st.rerun()
            except RuntimeError as e:
                st.error(str(e))
    else:
        st.success("هذا المشروع مكتمل بالفعل.")

    _show_stage_outputs(ctx)


def _show_stage_outputs(ctx: ProjectContext):
    if ctx.final_script:
        st.subheader("📜 السكريبت النهائي")
        st.text_area("Final Script", ctx.final_script, height=400, label_visibility="collapsed")
        st.download_button(
            "⬇️ تنزيل السكريبت", ctx.final_script,
            file_name=f"{ctx.title}_final_script.txt",
        )

    with st.expander("🔍 تفاصيل كل مرحلة (للمراجعة/الـ Debug)"):
        st.write("**فهم الموضوع**", ctx.topic_understanding)
        st.write("**الاستراتيجية**", ctx.strategy)
        st.write("**هيكل الحكاية**", ctx.story_architecture)
        st.write("**الهوك**", ctx.hook_options)
        st.write("**مسودة السكريبت**", ctx.script_draft)
        st.write("**بعد الإنسنة**", ctx.humanized_script)
        st.write("**تقرير Anti-Slop**", ctx.anti_slop_report)
        st.write("**مراجعة الاحتفاظ**", ctx.retention_review)
        st.write("**مراجعة التكرار**", ctx.repetition_review)
        st.write("**بعد تحرير اللهجة المصرية**", ctx.egyptian_edited_script)
        st.write("**فحص اتساق البصمة الصوتية**", ctx.voice_dna_consistency_report)
        st.write("**المراجعة النهائية كمشاهد**", ctx.final_human_review)


def main():
    _sidebar()
    ctx = st.session_state.get("ctx")
    if ctx is None:
        _new_project_form()
    else:
        _run_and_show_workflow(ctx)


if __name__ == "__main__":
    main()
