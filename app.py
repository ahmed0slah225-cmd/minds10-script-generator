# -*- coding: utf-8 -*-
"""
Minds10 Script Generator
تطبيق Streamlit لتوليد سكريبتات يوتيوب احترافية بالعامية المصرية، عن
طريق Pipeline من 13 عقل متخصص (تحليل، أفكار، بحث، هوك، نقد، كتابة،
احتفاظ بالجمهور، مراجعة تكرارات، تحرير لغوي، مراجعة أخيرة)، مع ذاكرة
دائمة (Turso) لتجنب تكرار نفس الهوكات في المرات الجاية.
"""

import io
import re
from datetime import datetime

import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import database
import pipeline
from pipeline import AGENT_ORDER, AGENT_TITLES, DEFAULT_PROMPTS


# ----------------------------- إعدادات عامة ----------------------------- #

st.set_page_config(
    page_title="Minds10 - مولّد سكريبتات يوتيوب",
    page_icon="🎬",
    layout="wide",
)

WORDS_PER_MINUTE = pipeline.WORDS_PER_MINUTE

database.init_db()


# ----------------------------- دوال مساعدة ----------------------------- #

def get_secret_api_key() -> str:
    """يجيب مفتاح الـ API من Secrets بتاعة Streamlit لو موجود، وإلا يرجع سلسلة فاضية."""
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


def get_api_key() -> str:
    """يجيب مفتاح الـ API من secrets الأول، ولو مش موجود يستخدم اللي المستخدم كتبه يدوي."""
    return get_secret_api_key() or st.session_state.get("manual_api_key", "")


def set_paragraph_rtl(paragraph):
    """يخلي الفقرة تتجه من اليمين لليسار في ملف الـ Word."""
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pPr = paragraph._p.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    bidi.set(qn("w:val"), "1")
    pPr.append(bidi)


def build_docx(script_text: str, topic: str) -> io.BytesIO:
    doc = Document()

    title = doc.add_heading(f"سكريبت: {topic}", level=0)
    set_paragraph_rtl(title)

    for raw_line in script_text.split("\n"):
        line = raw_line.strip()
        if not line:
            doc.add_paragraph()
            continue

        if line.startswith("## "):
            p = doc.add_heading(line.replace("## ", "").strip(), level=2)
        elif line.startswith("# "):
            p = doc.add_heading(line.replace("# ", "").strip(), level=1)
        else:
            p = doc.add_paragraph(line)

        set_paragraph_rtl(p)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


# ----------------------------- واجهة المستخدم ----------------------------- #

st.title("🎬 Minds10 — مولّد سكريبتات يوتيوب")
st.caption("13 عقل متخصص بيشتغلوا مع بعض عشان يطلعوا سكريبت كامل بالعامية المصرية، بذاكرة دائمة بتمنع تكرار نفس الهوكات.")

with st.sidebar:
    st.header("⚙️ الإعدادات")

    if not get_secret_api_key():
        st.text_input(
            "مفتاح Gemini API",
            type="password",
            key="manual_api_key",
            help="لو التطبيق شغال على Streamlit Cloud، حط المفتاح في Secrets بدل ما تكتبه هنا.",
        )
    else:
        st.success("مفتاح الـ API متظبط من إعدادات السيرفر ✅")

    model = st.selectbox(
        "الموديل",
        options=["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"],
        index=0,
    )

    duration_min = st.slider("مدة الفيديو (دقايق)", min_value=10, max_value=45, value=30, step=5)
    st.caption(f"هيتكتب تقريبًا {duration_min * WORDS_PER_MINUTE:,} كلمة")

    use_free_research = st.checkbox(
        "🆓 فعّل البحث المجاني (DuckDuckGo) في مرحلتي البحث",
        value=True,
        help=(
            "بيشغّل عقل \"باحث المعلومات\" وعقل \"مقالات منشورة عن الموضوع\" "
            "بحث حقيقي مجاني من غير أي فلوس أو Billing. باقي الـ11 عقل بيشتغلوا "
            "بمعرفة النموذج بس، من غير أي بحث، فمفيش أي حاجة في البايبلاين كله "
            "محتاجة Billing."
        ),
    )

    st.divider()
    if database.is_configured():
        st.success("🗄️ الذاكرة الدائمة (Turso): متصلة ✅")
    else:
        st.warning(
            "🗄️ الذاكرة الدائمة (Turso) مش متصلة - السكريبتات هتتكتب عادي "
            "بس من غير حفظ للهوكات السابقة لمنع التكرار بين الجلسات."
        )

    with st.expander("🧠 تخصيص تعليمات العقول الـ13 (اختياري ومتقدم)"):
        st.caption("كل عقل ليه تعليمات افتراضية جاهزة تقدر تعدلها هنا لو عايز تغيّر سلوكه.")
        for key in AGENT_ORDER:
            st.text_area(
                AGENT_TITLES[key],
                value=DEFAULT_PROMPTS[key],
                key=f"agent_prompt_{key}",
                height=120,
            )

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_area(
        "📌 موضوع الفيديو",
        placeholder="مثلاً: إزاي عقلك بيخدعك في القرارات اليومية بدون ما تحس",
        height=90,
    )
    notes = st.text_area(
        "🗂️ معلومات أو مصادر عندك (اختياري)",
        placeholder="أي نقاط أو روابط أو أفكار عايز تتضاف للسكريبت",
        height=100,
    )

with col2:
    audience = st.text_input("👥 الجمهور المستهدف (اختياري)", placeholder="مثلاً: شباب 18-30")
    tone = st.selectbox(
        "🎭 نبرة الفيديو",
        options=["تشويقي / إثارة فضول", "تعليمي مبسّط", "قصصي حكواتي", "تحليلي عميق"],
    )

