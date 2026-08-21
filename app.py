import re
import time
from pathlib import Path

import streamlit as st
from google import genai


# ==========================================================
# إعدادات الملفات
# ==========================================================

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

MIND_NAMES = [
    "العقل 1",
    "العقل 2",
    "العقل 3",
    "العقل 4",
    "العقل 5",
    "العقل 6",
]


# ==========================================================
# إعدادات الصفحة
# ==========================================================

st.set_page_config(
    page_title="غرفة كتابة السكريبت - 6 عقول",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 غرفة كتابة السكريبت — 6 عقول متعاونة")

st.write(
    """
    **فكرة أو عنوان أو سؤال أو نص**
    
    → فهم الحكاية
    
    → هندسة رحلة الفيديو
    
    → صناعة المواقف والحكايات
    
    → كتابة المسودة
    
    → Humanization وتظبيط الأسلوب
    
    → السكريبت النهائي
    """
)


# ==========================================================
# دوال مساعدة
# ==========================================================

def read_text(path: Path) -> str:
    """
    قراءة ملف نصي بترميز UTF-8
    """

    if not path.exists():
        raise FileNotFoundError(
            f"الملف غير موجود: {path.name}"
        )

    return path.read_text(
        encoding="utf-8"
    )


def trim_text(
    text: str,
    max_chars: int = 18000
) -> str:
    """
    اختصار النص الطويل مع الاحتفاظ
    بالبداية والنهاية.
    """

    if not text:
        return ""

    if len(text) <= max_chars:
        return text

    head = int(max_chars * 0.70)
    tail = max_chars - head

    return (
        text[:head]
        + "\n\n"
        + "[... تم اختصار جزء من المخرج للحفاظ على حجم السياق ...]"
        + "\n\n"
        + text[-tail:]
    )


def retry_delay(
    error_text: str,
    default: float
) -> float:
    """
    محاولة معرفة مدة الانتظار
    من رسالة Gemini.
    """

    match = re.search(
        r"retry(?: in)?\s+([0-9]+(?:\.[0-9]+)?)\s*s",
        error_text,
        re.I
    )

    if match:
        try:
            delay = float(match.group(1))

            return min(
                max(delay, default),
                120
            )

        except ValueError:
            pass

    return min(default, 120)


def ask_gemini(
    client,
    model: str,
    prompt: str,
    retries: int = 6
) -> str:
    """
    إرسال الطلب إلى Gemini
    مع إعادة المحاولة تلقائيًا
    عند أخطاء الضغط أو الـQuota.
    """

    last_error = None

    for attempt in range(retries):

        try:

            response = client.models.generate_content(
                model=model.strip(),
                contents=prompt,
            )

            text = getattr(
                response,
                "text",
                ""
            ) or ""

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

            if (
                not retryable
                or attempt == retries - 1
            ):
                raise

            default_delay = 4 * (2 ** attempt)

            delay = retry_delay(
                str(exc),
                default_delay
            )

            time.sleep(delay)

    raise last_error


# ==========================================================
# بناء السياق المناسب لكل عقل
# ==========================================================

def build_previous_context(
    index: int,
    outputs: dict
) -> str:
    """
    كل عقل يأخذ المعلومات التي يحتاجها فقط.

    index يبدأ من 0.

    العقل 1:
    لا يوجد مخرج سابق.

    العقل 2:
    يأخذ العقل 1.

    العقل 3:
    يأخذ العقل 1 + العقل 2.

    العقل 4:
    يأخذ العقل 1 + العقل 2 + العقل 3.

    العقل 5:
    يأخذ هندسة العقل 2
    + المسودة من العقل 4.

    العقل 6:
    يأخذ فهم العقل 1
    + هندسة العقل 2
    + السكريبت المحسن من العقل 5.
    """

    if index == 0:

        return (
            "لا يوجد مخرج سابق.\n"
            "أنت العقل الأول، ومهمتك فهم المادة الأصلية."
        )

    sections = []

    def add_output(
        mind_number: int,
        title: str,
        max_chars: int = 18000
    ):
        key = f"العقل {mind_number}"

        text = outputs.get(
            key,
            ""
        )

        if text.strip():

            sections.append(
                f"""
==================================================
{title}
==================================================

{trim_text(text, max_chars)}
""".strip()
            )

    # ------------------------------------------------------
    # العقل الثاني
    # ------------------------------------------------------

    if index == 1:

        add_output(
            1,
            "مخرج العقل الأول: فهم الحكاية"
        )

    # ------------------------------------------------------
    # العقل الثالث
    # ------------------------------------------------------

    elif index == 2:

        add_output(
            1,
            "مخرج العقل الأول: فهم الحكاية",
            14000
        )

        add_output(
            2,
            "مخرج العقل الثاني: هندسة رحلة الفيديو",
            18000
        )

    # ------------------------------------------------------
    # العقل الرابع
    # ------------------------------------------------------

    elif index == 3:

        add_output(
            1,
            "مخرج العقل الأول: فهم الحكاية",
            12000
        )

        add_output(
            2,
            "مخرج العقل الثاني: هندسة رحلة الفيديو",
            16000
        )

        add_output(
            3,
            "مخرج العقل الثالث: بنك المواقف والحكايات",
            22000
        )

    # ------------------------------------------------------
    # العقل الخامس
    # ------------------------------------------------------

    elif index == 4:

        add_output(
            2,
            "خريطة الفيديو التي يجب الحفاظ على منطقها",
            12000
        )

        add_output(
            4,
            "المسودة الكاملة المطلوب تحسينها",
            30000
        )

    # ------------------------------------------------------
    # العقل السادس
    # ------------------------------------------------------

    elif index == 5:

        add_output(
            1,
            "جوهر الموضوع الذي اكتشفه العقل الأول",
            10000
        )

        add_output(
            2,
            "خريطة رحلة الفيديو",
            12000
        )

        add_output(
            5,
            "السكريبت المحسن القادم من العقل الخامس",
            35000
        )

    if not sections:

        return "لا يوجد سياق سابق."

    return "\n\n".join(sections)


# ==========================================================
# بناء البرومبت
# ==========================================================

def build_prompt(
    index: int,
    topic: str,
    audience: str,
    minutes: int,
    sources: str,
    outputs: dict,
) -> str:

    # قراءة قواعد الأسلوب
    style_rules = read_text(
        STYLE_FILE
    )

    # قراءة برومبت العقل الحالي
    template = read_text(
        PROMPT_FILES[index]
    )

    # بناء السياق المناسب
    previous_context = build_previous_context(
        index=index,
        outputs=outputs,
    )

    values = {
        "STYLE_RULES": style_rules,

        "TOPIC": topic,

        "AUDIENCE": (
            audience
            or
            "جمهور عام مهتم بفهم الموضوع "
            "بطريقة بسيطة وممتعة."
        ),

        "TARGET_MINUTES": str(minutes),

        "SOURCES": (
            sources
            or
            "لا توجد مصادر إضافية."
        ),

        "PREVIOUS_OUTPUT": previous_context,
    }

    # استبدال المتغيرات
    #
    # STYLE_RULES يتم وضعه أولًا،
    # ثم يتم استبدال باقي المتغيرات،
    # لذلك لو ملف القواعد يحتوي على
    # {TOPIC} أو {SOURCES}
    # سيتم استبدالهم أيضًا.

    for key, value in values.items():

        template = template.replace(
            "{" + key + "}",
            value
        )

    return template


# ==========================================================
# الشريط الجانبي
# ==========================================================

with st.sidebar:

    st.header("⚙️ الإعدادات")

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
        min_value=10,
        max_value=90,
        value=30,
        step=5,
    )

    audience = st.text_area(
        "الجمهور المستهدف",
        value=(
            "شباب وبنات عايزين يفهموا الموضوع ببساطة، "
            "وبيحبوا الحكي والأمثلة ومش بيحبوا "
            "المحاضرات الجافة."
        ),
        height=120,
    )

    sources = st.text_area(
        "مصادر أو ملاحظات اختيارية",
        placeholder=(
            "الصق هنا كتابًا أو بحثًا أو دراسة "
            "أو نقاطًا أو ملاحظات."
        ),
        height=150,
    )

    show_outputs = st.checkbox(
        "عرض مخرجات العقول أثناء التشغيل",
        value=True,
    )

    st.divider()

    st.caption(
        "💡 العقول تحفظ تقدمها، ولو حصل خطأ "
        "أو Quota تقدر تشغل مرة تانية "
        "وتكمل من آخر عقل."
    )


