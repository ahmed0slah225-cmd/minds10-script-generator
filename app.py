# -*- coding: utf-8 -*-
"""
Minds10 Script Generator
تطبيق Streamlit لتوليد سكريبتات يوتيوب احترافية بالعامية المصرية،
مع بحث تلقائي على الإنترنت (Grounding with Google Search) عشان يجيب
أدلة وأبحاث ودراسات حقيقية أثناء الكتابة.
"""

import io
import re
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ----------------------------- إعدادات عامة ----------------------------- #

st.set_page_config(
    page_title="Minds10 - مولّد سكريبتات يوتيوب",
    page_icon="🎬",
    layout="wide",
)

WORDS_PER_MINUTE = 145  # متوسط سرعة الكلام بالعامية المصرية في الفويس أوفر
DEFAULT_MODEL = "gemini-3.7-flash"  # ممكن تغيّره لـ gemini-3.6-flash أو gemini-2.5-flash لو حابب


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


def build_system_instruction() -> str:
    return """
انت كاتب سكريبتات يوتيوب محترف ومتخصص في المحتوى العربي، وشغلك إنك تكتب
سكريبتات فيديوهات طويلة (حوالي 30 دقيقة) بالعامية المصرية البسيطة والسهلة،
موجهة لقناة اسمها Minds10.

القواعد اللي لازم تتبعها بالحرف:

1. الهوك (Hook): أول 10-15 ثانية لازم تكون قوية جدًا وتخلي المشاهد يحس إنه
   لازم يكمل، من غير مقدمات مملة زي "في الفيديو ده هنتكلم عن...".
2. المقدمة: قصيرة، تربط الهوك بموضوع الفيديو، وتدي وعد واضح للمشاهد
   بإيه اللي هياخده لو كمّل للآخر.
3. المحتوى الأساسي: قسّمه لأجزاء واضحة، كل جزء فيه فكرة واحدة رئيسية،
   وادعم كل فكرة بدليل أو رقم أو دراسة أو بحث حقيقي لو لقيت مصدر موثوق
   بالبحث على الإنترنت. لو مش لاقي رقم أو دراسة دقيقة، متخترعش أرقام
   أو أسماء دراسات وهمية - اتكلم بشكل عام بدون ما تدّعي وجود مصدر معين.
4. القصص: حط قصة حقيقية (لو لقيتها بالبحث) أو قصة تخيلية واقعية توضح
   الفكرة، بشرط تكون قصيرة ومرتبطة بموضوع الفيديو مباشرة.
5. اللغة: عامية مصرية بسيطة جدًا، زي ما بتتكلم مع صاحبك، من غير فصحى
   تقيلة ومن غير مصطلحات معقدة إلا لو لازم تشرحها بشكل مبسط فورًا.
6. الإيقاع: خلي كل فقرة قصيرة، وكل شوية حط سؤال أو جملة تشد الانتباه
   تاني (زي "بس اللي هيصدمك إن..." أو "وده مش كل حاجة...") عشان محدش
   يمل ويسيب الفيديو من نصه.
7. من غير حشو خالص: كل جملة لازم تضيف معلومة أو مشاعر أو تشويق،
   ممنوع الكلام الفاضي أو التكرار.
8. الخاتمة: لخّص الفكرة الرئيسية في جملتين، واقفل بدعوة واضحة للفعل
   (زي اشتراك أو تعليق) بطريقة طبيعية مش مفتعلة.
9. اكتب السكريبت بعناوين واضحة بصيغة Markdown كالتالي:
   # الهوك
   # المقدمة
   ## [اسم الجزء الأول]
   ## [اسم الجزء الثاني]
   ... (وهكذا لكل الأجزاء)
   # الخاتمة
10. لو استخدمت بحث الإنترنت، اذكر مصدر المعلومة بشكل طبيعي جوه الكلام
    (زي "دراسة من جامعة كذا لقت إن..." أو "موقع كذا نشر إحصائية...")
    من غير ما تحط روابط أو أقواس مرجعية جوه النص.
""".strip()


def build_user_prompt(topic: str, audience: str, tone: str, notes: str, duration_min: int) -> str:
    target_words = int(duration_min * WORDS_PER_MINUTE)
    lines = [
        f"اكتب سكريبت فيديو يوتيوب كامل عن الموضوع ده: {topic.strip()}",
        f"مدة الفيديو المستهدفة: {duration_min} دقيقة تقريبًا، يعني السكريبت لازم يكون حوالي "
        f"{target_words} كلمة (زائد أو ناقص 10%)، من غير حشو - لو الموضوع مش هيكفي العدد ده "
        f"بمحتوى حقيقي، وسّع بالبحث عن جوانب إضافية للموضوع بدل ما تكرر كلام.",
        f"نبرة الفيديو: {tone}.",
    ]
    if audience.strip():
        lines.append(f"الجمهور المستهدف: {audience.strip()}.")
    if notes.strip():
        lines.append(
            "معلومات أو مصادر إضافية من صاحب القناة، استخدمها في السكريبت ولو محتاج "
            f"وسّعها بالبحث: {notes.strip()}"
        )
    lines.append(
        "دوّر على الإنترنت على أحدث الأدلة والأرقام والدراسات المتعلقة بالموضوع ده "
        "قبل ما تكتب، واستخدمها في الأجزاء المناسبة بشكل طبيعي."
    )
    return "\n".join(lines)


def generate_script(api_key: str, model: str, topic: str, audience: str,
                     tone: str, notes: str, duration_min: int):
    client = genai.Client(api_key=api_key)

    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        system_instruction=build_system_instruction(),
        tools=[grounding_tool],
        max_output_tokens=16000,
    )

    prompt = build_user_prompt(topic, audience, tone, notes, duration_min)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config,
    )
    return response


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

    model = st.selectbox(
        "الموديل",
        options=["gemini-3.7-flash", "gemini-3.6-flash", "gemini-2.5-flash"],
        index=0,
    )

    duration_min = st.slider("مدة الفيديو (دقايق)", min_value=10, max_value=45, value=30, step=5)
    st.caption(f"هيتكتب تقريبًا {duration_min * WORDS_PER_MINUTE:,} كلمة")

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
                response = generate_script(api_key, model, topic, audience, tone, notes, duration_min)
                script_text = response.text or ""
            except genai_errors.APIError as e:
                if getattr(e, "code", None) == 429:
                    st.error(
                        "⏳ وصلت لحد الحصة المجانية (Quota) بتاعة مفتاح الـ Gemini API دلوقتي.\n\n"
                        "**الأسباب الشائعة:** البحث التلقائي (Grounding) وسط توليد سكريبت طويل "
                        "بياخد من الكوتة بسرعة، خصوصًا لو مفعلش عندك Billing على المشروع في "
                        "Google AI Studio.\n\n"
                        "**تقدر:**\n"
                        "- تستنى وتجرب تاني بعد شوية (الكوتة اليومية بترجع تتصفر تلقائيًا).\n"
                        "- تتابع استهلاكك من [صفحة الحصص](https://ai.dev/rate-limit).\n"
                        "- تفعّل الفوترة (Billing) على مشروعك في Google AI Studio عشان تاخد "
                        "حصة أكبر بكتير لو هتستخدم التطبيق بشكل مستمر."
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
