import re
import time
from pathlib import Path

import streamlit as st
from google import genai


# ============================================================
# الملفات والمسارات
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

TOTAL_MINDS = 6


# ============================================================
# إعداد الصفحة
# ============================================================

st.set_page_config(
    page_title="غرفة كتابة السكريبت - 6 عقول",
    page_icon="🧠",
    layout="wide",
)


st.title("🧠 غرفة كتابة السكريبت — 6 عقول")

st.write(
    """
    أدخل أي مادة تريد تحويلها إلى فيديو:
    عنوان، فكرة، سؤال، مشكلة، نص، مقال، جزء من كتاب أو ملاحظات.

    العقول الستة ستحول المادة إلى:
    فهم الحكاية → رحلة الفيديو → المواقف والحكايات →
    كتابة السكريبت → Humanization → النسخة النهائية.
    """
)


# ============================================================
# قراءة الملفات
# ============================================================

def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f"الملف غير موجود:\n{path.name}"
        )

    return path.read_text(
        encoding="utf-8"
    )


# ============================================================
# تقليل حجم النص عند الحاجة
# ============================================================

def trim_text(
    text: str,
    max_chars: int = 35000
) -> str:

    if not text:
        return ""

    if len(text) <= max_chars:
        return text

    head_size = int(max_chars * 0.70)
    tail_size = max_chars - head_size

    return (
        text[:head_size]
        + "\n\n"
        + "[تم اختصار جزء من النص للحفاظ على حجم السياق]\n"
        + "\n"
        + text[-tail_size:]
    )


# ============================================================
# استخراج وقت إعادة المحاولة من رسالة الخطأ
# ============================================================

def retry_delay(
    error_text: str,
    default: float
) -> float:

    patterns = [
        r"retry(?: in)?\s+([0-9]+(?:\.[0-9]+)?)\s*s",
        r"retry_delay[^0-9]*([0-9]+(?:\.[0-9]+)?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            error_text,
            re.IGNORECASE
        )

        if match:
            try:

                delay = float(
                    match.group(1)
                )

                return min(
                    max(delay, default),
                    120
                )

            except ValueError:
                pass

    return min(
        default,
        120
    )


# ============================================================
# الاتصال بـ Gemini مع إعادة المحاولة
# ============================================================

def ask_gemini(
    client,
    model: str,
    prompt: str,
    retries: int = 6
) -> str:

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

            error_message = str(exc).lower()

            retryable_tokens = [

                "429",
                "503",
                "quota",
                "resource_exhausted",
                "unavailable",
                "overloaded",
                "internal",
                "deadline_exceeded",

            ]

            retryable = any(
                token in error_message
                for token in retryable_tokens
            )

            if (
                not retryable
                or attempt == retries - 1
            ):
                raise

            default_delay = 5 * (
                2 ** attempt
            )

            delay = retry_delay(
                str(exc),
                default_delay
            )

            time.sleep(delay)

    raise last_error


# ============================================================
# تجهيز البرومبت
# ============================================================

def build_prompt(
    index: int,
    topic: str,
    audience: str,
    minutes: int,
    sources: str,
    previous: str
) -> str:

    style_rules = read_text(
        STYLE_FILE
    )

    template = read_text(
        PROMPT_FILES[index]
    )

    values = {

        "STYLE_RULES":
            style_rules,

        "TOPIC":
            trim_text(
                topic,
                40000
            ),

        "AUDIENCE":
            audience
            or
            "جمهور عام مهتم يفهم الموضوع بطريقة بسيطة وممتعة وبيحب الحكي والأمثلة ومش بيحب المحاضرات الجافة.",

        "TARGET_MINUTES":
            str(minutes),

        "SOURCES":
            trim_text(
                sources,
                30000
            )
            if sources
            else
            "لا توجد مصادر إضافية.",

        "PREVIOUS_OUTPUT":
            trim_text(
                previous,
                50000
            )
            if previous
            else
            "لا يوجد مخرج سابق.",

    }

    for key, value in values.items():

        placeholder = (
            "{"
            + key
            + "}"
        )

        template = template.replace(
            placeholder,
            value
        )

    return template


# ============================================================
# تجهيز السياق لكل عقل
# ============================================================