# ==========================================================
# Session State
# ==========================================================

if "outputs" not in st.session_state:

    st.session_state.outputs = {}


if "saved_topic" not in st.session_state:

    st.session_state.saved_topic = ""


# ==========================================================
# إدخال الموضوع
# ==========================================================

topic = st.text_area(
    "اكتب الفكرة أو العنوان أو الصق النص الذي تريد تحويله إلى سكريبت",
    height=260,
    placeholder=(
        "أمثلة:\n\n"
        "ليه مش بعرف أحافظ على عادة جديدة؟\n\n"
        "كيف تتجنب التعرض للتجاهل المفاجئ؟\n\n"
        "إزاي أجبر نفسي أشتغل على مستقبلي رغم إني "
        "مرهق وقرفان؟\n\n"
        "أو الصق هنا نصًا طويلًا من كتاب أو بحث أو ملاحظات."
    ),
)


# ==========================================================
# أزرار التشغيل
# ==========================================================

col1, col2 = st.columns(
    [3, 1]
)

with col1:

    run = st.button(
        "🚀 شغّل العقول الستة",
        type="primary",
        use_container_width=True,
    )


with col2:

    reset = st.button(
        "🔄 ابدأ من جديد",
        use_container_width=True,
    )


# ==========================================================
# إعادة التشغيل من الصفر
# ==========================================================

if reset:

    st.session_state.outputs = {}

    st.session_state.saved_topic = ""

    st.rerun()


