import json
import os
import re
import time
from pathlib import Path

import streamlit as st
from google import genai


# ============================================================
# الملفات الأساسية
# ============================================================

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


# ============================================================
# إعداد الصفحة
# ============================================================

st.set_page_config(
    page_title="غرفة كتابة السكريبت - 6 عقول",
    page_icon="🧠",
    layout="wide",
)

st.title("غرفة كتابة السكريبت — 6 عقول متسلسلة")

st.write(
    """
    المادة الأصلية → فهم وتحليل → بناء الحكاية → رحلة المشاهد
    → تطوير الشرح → الحلول والنهاية → السكريبت النهائي
    """
)


# ============================================================
# قراءة الملفات
# ============================================================

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ============================================================
# تقليل حجم النص عند الحاجة
# ============================================================

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


# ============================================================
# استخراج مدة الانتظار من الخطأ
# ============================================================

def retry_delay(error_text: str, default: float) -> float:

    match = re.search(
        r"retry(?: in)?\s+([0-9]+(?:\.[0-9]+)?)\s*s",
        error_text,
        re.I,
    )

    if match:
        try:
            return min(
                max(float(match.group(1)), default),
                120,
            )

        except ValueError:
            pass

    return min(default, 120)


# ============================================================
# إرسال الطلب إلى Gemini مع إعادة المحاولة
# ============================================================

def ask_gemini(
    client,
    model: str,
    prompt: str,
    retries: int = 6,
) -> str:

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

            raise RuntimeError(
                "الموديل رجّع ردًا فارغًا."
            )

        except Exception as exc:

            last_error = exc

            message = str(exc).lower()

            retryable = any(
                token in message
                for token in [
                    "429",
                    "503",
                    "quota",
                    "resource_exhausted",
                    "unavailable",
                    "overloaded",
                ]
            )

            if not retryable or attempt == retries - 1:
                raise

            delay = retry_delay(
                str(exc),
                4 * (2 ** attempt),
            )

            time.sleep(delay)

    raise last_error


# ============================================================
# بناء السياق التراكمي
# ============================================================

def build_cumulative_context(outputs: dict, current_index: int) -> str:
    """
    يجمع مخرجات كل العقول السابقة.

    مثال:

    العقل 3 يرى:
    - مخرجات العقل 1
    - مخرجات العقل 2

    العقل 6 يرى:
    - مخرجات العقل 1
    - مخرجات العقل 2
    - مخرجات العقل 3
    - مخرجات العقل 4
    - مخرجات العقل 5
    """

    if current_index == 0:
        return "لا يوجد مخرج سابق. أنت العقل الأول."

    context_parts = []

    for index in range(current_index):

        key = f"العقل {index + 1}"

        if key in outputs:

            context_parts.append(
                f"""
━━━━━━━━━━━━━━━━━━
مخرجات {key}
━━━━━━━━━━━━━━━━━━

{outputs[key]}
"""
            )

    if not context_parts:
        return "لا توجد مخرجات سابقة."

    full_context = "\n".join(context_parts)

    return trim_text(
        full_context,
        max_chars=90000,
    )


# ============================================================
# بناء البرومبت لكل عقل
# ============================================================

def build_prompt(
    index: int,
    topic: str,
    audience: str,
    minutes: int,
    sources: str,
    previous: str,
) -> str:

    style_rules = read_text(STYLE_FILE)

    template = read_text(
        PROMPT_FILES[index]
    )

    values = {

        "STYLE_RULES": style_rules,

        "TOPIC": topic,

        "AUDIENCE": (
            audience
            or
            "جمهور عام مهتم يفهم الموضوع بطريقة بسيطة وممتعة."
        ),

        "TARGET_MINUTES": str(minutes),

        "SOURCES": (
            sources
            or
            "لا توجد مصادر إضافية."
        ),

        "PREVIOUS_OUTPUT": (
            trim_text(
                previous,
                max_chars=90000,
            )
            if previous
            else
            "لا يوجد مخرج سابق. أنت العقل الأول."
        ),
    }

    for key, value in values.items():

        template = template.replace(
            "{" + key + "}",
            value,
        )

    return template


# ============================================================
# الإعدادات الجانبية
# ============================================================

with st.sidebar:

    st.header("الإعدادات")

    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
    )

    model_name = st.text_input(
        "اسم الموديل",
        value="gemini-3-flash-preview",
    )

    target_minutes = st.slider(
        "مدة الفيديو التقريبية بالدقائق",
        10,
        90,
        30,
        5,
    )

    audience = st.text_area(
        "الجمهور المستهدف",

        value=(
            "شباب وبنات عايزين يفهموا الموضوع ببساطة، "
            "وبيحبوا الحكي والأمثلة ومش بيحبوا المحاضرات الجافة."
        ),

        height=110,
    )

    sources = st.text_area(
        "مصادر أو ملاحظات اختيارية",

        placeholder=(
            "الصق هنا كتابًا أو بحثًا أو نقاطًا أو اتركها فارغة."
        ),

        height=130,
    )

    show_outputs = st.checkbox(
        "عرض مخرجات العقول الستة",
        value=True,
    )


# ============================================================
# Session State
# ============================================================

if "outputs" not in st.session_state:
    st.session_state.outputs = {}

if "saved_topic" not in st.session_state:
    st.session_state.saved_topic = ""


# ============================================================
# إدخال المادة
# ============================================================