def get_context_for_mind(
    index: int,
    outputs: dict
) -> str:

    # --------------------------------------------------------
    # العقل الأول
    # --------------------------------------------------------

    if index == 0:

        return (
            "لا يوجد مخرج سابق. "
            "أنت أول عقل يستلم المادة."
        )

    # --------------------------------------------------------
    # العقل الثاني
    # --------------------------------------------------------

    if index == 1:

        return outputs.get(
            "العقل 1",
            ""
        )

    # --------------------------------------------------------
    # العقل الثالث
    # --------------------------------------------------------

    if index == 2:

        return outputs.get(
            "العقل 2",
            ""
        )

    # --------------------------------------------------------
    # العقل الرابع - الكاتب الرئيسي
    #
    # هنا يحتاج:
    #
    # رحلة الفيديو من العقل الثاني
    # +
    # بنك المواقف والحكايات من العقل الثالث
    # --------------------------------------------------------

    if index == 3:

        mind_2 = outputs.get(
            "العقل 2",
            ""
        )

        mind_3 = outputs.get(
            "العقل 3",
            ""
        )

        return f"""

==================================================
رحلة الفيديو التي بناها العقل الثاني
==================================================

{trim_text(mind_2, 30000)}

==================================================
المواقف والحكايات والأمثلة من العقل الثالث
==================================================

{trim_text(mind_3, 30000)}

==================================================
مهمتك الآن
==================================================

أنت الكاتب الرئيسي.

لا تحول هذه المخرجات إلى تقرير.

استخدمها كمادة خام فقط.

الهدف هو كتابة سكريبت طبيعي،
إنساني،
بالعامية المصرية،
ويتحرك كمحتوى فيديو حقيقي.

"""

    # --------------------------------------------------------
    # العقل الخامس
    #
    # يأخذ السكريبت فقط
    # --------------------------------------------------------

    if index == 4:

        return outputs.get(
            "العقل 4",
            ""
        )

    # --------------------------------------------------------
    # العقل السادس
    #
    # يأخذ النسخة المحسنة فقط
    # --------------------------------------------------------

    if index == 5:

        return outputs.get(
            "العقل 5",
            ""
        )

    return ""


# ============================================================
# القائمة الجانبية
# ============================================================

with st.sidebar:

    st.header("⚙️ الإعدادات")

    api_key = st.text_input(
        "Google Gemini API Key",
        type="password"
    )

    model_name = st.text_input(
        "اسم الموديل",
        value="gemini-3-flash-preview"
    )

    target_minutes = st.slider(
        "مدة الفيديو التقريبية بالدقائق",
        min_value=10,
        max_value=90,
        value=30,
        step=5
    )

    audience = st.text_area(
        "الجمهور المستهدف",
        value=(
            "شباب وبنات عايزين يفهموا الموضوع "
            "ببساطة، وبيحبوا الحكي والأمثلة "
            "ومش بيحبوا المحاضرات الجافة."
        ),
        height=120
    )

    sources = st.text_area(
        "مصادر أو ملاحظات اختيارية",
        placeholder=(
            "الصق هنا كتابًا أو بحثًا أو ملاحظات "
            "أو أي معلومات تريد استخدامها."
        ),
        height=160
    )

    show_outputs = st.checkbox(
        "عرض مخرجات العقول الستة",
        value=True
    )


# ============================================================
# Session State
# ============================================================

if "outputs" not in st.session_state:

    st.session_state.outputs = {}


if "saved_topic" not in st.session_state:

    st.session_state.saved_topic = ""


if "run_settings" not in st.session_state:

    st.session_state.run_settings = {}


# ============================================================
# إدخال المادة
# ============================================================

topic = st.text_area(
    "✍️ اكتب الفكرة أو الصق النص الذي تريد تحويله إلى سكريبت",
    height=260,
    placeholder="""
أمثلة:

كيف تتجنب التعرض للتجاهل المفاجئ؟

إزاي أجبر نفسي أشتغل على مستقبلي وأنا قرفان ومرهق طول اليوم؟

لماذا نبدأ العادات الجديدة بحماس ثم نتركها؟

أو الصق هنا نصًا كاملًا أو جزءًا من كتاب أو مقال.
"""
)


# ============================================================
# الأزرار
# ============================================================

col1, col2 = st.columns(
    [3, 1]
)

with col1:

    run = st.button(
        "🚀 شغّل العقول الستة",
        type="primary",
        use_container_width=True
    )


with col2:

    reset = st.button(
        "🔄 ابدأ من جديد",
        use_container_width=True
    )


# ============================================================
# إعادة البداية
# ============================================================