# ==========================================================
# تشغيل العقول
# ==========================================================

if run:

    # ------------------------------------------------------
    # التحقق من API Key
    # ------------------------------------------------------

    if not api_key.strip():

        st.error(
            "اكتب Google Gemini API Key أولًا."
        )

        st.stop()

    # ------------------------------------------------------
    # التحقق من الموضوع
    # ------------------------------------------------------

    if not topic.strip():

        st.warning(
            "اكتب فكرة أو عنوان أو نص أولًا."
        )

        st.stop()

    # ------------------------------------------------------
    # إذا تغير الموضوع
    # نمسح المخرجات القديمة
    # ------------------------------------------------------

    if (
        st.session_state.saved_topic
        and
        st.session_state.saved_topic
        != topic.strip()
    ):

        st.session_state.outputs = {}

    # حفظ الموضوع الحالي
    st.session_state.saved_topic = topic.strip()

    outputs = st.session_state.outputs

    # إنشاء Gemini Client
    client = genai.Client(
        api_key=api_key.strip()
    )

    # حساب التقدم الحالي
    completed = len(outputs)

    progress = st.progress(
        completed / 6
    )

    status = st.empty()

    # ------------------------------------------------------
    # تشغيل العقول بالترتيب
    # ------------------------------------------------------

    try:

        for index in range(6):

            key = MIND_NAMES[index]

            # ----------------------------------------------
            # لو العقل خلص قبل كده
            # ----------------------------------------------

            if key in outputs:

                progress.progress(
                    (index + 1) / 6
                )

                continue

            # ----------------------------------------------
            # رسالة الحالة
            # ----------------------------------------------

            status.info(
                f"🧠 {key} من 6 شغال دلوقتي..."
            )

            # ----------------------------------------------
            # بناء البرومبت
            # ----------------------------------------------

            prompt = build_prompt(
                index=index,
                topic=topic.strip(),
                audience=audience.strip(),
                minutes=target_minutes,
                sources=sources.strip(),
                outputs=outputs,
            )

            # ----------------------------------------------
            # إرسال إلى Gemini
            # ----------------------------------------------

            result = ask_gemini(
                client=client,
                model=model_name,
                prompt=prompt,
            )

            # ----------------------------------------------
            # حفظ النتيجة فورًا
            # ----------------------------------------------

            outputs[key] = result

            st.session_state.outputs = outputs

            # ----------------------------------------------
            # تحديث Progress
            # ----------------------------------------------

            progress.progress(
                (index + 1) / 6
            )

            # ----------------------------------------------
            # عرض المخرج
            # ----------------------------------------------

            if show_outputs:

                with st.expander(
                    f"🧠 {key}",
                    expanded=index >= 3,
                ):

                    st.text_area(
                        label=f"مخرج {key}",
                        value=result,
                        height=500,
                        key=f"output_display_{index}",
                    )

        # ==================================================
        # السكريبت النهائي
        # ==================================================

        final_script = outputs.get(
            "العقل 6",
            ""
        )

        status.success(
            "🎉 السكريبت النهائي جاهز!"
        )

        st.divider()

        st.header(
            "🎬 السكريبت النهائي"
        )

        st.text_area(
            "النص الجاهز للتسجيل",
            value=final_script,
            height=1200,
            key="final_script_display",
        )

        # ==================================================
        # تحميل السكريبت النهائي
        # ==================================================

        st.download_button(
            "⬇️ تحميل السكريبت النهائي TXT",
            data=final_script,
            file_name="master_script_egyptian.txt",
            mime="text/plain",
            use_container_width=True,
        )

        # ==================================================
        # إنشاء تقرير العقول
        # ==================================================

        report = []

        for index in range(6):

            key = MIND_NAMES[index]

            content = outputs.get(
                key,
                ""
            )

            report.append(
                f"""
{'=' * 80}

{key}

{'=' * 80}

{content}
""".strip()
            )

        full_report = "\n\n".join(
            report
        )

        st.download_button(
            "📄 تحميل تقرير العقول الستة",
            data=full_report,
            file_name="six_minds_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    except Exception as exc:

        error_message = str(exc)

        st.error(
            f"حصل خطأ أثناء التشغيل:\n\n{error_message}"
        )

        st.info(
            """
            المخرجات السابقة محفوظة.

            لو المشكلة بسبب:
            
            - Quota
            - 429
            - ضغط على Gemini
            - انتهاء الحصة المؤقتة

            استنى شوية واضغط تشغيل مرة تانية.

            النظام هيكمل من آخر عقل خلص.
            """
        )


# ==========================================================
# عرض حالة المخرجات المحفوظة
# ==========================================================

if (
    st.session_state.outputs
    and
    not run
):

    completed_count = len(
        st.session_state.outputs
    )

    st.info(
        f"💾 فيه {completed_count} من 6 "
        f"مخرجات محفوظة."
    )

    st.caption(
        "اضغط «شغّل العقول الستة» عشان "
        "تكمل من آخر مرحلة."
    )
