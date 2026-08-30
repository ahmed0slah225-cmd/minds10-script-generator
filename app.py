# -*- coding: utf-8 -*-
"""
Minds10 Script Generator
تطبيق Streamlit لتوليد سكريبتات يوتيوب احترافية بالعامية المصرية،
مع بحث تلقائي على الإنترنت (Grounding with Google Search) عشان يجيب
أدلة وأبحاث ودراسات حقيقية أثناء الكتابة.

ملاحظة: كل التعليمات (System Instruction) وبناء الـ Prompt موجودة في
engine/prompts.py - الملف ده بيركز على الواجهة (UI) بس.
"""

import io
import re
import time
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from engine.prompts import (
    WORDS_PER_MINUTE,
    build_system_instruction,
    build_user_prompt,
)


# ----------------------------- إعدادات عامة ----------------------------- #

st.set_page_config(
    page_title="Minds10 - مولّد سكريبتات يوتيوب",
    page_icon="🎬",
    layout="wide",
)

# ترتيب الموديلات: الأحدث والأقوى أولًا، مع خيار اقتصادي احتياطي في الآخر
MODEL_OPTIONS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",  # خيار احتياطي أرخص لو حصل ضغط على موديلات الـ 3.x
]


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


def generate_script(api_key: str, model: str, topic: str, audience: str,
                     tone: str, notes: str, duration_min: int, use_grounding: bool):
    client = genai.Client(api_key=api_key)

    tools = [types.Tool(google_search=types.GoogleSearch())] if use_grounding else None
    config = types.GenerateContentConfig(
        system_instruction=build_system_instruction(use_grounding),
        tools=tools,
        max_output_tokens=16000,
    )

    prompt = build_user_prompt(topic, audience, tone, notes, duration_min, use_grounding)

    max_attempts = 3
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
        except genai_errors.ServerError as e:
            last_error = e
            if getattr(e, "code", None) == 503 and attempt < max_attempts:
                time.sleep(5 * attempt)  # 5 ثواني، بعدين 10
                continue
            raise
    raise last_error