if reset:

    st.session_state.outputs = {}

    st.session_state.saved_topic = ""

    st.session_state.run_settings = {}

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
    # التحقق من وجود المادة
    # --------------------------------------------------------

    if not topic.strip():

        st.warning(
            "اكتب عنوانًا أو فكرة أو نصًا أولًا."
        )

        st.stop()


    current_topic = topic.strip()


    # --------------------------------------------------------
    # لو المستخدم غيّر المادة
    # نبدأ من جديد
    # --------------------------------------------------------

    if (
        st.session_state.saved_topic
        and
        st.session_state.saved_topic
        != current_topic
    ):

        st.session_state.outputs = {}


    st.session_state.saved_topic = (
        current_topic
    )


    # --------------------------------------------------------
    # حفظ إعدادات التشغيل
    # --------------------------------------------------------

    st.session_state.run_settings = {

        "audience":
            audience.strip(),

        "minutes":
            target_minutes,

        "sources":
            sources.strip(),

        "model":
            model_name.strip(),

    }


    outputs = (
        st.session_state.outputs
    )


    # --------------------------------------------------------
    # إنشاء العميل
    # --------------------------------------------------------

    client = genai.Client(
        api_key=api_key.strip()
    )


    # --------------------------------------------------------
    # شريط التقدم
    # --------------------------------------------------------

    completed_count = len(outputs)

    progress = st.progress(
        completed_count / TOTAL_MINDS
    )

    status = st.empty()


    mind_names = [

        "🧠 العقل الأول: فهم الحكاية",

        "🧭 العقل الثاني: بناء رحلة الفيديو",

        "🎭 العقل الثالث: صناعة المواقف والحكايات",

        "✍️ العقل الرابع: كتابة السكريبت",

        "🫂 العقل الخامس: Humanization",

        "🎬 العقل السادس: الإخراج النهائي",

    ]


    try:

        for index in range(
            TOTAL_MINDS
        ):

            key = (
                f"العقل {index + 1}"
            )


            # ------------------------------------------------
            # لو العقل خلص قبل كده
            # ------------------------------------------------

            if key in outputs:

                progress.progress(
                    (index + 1)
                    /
                    TOTAL_MINDS
                )

                continue


            # ------------------------------------------------
            # رسالة الحالة
            # ------------------------------------------------

            status.info(
                f"{mind_names[index]} "
                f"— {index + 1} من "
                f"{TOTAL_MINDS}"
            )


            # ------------------------------------------------
            # تجهيز السياق المناسب للعقل
            # ------------------------------------------------

            previous_context = (
                get_context_for_mind(
                    index,
                    outputs
                )
            )


            # ------------------------------------------------
            # بناء البرومبت
            # ------------------------------------------------

            prompt = build_prompt(

                index=index,

                topic=current_topic,

                audience=audience.strip(),

                minutes=target_minutes,

                sources=sources.strip(),

                previous=previous_context,

            )


            # ------------------------------------------------
            # تشغيل Gemini
            # ------------------------------------------------

            result = ask_gemini(

                client=client,

                model=model_name,

                prompt=prompt,

            )


            # ------------------------------------------------
            # حفظ النتيجة
            # ------------------------------------------------

            outputs[key] = result

            st.session_state.outputs = (
                outputs
            )


            progress.progress(
                (index + 1)
                /
                TOTAL_MINDS
            )


            # ------------------------------------------------
            # عرض المخرج
            # ------------------------------------------------

            if show_outputs:

                expanded = (
                    index >= 3
                )

                with st.expander(
                    f"{mind_names[index]}",
                    expanded=expanded
                ):

                    st.text_area(

                        label="المخرج",

                        value=result,

                        height=500,

                        key=f"output_view_{index}",

                    )


        # ====================================================
        # السكريبت النهائي
        # ====================================================

        final_script = outputs.get(
            "العقل 6",
            ""
        )


        status.success(
            "🎉 السكريبت النهائي جاهز!"
        )


        progress.progress(1.0)


        st.divider()


        st.header(
            "🎬 السكريبت النهائي"
        )


        st.text_area(

            "النص الجاهز للتسجيل",

            value=final_script,

            height=1200,

        )


        # ====================================================
        # تحميل السكريبت
        # ====================================================

        st.download_button(

            "⬇️ تحميل السكريبت النهائي TXT",

            data=final_script,

            file_name=(
                "master_script_egyptian.txt"
            ),

            mime="text/plain",

            use_container_width=True,

        )


        # ====================================================
        # تقرير جميع العقول
        # ====================================================

        report_parts = []


        for index in range(
            TOTAL_MINDS
        ):

            key = (
                f"العقل {index + 1}"
            )

            result = outputs.get(
                key,
                ""
            )

            report_parts.append(

                f"""

{'=' * 80}

{mind_names[index]}

{'=' * 80}


{result}

"""

            )


        full_report = (
            "\n".join(
                report_parts
            )
        )


        st.download_button(

            "📄 تحميل تقرير العقول الستة",

            data=full_report,

            file_name=(
                "six_minds_report.txt"
            ),

            mime="text/plain",

            use_container_width=True,

        )


    except Exception as exc:

        status.empty()

        st.error(
            f"حصل خطأ أثناء التشغيل:\n\n{exc}"
        )


        st.info(
            """
لو الخطأ حصل بسبب الضغط أو الـQuota،
استنى شوية واضغط تشغيل مرة ثانية.

المخرجات اللي خلصت بالفعل محفوظة،
والبرنامج هيكمل من آخر عقل وصل له.
"""
        )


# ============================================================
# لو فيه مخرجات محفوظة
# ============================================================

if (
    st.session_state.outputs
    and
    not run
):

    completed = len(
        st.session_state.outputs
    )

    st.info(
        f"""
فيه حاليًا {completed} من أصل
{TOTAL_MINDS} عقول خلصوا.

لو كنت وقفت بسبب خطأ أو Quota،
اضغط "شغّل العقول الستة"
وهيكمل من آخر عقل.
"""
    )