generate_clicked = st.button("🚀 اكتب السكريبت عبر الـ13 عقل", type="primary", use_container_width=True)

if generate_clicked:
    api_key = get_api_key()
    if not api_key:
        st.error("محتاج تحط مفتاح Gemini API الأول (في الشريط الجانبي أو في Secrets).")
    elif not topic.strip():
        st.error("اكتب موضوع الفيديو الأول.")
    else:
        agent_prompts = {
            key: st.session_state.get(f"agent_prompt_{key}", DEFAULT_PROMPTS[key])
            for key in AGENT_ORDER
        }
        previous_hooks = database.get_previous_hooks(topic)

        status = st.status("🧠 بدء توليد السكريبت عبر 13 عقل متخصص...", expanded=True)

        def progress_callback(key, title):
            status.write(f"▶️ {title}")

        try:
            result = pipeline.run_pipeline(
                api_key=api_key, model=model, topic=topic, audience=audience,
                tone=tone, notes=notes, duration_min=duration_min,
                use_free_research=use_free_research, previous_hooks=previous_hooks,
                agent_prompts=agent_prompts, progress_callback=progress_callback,
            )
            status.update(label="✅ خلصت كل العقول الـ13!", state="complete")

            st.session_state["last_script"] = result["final_script"]
            st.session_state["last_topic"] = topic
            st.session_state["last_review_notes"] = result["review_notes"]
            st.session_state["last_sources"] = result["sources"]
            st.session_state["last_stage_outputs"] = result["stage_outputs"]

            database.save_hook(topic, result["hook_text"])

        except pipeline.genai_errors.ServerError as e:
            status.update(label="❌ حصل خطأ من سيرفر Gemini", state="error")
            if getattr(e, "code", None) == 503:
                st.error(
                    "🔧 سيرفرات Gemini مزنوقة مؤقتًا بسبب ضغط استخدام كبير (مش مشكلة "
                    "من عندك خالص). جرب تاني بعد شوية، أو غيّر الموديل من الشريط الجانبي "
                    "لموديل تاني زي gemini-3.6-flash."
                )
            else:
                st.error(f"حصل خطأ من سيرفر الـ API (كود {getattr(e, 'code', '؟')}): {e}")
        except pipeline.genai_errors.APIError as e:
            status.update(label="❌ حصل خطأ من الـ API", state="error")
            if getattr(e, "code", None) == 429:
                st.error(
                    "⏳ وصلت لحد الحصة المجانية (Quota) بتاعة مفتاح الـ Gemini API دلوقتي.\n\n"
                    "13 نداء API لكل سكريبت بيستهلكوا الحصة اليومية بسرعة أكبر من نداء "
                    "واحد. تقدر تستنى الكوتة تترجع تتصفر (كل يوم تقريبًا)، أو تفعّل "
                    "الفوترة (Billing) على مشروعك في [Google AI Studio](https://aistudio.google.com) "
                    "عشان تاخد حصة أكبر بكتير."
                )
            elif getattr(e, "code", None) == 404:
                st.error(
                    "🚫 النموذج ده مش متاح للمفتاح بتاعك. اختار موديل تاني من الشريط "
                    "الجانبي (زي gemini-3.7-flash أو gemini-3.6-flash) وجرب تاني."
                )
            else:
                st.error(f"حصل خطأ من الـ API (كود {getattr(e, 'code', '؟')}): {e}")
        except Exception as e:
            status.update(label="❌ حصل خطأ غير متوقع", state="error")
            st.error(f"حصل خطأ أثناء التوليد: {e}")

if st.session_state.get("last_script"):
    script_text = st.session_state["last_script"]
    topic_saved = st.session_state.get("last_topic", "سكريبت")

    st.divider()
    wc = word_count(script_text)
    est_minutes = round(wc / WORDS_PER_MINUTE, 1)
    st.subheader("📝 السكريبت النهائي")
    st.caption(f"عدد الكلمات: {wc:,} — المدة التقريبية: {est_minutes} دقيقة")

    st.markdown(script_text)

    review_notes = st.session_state.get("last_review_notes", "")
    if review_notes:
        with st.expander("🔍 ملاحظات المراجعة النهائية (عقل رقم 13)"):
            st.markdown(review_notes)

    sources = st.session_state.get("last_sources", [])
    if sources:
        with st.expander("🔎 المصادر اللي اتلقت (بحث مجاني - DuckDuckGo)"):
            seen = set()
            for r in sources:
                url = r.get("href") or r.get("url") or ""
                if url in seen:
                    continue
                seen.add(url)
                title = r.get("title") or url or "مصدر"
                if url:
                    st.markdown(f"- [{title}]({url})")
                else:
                    st.markdown(f"- {title}")

    stage_outputs = st.session_state.get("last_stage_outputs", {})
    if stage_outputs:
        with st.expander("🧠 شوف مخرجات كل عقل بالتفصيل (للفضوليين)"):
            for key in AGENT_ORDER:
                st.markdown(f"**{AGENT_TITLES[key]}**")
                st.text(stage_outputs.get(key, ""))
                st.markdown("---")

    st.divider()
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button(
            "⬇️ تحميل كـ TXT",
            data=script_text.encode("utf-8"),
            file_name=f"{topic_saved[:40] or 'script'}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dcol2:
        docx_buffer = build_docx(script_text, topic_saved or "سكريبت")
        st.download_button(
            "⬇️ تحميل كـ Word (docx)",
            data=docx_buffer,
            file_name=f"{topic_saved[:40] or 'script'}_{datetime.now().strftime('%Y%m%d')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