def extract_sources(response):
    """يحاول يطلع المصادر والاستعلامات اللي البحث استخدمها، لو موجودة."""
    sources = []
    queries = []
    try:
        candidate = response.candidates[0]
        gm = getattr(candidate, "grounding_metadata", None)
        if gm:
            queries = list(getattr(gm, "web_search_queries", None) or [])
            chunks = getattr(gm, "grounding_chunks", None) or []
            for chunk in chunks:
                web = getattr(chunk, "web", None)
                if web and getattr(web, "uri", None):
                    sources.append({
                        "title": getattr(web, "title", None) or web.uri,
                        "uri": web.uri,
                    })
    except Exception:
        pass
    return queries, sources


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
st.caption("سكريبتات بالعامية المصرية، مدعومة بأدلة وأبحاث حقيقية من الإنترنت، جاهزة للتسجيل.")

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

    model = st.selectbox("الموديل", options=MODEL_OPTIONS, index=0)

    duration_min = st.slider("مدة الفيديو (دقايق)", min_value=10, max_value=45, value=30, step=5)
    st.caption(f"هيتكتب تقريبًا {duration_min * WORDS_PER_MINUTE:,} كلمة")

    use_grounding = st.checkbox(
        "🔎 فعّل البحث التلقائي من الإنترنت (Grounding)",
        value=False,
        help=(
            "الخاصية دي مجانية ومدمجة جوه Gemini API (مش محتاجة مفتاح API تاني منفصل)، "
            "لكنها محتاجة Billing مفعّل على مشروعك في Google AI Studio عشان تشتغل بشكل "
            "موثوق، وإلا هتقابل خطأ 429 (تجاوز الحصة). لو مفعّلش Billing، سيبها مطفية "
            "وهيكتب السكريبت من غير بحث حي بس هيفضل كويس."
        ),
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

generate_clicked = st.button("🚀 اكتب السكريبت", type="primary", use_container_width=True)

if generate_clicked:
    api_key = get_api_key()
    if not api_key:
        st.error("محتاج تحط مفتاح Gemini API الأول (في الشريط الجانبي أو في Secrets).")
    elif not topic.strip():
        st.error("اكتب موضوع الفيديو الأول.")
    else:
        with st.spinner("بيبحث ويكتب... الموضوع بياخد شوية وقت عشان السكريبت طويل 🎬"):
            try:
                response = generate_script(api_key, model, topic, audience, tone, notes, duration_min, use_grounding)
                script_text = response.text or ""
            except genai_errors.ServerError as e:
                if getattr(e, "code", None) == 503:
                    st.error(
                        "🔧 سيرفرات Gemini مزنوقة مؤقتًا بسبب ضغط استخدام كبير (مش مشكلة "
                        "من عندك خالص). جرب تاني بعد شوية، أو غيّر الموديل من الشريط الجانبي "
                        "لموديل تاني زي gemini-3.6-flash."
                    )
                else:
                    st.error(f"حصل خطأ من سيرفر الـ API (كود {getattr(e, 'code', '؟')}): {e}")
                script_text = ""
            except genai_errors.APIError as e:
                if getattr(e, "code", None) == 429:
                    st.error(
                        "⏳ وصلت لحد الحصة المجانية (Quota) بتاعة مفتاح الـ Gemini API دلوقتي.\n\n"
                        "**الأسباب الشائعة:** البحث التلقائي (Grounding) محتاج Billing مفعّل "
                        "على مشروعك في Google AI Studio عشان يشتغل بثبات، حتى لو المفتاح جديد "
                        "أو الكوتة اليومية اترجعت اتصفرت.\n\n"
                        "**تقدر:**\n"
                        "- تطفي خيار \"فعّل البحث التلقائي\" من الشريط الجانبي والسكريبت هيتكتب "
                        "من غير مشاكل كوتة.\n"
                        "- تتابع استهلاكك من [صفحة الحصص](https://ai.dev/rate-limit).\n"
                        "- تفعّل الفوترة (Billing) على مشروعك في Google AI Studio لو عايز "
                        "البحث التلقائي يشتغل بشكل ثابت."
                    )
                elif getattr(e, "code", None) == 404:
                    st.error(
                        "🚫 النموذج ده مش متاح للمفتاح بتاعك (اتوقف أو مش موجود لحسابات جديدة).\n\n"
                        "اختار موديل تاني من قايمة \"الموديل\" في الشريط الجانبي "
                        "(زي gemini-3.7-flash أو gemini-3.6-flash) وجرب تاني."
                    )
                else:
                    st.error(f"حصل خطأ من الـ API (كود {getattr(e, 'code', '؟')}): {e}")
                script_text = ""
            except Exception as e:
                st.error(f"حصل خطأ أثناء التوليد: {e}")
                script_text = ""

        if script_text:
            st.session_state["last_script"] = script_text
            st.session_state["last_topic"] = topic
            st.session_state["last_response"] = response

if st.session_state.get("last_script"):
    script_text = st.session_state["last_script"]
    topic_saved = st.session_state.get("last_topic", "سكريبت")

    st.divider()
    wc = word_count(script_text)
    est_minutes = round(wc / WORDS_PER_MINUTE, 1)
    st.subheader("📝 السكريبت")
    st.caption(f"عدد الكلمات: {wc:,} — المدة التقريبية: {est_minutes} دقيقة")

    st.markdown(script_text)

    queries, sources = extract_sources(st.session_state.get("last_response"))
    if queries or sources:
        with st.expander("🔎 المصادر والبحث اللي اتعمل"):
            if queries:
                st.markdown("**استعلامات البحث:**")
                for q in queries:
                    st.markdown(f"- {q}")
            if sources:
                st.markdown("**المصادر:**")
                for s in sources:
                    st.markdown(f"- [{s['title']}]({s['uri']})")

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
