import json
import os
import re
import time
from pathlib import Path

import streamlit as st
from google import genai

BASE_DIR = Path(__file__).parent
STYLE_FILE = BASE_DIR / "00_قواعد_الاسلوب.txt"
PROMPT_FILES = [
    BASE_DIR / "01_العقل_الاول_فهم_الحكاية.txt",
    BASE_DIR / "02_العقل_الثاني_هندسة_الاجزاء.txt",
    BASE_DIR / "03_العقل_الثالث_المواقف_والحكايات.txt",
    BASE_DIR / "04_العقل_الرابع_كتابة_المسودة.txt",
    BASE_DIR / "05_العقل_الخامس_تظبيط_الاسلوب.txt",
    BASE_DIR / "06_العقل_السادس_الاخراج_النهائي.txt",
]

st.set_page_config(
    page_title="غرفة كتابة السكريبت - 6 عقول",
    page_icon="🧠",
    layout="wide",
)

st.title("غرفة كتابة السكريبت — 6 عقول متسلسلة")
st.write(
    "الفكرة أو النص → فهم الحكاية → هندسة الأجزاء → صناعة المواقف → كتابة المسودة → تظبيط الأسلوب → السكريبت النهائي"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def trim_text(text: str, max_chars: int = 30000) -> str:
    if len(text) <= max_chars:
        return text
    head = int(max_chars * 0.72)
    tail = max_chars - head
    return (
        text[:head]
        + "\n\n[تم اختصار جزء من المخرج للحفاظ على حجم السياق]\n\n"
        + text[-tail:]
    )


def retry_delay(error_text: str, default: float) -> float:
    match = re.search(r"retry(?: in)?\s+([0-9]+(?:\.[0-9]+)?)\s*s", error_text, re.I)
    if match:
        try:
            return min(max(float(match.group(1)), default), 120)
        except ValueError:
            pass
    return min(default, 120)


def ask_gemini(client, model: str, prompt: str, retries: int = 6) -> str:
    last_error = None
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=model.strip(),
                contents=prompt,
            )
            text = getattr(response, "text", "") or ""
            if text.strip():
                return text.strip()
            raise RuntimeError("الموديل رجّع ردًا فارغًا.")
        except Exception as exc:
            last_error = exc
            message = str(exc).lower()
            retryable = any(
                token in message
                for token in ["429", "503", "quota", "resource_exhausted", "unavailable", "overloaded"]
            )
            if not retryable or attempt == retries - 1:
                raise
            time.sleep(retry_delay(str(exc), 4 * (2**attempt)))
    raise last_error


def build_prompt(index: int, topic: str, audience: str, minutes: int, sources: str, previous: str) -> str:
    style_rules = read_text(STYLE_FILE)
    template = read_text(PROMPT_FILES[index])

    values = {
        "STYLE_RULES": style_rules,
        "TOPIC": topic,
        "AUDIENCE": audience or "جمهور عام مهتم يفهم الموضوع بطريقة بسيطة وممتعة.",
        "TARGET_MINUTES": str(minutes),
        "SOURCES": sources or "لا توجد مصادر إضافية.",
        "PREVIOUS_OUTPUT": trim_text(previous) if previous else "لا يوجد مخرج سابق. أنت العقل الأول.",
    }

    for key, value in values.items():
        template = template.replace("{" + key + "}", value)
    return template


with st.sidebar:
    st.header("الإعدادات")
    api_key = st.text_input("Google Gemini API Key", type="password")
    model_name = st.text_input("اسم الموديل", value="gemini-3-flash-preview")
    target_minutes = st.slider("مدة الفيديو التقريبية بالدقائق", 10, 90, 30, 5)
    audience = st.text_area(
        "الجمهور المستهدف",
        value="شباب وبنات عايزين يفهموا الموضوع ببساطة، وبيحبوا الحكي والأمثلة ومش بيحبوا المحاضرات الجافة.",
        height=110,
    )
    sources = st.text_area(
        "مصادر أو ملاحظات اختيارية",
        placeholder="الصق هنا كتابًا أو بحثًا أو نقاطًا أو اتركها فارغة.",
        height=130,
    )
    show_outputs = st.checkbox("عرض مخرجات العقول الستة", value=True)

if "outputs" not in st.session_state:
    st.session_state.outputs = {}
if "saved_topic" not in st.session_state:
    st.session_state.saved_topic = ""


topic = st.text_area(
    "اكتب الفكرة أو الصق النص الذي تريد تحويله إلى سكريبت",
    height=240,
    placeholder="مثال: لماذا نبدأ العادات الجديدة بحماس ثم نتركها بعد فترة؟",
)

col1, col2 = st.columns([3, 1])
with col1:
    run = st.button("شغّل العقول الستة", type="primary", use_container_width=True)
with col2:
    reset = st.button("ابدأ من جديد", use_container_width=True)

if reset:
    st.session_state.outputs = {}
    st.session_state.saved_topic = ""
    st.rerun()

if run:
    if not api_key.strip():
        st.error("اكتب مفتاح Gemini API أولًا.")
        st.stop()
    if not topic.strip():
        st.warning("اكتب فكرة أو نصًا أولًا.")
        st.stop()

    if st.session_state.saved_topic and st.session_state.saved_topic != topic.strip():
        st.session_state.outputs = {}

    st.session_state.saved_topic = topic.strip()
    outputs = st.session_state.outputs
    client = genai.Client(api_key=api_key.strip())
    progress = st.progress(len(outputs) / 6)
    status = st.empty()

    try:
        for index in range(6):
            key = f"العقل {index + 1}"
            if key in outputs:
                progress.progress((index + 1) / 6)
                continue

            status.info(f"العقل {index + 1} من 6 بيجهز مخرجه...")
            previous = outputs.get(f"العقل {index}", "")
            prompt = build_prompt(
                index=index,
                topic=topic.strip(),
                audience=audience.strip(),
                minutes=target_minutes,
                sources=sources.strip(),
                previous=previous,
            )
            result = ask_gemini(client, model_name, prompt)
            outputs[key] = result
            st.session_state.outputs = outputs
            progress.progress((index + 1) / 6)

            if show_outputs:
                with st.expander(key, expanded=index >= 4):
                    st.text(result)

        final_script = outputs["العقل 6"]
        status.success("السكريبت النهائي جاهز.")
        st.header("السكريبت النهائي")
        st.text_area("النص الجاهز للتسجيل", value=final_script, height=1100)
        st.download_button(
            "تحميل السكريبت النهائي TXT",
            data=final_script,
            file_name="master_script_egyptian.txt",
            mime="text/plain",
            use_container_width=True,
        )

        report = []
        for index in range(6):
            key = f"العقل {index + 1}"
            report.append(f"\n{'=' * 70}\n{key}\n{'=' * 70}\n\n{outputs[key]}")
        st.download_button(
            "تحميل تقرير العقول الستة",
            data="\n".join(report),
            file_name="six_minds_report.txt",
            mime="text/plain",
            use_container_width=True,
        )
    except Exception as exc:
        st.error(f"حصل خطأ أثناء التشغيل: {exc}")
        st.info("لو الخطأ بسبب الضغط أو الحصة، استنى شوية واضغط تشغيل مرة ثانية؛ المخرجات المحفوظة هتخلي السلسلة تكمل من آخر عقل.")

if st.session_state.outputs and not run:
    st.info(f"فيه {len(st.session_state.outputs)} مخرجات محفوظة. اضغط تشغيل عشان تكمل من آخر عقل.")