topic = st.text_area(

    "اكتب الفكرة أو الصق النص الذي تريد تحويله إلى سكريبت",

    height=240,

    placeholder=(
        "مثال: لماذا نبدأ العادات الجديدة بحماس ثم نتركها بعد فترة؟"
    ),
)


# ============================================================
# الأزرار
# ============================================================

col1, col2 = st.columns([3, 1])

with col1:

    run = st.button(
        "شغّل العقول الستة",
        type="primary",
        use_container_width=True,
    )

with col2:

    reset = st.button(
        "ابدأ من جديد",
        use_container_width=True,
    )


# ============================================================
# إعادة التشغيل
# ============================================================

if reset:

    st.session_state.outputs = {}

    st.session_state.saved_topic = ""

    st.rerun()


# ============================================================
# تشغيل العقول
# ============================================================

if run:

    # --------------------------------------------------------
    # التحقق من API Key
    # --------------------------------------------------------

    if not api_key.strip():

        st.error(
            "اكتب مفتاح Gemini API أولًا."
        )

        st.stop()


    # --------------------------------------------------------
    # التحقق من المادة
    # --------------------------------------------------------

    if not topic.strip():

        st.warning(
            "اكتب فكرة أو نصًا أولًا."
        )

        st.stop()


    # --------------------------------------------------------
    # لو الموضوع اتغير نمسح المخرجات القديمة
    # --------------------------------------------------------

    if (
        st.session_state.saved_topic
        and
        st.session_state.saved_topic != topic.strip()
    ):

        st.session_state.outputs = {}


    # حفظ المادة الحالية

    st.session_state.saved_topic = topic.strip()

    outputs = st.session_state.outputs


    # --------------------------------------------------------
    # إنشاء Gemini Client
    # --------------------------------------------------------

    client = genai.Client(
        api_key=api_key.strip()
    )


    # --------------------------------------------------------
    # شريط التقدم
    # --------------------------------------------------------

    progress = st.progress(
        len(outputs) / 6
    )

    status = st.empty()


    try:

        # ====================================================
        # تشغيل العقول الستة
        # ====================================================

        for index in range(6):

            key = f"العقل {index + 1}"


            # ------------------------------------------------
            # لو العقل خلص قبل كده ما نشغلوش تاني
            # ------------------------------------------------

            if key in outputs:

                progress.progress(
                    (index + 1) / 6
                )

                continue


            # ------------------------------------------------
            # رسالة الحالة
            # ------------------------------------------------

            status.info(
                f"العقل {index + 1} من 6 بيجهز مخرجه..."
            )


            # ------------------------------------------------
            # هنا التعديل الأساسي
            #
            # كل عقل يستلم كل مخرجات العقول السابقة
            # ------------------------------------------------

            previous_context = build_cumulative_context(
                outputs=outputs,
                current_index=index,
            )


            # ------------------------------------------------
            # بناء البرومبت
            # ------------------------------------------------

            prompt = build_prompt(

                index=index,

                topic=topic.strip(),

                audience=audience.strip(),

                minutes=target_minutes,

                sources=sources.strip(),

                previous=previous_context,
            )


            # ------------------------------------------------
            # تشغيل العقل
            # ------------------------------------------------

            result = ask_gemini(

                client=client,

                model=model_name,

                prompt=prompt,
            )


            # ------------------------------------------------
            # حفظ المخرج
            # ------------------------------------------------

            outputs[key] = result

            st.session_state.outputs = outputs


            # ------------------------------------------------
            # تحديث شريط التقدم
            # ------------------------------------------------

            progress.progress(
                (index + 1) / 6
            )


            # ------------------------------------------------
            # عرض مخرجات العقول
            # ------------------------------------------------

            if show_outputs:

                with st.expander(
                    key,
                    expanded=index >= 4,
                ):

                    st.text(result)


        # ====================================================
        # السكريبت النهائي
        # ====================================================

        final_script = outputs["العقل 6"]


        status.success(
            "السكريبت النهائي جاهز."
        )


        st.header(
            "السكريبت النهائي"
        )


        st.text_area(

            "النص الجاهز للتسجيل",

            value=final_script,

            height=1100,
        )


        # ====================================================
        # تحميل السكريبت النهائي
        # ====================================================

        st.download_button(

            "تحميل السكريبت النهائي TXT",

            data=final_script,

            file_name="master_script_egyptian.txt",

            mime="text/plain",

            use_container_width=True,
        )


        # ====================================================
        # تقرير العقول الستة
        # ====================================================

        report = []

        for index in range(6):

            key = f"العقل {index + 1}"

            report.append(

                f"""
{'=' * 70}
{key}
{'=' * 70}

{outputs[key]}
"""
            )


        st.download_button(

            "تحميل تقرير العقول الستة",

            data="\n".join(report),

            file_name="six_minds_report.txt",

            mime="text/plain",

            use_container_width=True,
        )


    # ========================================================
    # معالجة الأخطاء
    # ========================================================

    except Exception as exc:

        st.error(
            f"حصل خطأ أثناء التشغيل: {exc}"
        )

        st.info(
            "لو الخطأ بسبب الضغط أو الحصة، استنى شوية واضغط تشغيل مرة ثانية؛ "
            "المخرجات المحفوظة هتخلي السلسلة تكمل من آخر عقل."
        )


# ============================================================
# لو فيه مخرجات محفوظة
# ============================================================

if st.session_state.outputs and not run:

    st.info(

        f"فيه {len(st.session_state.outputs)} "
        "مخرجات محفوظة. اضغط تشغيل عشان تكمل من آخر عقل."
    )
