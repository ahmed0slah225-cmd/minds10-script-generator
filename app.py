import time
import re
import streamlit as st
from google import genai

# ============================================================
# إعداد الصفحة
# ============================================================

st.set_page_config(
    page_title="غرفة كتابة يوتيوب - 10 عقول احترافية",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 غرفة كتابة سكريبت يوتيوب - نظام الـ 10 عقول المطور")
st.write(
    "نظام صياغة سكريبتات يوتيوب طويلة عميقة، إنسانية، قائمة على التحول الفكري "
    "والسرد السلس بعيداً عن المباشرة والكليشيهات."
)

# ============================================================
# الإعدادات
# ============================================================

with st.sidebar:
    st.header("⚙️ الإعدادات")

    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
    )

    model_name = st.text_input(
        "اسم الموديل",
        value="gemini-2.5-flash",
    )

    fallback_model = st.text_input(
        "Fallback Model",
        value="gemini-2.5-flash",
    )

    target_minutes = st.slider(
        "مدة الفيديو المستهدفة بالدقائق",
        min_value=10,
        max_value=60,
        value=25,
        step=5,
    )

    audience = st.text_area(
        "الجمهور المستهدف",
        value=(
            "جمهور يبحث عن فهم أعمق لنفسه وللحياة، يكره المحاضرات والوعظ والمثالية المزيفة، "
            "يريد كلاماً يلمس واقعه الشفهي اليومي ويغير زاوية رؤيته للأمور."
        ),
        height=130,
    )

    sources = st.text_area(
        "مصادر أو كتب أو ملاحظات اختيارية",
        placeholder="اكتب هنا كتب، أبحاث، أو أفكار ملهمة (مثل: كتاب Dopamine Nation، Atomic Habits، إلخ)...",
        height=140,
    )

    st.divider()

    show_all_outputs = st.checkbox(
        "عرض مخرجات كل العقول",
        value=True,
    )


# ============================================================
# القواعد العامة الفائقة
# ============================================================

GLOBAL_RULES = """
أنت كاتب وصانع محتوى خبير ومحترف في كتابة سكريبتات يوتيوب طويلة (Long-form Essays / Story-driven Videos).

الهدف النهائي: إنتاج سكريبت بشري جداً، دافئ، مستفز فكرياً، يجعل المشاهد يشعر أن الفيديو صُمم خصيصاً له، ويخوض معه "رحلة اكتشاف فكرية أو نفسية".

اللغة: اللهجة العامية المصرية الطبيعية جداً، الشفهية، المناسبة لإلقاء أمام الكاميرا بكل تلقائية (أو الفصحى البسيطة السلسة إن فرض الموضوع ذلك، ولكن العامية المفهومة هي الأصل).

قواعد غير قابلة للكسر:
1. لا تبدأ بسلام، تحية، أو تعريف بنفسك أو بالفيديو (ممنوع: "أهلاً بيكم"، "في الفيديو ده هنتكلم عن").
2. لا تستخدم كليشيهات الذكاء الاصطناعي أو المقالات (ممنوع: "دعنا نتعمق"، "في عصرنا الحالي"، "الجدير بالذكر").
3. لا تبدأ بتعاريف أكاديمية جافة، بل ابدأ بموقف، مفارقة، أو اقتباس مدهش، أو أسئلة تعبر عن حوار داخلي حقيقي.
4. الفيديو ليس محاضرة وليس قائمة نصائح منفصلة؛ الفيديو هو "قصة فكرة" تتطور تدريجياً.
5. المتحدث ليس "سوبر هيرو" يوزع الحكمة، بل هو إنسان يستكشف مع المشاهد (صوت صديق ذكي ومشارك).
6. تجنب التنظير دون أمثلة ملموسة من الحياة اليومية (الشاشة، النوم، المنبه، الصراع الداخلي).
7. الحرص على وجود Open Loops (أسئلة معلقة) تجعل المشاهد ينتظر الإجابة بشغف.
"""

COMMON_INPUTS = """
================ بيانات المشروع ================

فكرة أو عنوان الفيديو:
{topic}

الجمهور المستهدف:
{audience}

المدة المستهدفة:
{target_minutes} دقيقة

المصادر والملاحظات المرفقة:
{sources}

=================================================
"""


# ============================================================
# العقول العشرة المحسّنة (The 10 Enhanced Prompts)
# ============================================================

MINDS = [

    # --------------------------------------------------------
    # العقل 1
    # --------------------------------------------------------
    {
        "id": 1,
        "name": "العقل 1 — تفكيك الجذر النفسي والمعرفي",
        "role": "Deep Problem & Insight Deconstructor",
        "description": """
مهمتك ليست كتابة السكريبت، بل التفتيش عن "الجذر الحقيقي" للموضوع.

فكّك الموضوع إلى:
1. الظاهر السطحي: ماذا يعتقد الناس أنه المشكلة؟ (مثلاً: الكسل، قلة الوقت، ضعف الإرادة).
2. الجذر العميق: ما الآلية النفسية أو العصبية الحقيقية التي تفكر خلف الستار؟ (مثلاً: الهروب من الألم، ميزان الدوبامين، الخوف من الفشل).
3. التناقضات والمفارقات: ما الشيء الغريب أو المتناقض في سلوك الإنسان تجاه هذا الموضوع؟
4. مفاهيم علمية أو كتب مرجعية: استخرج من معرفتك أو المصادر المرفقة أهم 3-5 مفاهيم أو تجارب (مثل أبحاث الدوبامين، تجارب علماء النفس، كتب شهيرة) واشرح كيف تفسر السلوك البشري بسلاسة.

المخرج المطلوب:
- صياغة المشكلة كـ "معاناة إنسانية" وليست مشكلة تقنية.
- قائمة بـ 8 صراعات يومية واقعية يعيشها المشاهد.
- 5 مفاهيم علمية/فكرية قوية تمثل عصب الفيديو.
""",
    },

    # --------------------------------------------------------
    # العقل 2
    # --------------------------------------------------------
    {
        "id": 2,
        "name": "العقل 2 — سيكولوجية المشاهد والحوار الداخلي",
        "role": "Viewer Psychology & Internal Monologue Expert",
        "description": """
أنت تدرس شخصية المشاهد في اللحظة التي يقرر فيها الضغط على الفيديو.

قم بما يلي:
1. ابنِ الحوار الداخلي (Monologue): اكتب 10 جمل شفهية بالعامية المصرية لما يقوله المشاهد لنفسه في سرّه وخجل من إظهاره (مثل: "أنا عارف إن الموبايل بياكل يومي، بس الواقع برا الموبايل موحش وممل").
2. فكك المشاعر: ما الخوف الدفين؟ ما الاعتقاد الخاطئ الذي يسلّي به نفسه؟ ما الحقيقة التي يحتاج لسماعها دون أن نجرحه؟
3. خريطة شعور المشاهد خلال دقائق الفيديو:
   - في البداية: "ده بيوصف اللي جوايا بالظبط!"
   - في المنتصف: "أنا عمري ما فكرت فيها بالطريقة دي..."
   - في النهاية: "أنا فهمت المشكلة صح، ودلوقتي عارف أنا هعمل إيه."

أخرج تحليلاً سيكولوجياً حاداً يركز على نقل المشاهد من الذنب والرغبة في الهروب إلى الاستبصار والارتياح.
""",
    },

    # --------------------------------------------------------
    # العقل 3
    # --------------------------------------------------------
    {
        "id": 3,
        "name": "العقل 3 — مهندس الزاوية الفريدة والفكرة الكبرى",
        "role": "The Big Idea & Paradox Strategist",
        "description": """
مهمتك العثور على "الزاوية الذهبية" (The Unique Angle) التي تجعل الفيديو غير مكرر.

اطرح 4 زوايا مختلفة كلياً للموضوع:
- زاوية قائمة على (المفارقة التاريخية أو الأدبية): مثل مقارنة كتابين أو زمنين.
- زاوية قائمة على (قلب المفاهيم): جعل الشيء السلبي يبدو كعرض وليس سبباً.
- زاوية قائمة على (رحلة إعادة تعريف): إعادة تعريف مفهوم شائع (مثل القراءة، النجاح، الإرادة).
- زاوية قائمة على (صراع الميكانيزم): كيف يخدعنا عقلنا لحمايتنا.

اختر **أقوى زاوية واحدة** وقم بصياغتها في:
1. الفكرة الكبرى (The Big Idea) في جملة واحدة مكثفة.
2. التحول الفكري (Paradigm Shift): من "المشاهد يعتقد X" إلى "المشاهد يكتشف Y".
3. السؤال المركزي الذي سيظل معلقاً طوال الفيديو.
""",
    },

    # --------------------------------------------------------
    # العقل 4
    # --------------------------------------------------------
    {
        "id": 4,
        "name": "العقل 4 — صانع الهوك والافتتاحية الآسرة",
        "role": "Master Hook & Cold Open Writer",
        "description": """
صمم البداية (أول 60 إلى 90 ثانية) التي تضمن عدم خروج المشاهد.

ابتعد عن الافتتاحيات التقليدية. اكتب 5 أساليب مختلفة للبداية بالعامية المصرية:
1. طريقة "المشهد الواقعي الدقيق" (الوصف الحسي للحظة يومية).
2. طريقة "المفارقة الصادمة" (مقارنة بين كائنين، كتابين، أو زمنين).
3. طريقة "الاعتراف المباشر" (صوت المتحدث وهو يشارك تجربة أو تساؤلاً يؤرقه).
4. طريقة "السؤال الوجودي/السيكولوجي" (طرح سؤال يضرب القناعة القديمة).
5. طريقة "القصة المبتدئة من المنتصف" (In media res).

ثم اختار الأفضل وابنِ **الافتتاحية الكاملة** لتسلسل أول 90 ثانية:
- المشهد الخاطف ← فتح المفارقة/المشكلة ← السؤال المعلق ← وعد الفيديو الشفاف (دون كليشيهات).
""",
    },

    # --------------------------------------------------------
    # العقل 5
    # --------------------------------------------------------
    {
        "id": 5,
        "name": "العقل 5 — مهندس الرحلة السردية والإيقاع",
        "role": "Narrative Architect & Pacing Master",
        "description": """
ابنِ الهيكل البنائي السلس للفيديو بحيث يبدو مثل قصة أو مقال متصل (Essay) وليس قائمة نقاط.

قسّم الفيديو إلى فصول درامية متسلسلة تناسب المدة المحددة:
1. الفصل الأول: صدمة التعرية (كشف المشكلة والواقع).
2. الفصل الثاني: تشريح الآلية (كيف يحدث هذا في الدماغ/الحياة؟).
3. الفصل الثالث: الخدعة/الكذبة الكبرى (لماذا تفشل الحلول التقليدية؟).
4. الفصل الرابع: نقطة التحول والمنظور الجديد (إعادة التعريف).
5. الفصل الخامس: التطبيق الواقعي السلس والخاتمة الإنسانية.

لكل فصل حدد:
- العنوان السردي المستفز.
- هدف الفصل الذهني والوجداني.
- الخيط الرابط الذي يسلم الفصل للفصل الذي يليه بدون فواصل مصطنعة.
""",
    },

    # --------------------------------------------------------
    # العقل 6
    # --------------------------------------------------------
    {
        "id": 6,
        "name": "العقل 6 — الحكواتي ومترجم التشبيهات",
        "role": "Storyteller, Analogies & Real-life Scenes",
        "description": """
مهمتك إعطاء الأفكار الجافة طعماً ولحماً وروحاً.

لكل فصل من فصول الرحلة السردية قدم:
1. تشبيه ملموس أصلي (Analogy) يقرب الفكرة النفسية أو العلمية (مثل تشبيه الدماغ بميزان اللذة والألم، أو تشبيه بناء العقل بالنادي والوصلات العصبية).
2. قصة أو مثال واقعي حقيقي (قصة عالم، تجربة شخصية، أو مشهد يومي يتكرر معنا جميعاً).
3. صياغة الحوارات والعبارات الشفهية التي تقال داخل المشهد.

أخرج "بنك التشبيهات والمشاهد السردية" الموزعة على فصول الفيديو.
""",
    },

    # --------------------------------------------------------
    # العقل 7
    # --------------------------------------------------------
    {
        "id": 7,
        "name": "العقل 7 — مهندس الاستبقاء وإعادة إشعال الشغف",
        "role": "Retention & Open-Loops Specialist",
        "description": """
مهمتك حماية السكريبت من الرتابة أو الهبوط في المنتصف.

راجع الهيكل وابنِ نظام الـ Retention:
1. زراعة الحلقات المفتوحة (Open Loops): أسئلة تفكر فيها الأذنان ولا تُجاب إلا لاحقاً.
2. نقاط إعادة الضبط (Pattern Breaks): لحظات يغير فيها المتحدث نبرته، يعترف بشرطه البشري، أو يطرح اعتراضاً قد يدور في عقل المشاهد ليرد عليه.
3. اختبار التدفق: التأكد من عدم وجود أكثر من 45 ثانية شرح نظري مستمر دون تحويله لمثال أو سؤال تفاعلي.

أخرج خطة الاستبقاء متضمنة التوجيهات الصوتية والتعبيرية.
""",
    },

    # --------------------------------------------------------
    # العقل 8
    # --------------------------------------------------------
    {
        "id": 8,
        "name": "العقل 8 — الكاتب الرئيسي للمسودة الأولى",
        "role": "Master Scriptwriter (Draft 1)",
        "description": """
اكتب المسودة الكاملة للسكريبت بناءً على كل ما أعدته العقول السابقة.

شروط المسودة:
1. اكتب السكريبت بالكامل بالعامية المصرية الحية الشفهية التي تُقال أمام الكاميرا تلقائياً.
2. اللغة يجب أن تسيل كالنهر: أفكار متصلة، جمل متنوعة الطول، نبرة صديق ذكي ودافئ.
3. ادمج القصص والتشبيهات والآليات العلمية داخل السرد كأنها جزء من الحكاية.
4. استخدم توجيهات إخراجية وأداء بسيط بين أقواس مثل: [وقف قصير]، [تغيير نبرة الصوت]، [مشهد أرشيفي].

ابدأ فوراً بكتابة النص كاملاً من البداية حتى نهاية السكريبت.
""",
    },

    # --------------------------------------------------------
    # العقل 9
    # --------------------------------------------------------
    {
        "id": 9,
        "name": "العقل 9 — المحرر القاسي وإزالة التكلف",
        "role": "Brutal Script Doctor & Humanizer",
        "description": """
اقرأ مسودة العقل 8 بعين محرر لا يرحم وبطريقة مشاهد يوتيوب ملول.

افحص ما يلي:
1. هل هناك أي جملة تبدو كأنها "مقال مكتوب" وليس "كلاماً يُقال"؟ حددها واكتب بديلها الشفهي.
2. هل يوجد حشو أو تكرار لنفس الفكرة للوصول للمدة؟ احذفه أو اقترح تعميقه بمثال.
3. هل نبرة المتحدث متعالية أو واعظة؟ حولها لنبرة مشاركة وتساؤل.
4. مراجعة سلاسة التنقل بين الأفكار.

أخرج تقريراً تحريرياً دقيقاً يحتوي على المقاطع الواجب تعديلها والصياغات البديلة.
""",
    },

    # --------------------------------------------------------
    # العقل 10
    # --------------------------------------------------------
    {
        "id": 10,
        "name": "العقل 10 — المخرج النهائي والكاتب العبقري",
        "role": "Final Master Writer (The Platinum Version)",
        "description": """
أنت الكاتب النهائي الذي يصيغ النسخة المعتمدة للتسجيل فوراً (Master Script).

قم بتطبيق ملاحظات العقل 9 على مسودة العقل 8، واكتب النص الكامل النهائي بنفس واحد، وروح واحدة، ولغة مصرية حية ودافئة وعميقة.

الشروط النهائية:
1. البداية فوراً بالسكريبت النهائي جاهزاً للقراءة والتسجيل.
2. أن تكون الخاتمة حازمة، دافئة، تعود لموقف البداية بوعي جديد، وتقدم تطبيقاً عملياً واقعياً ومستداماً دون مثاليات.
3. إضافة التوجيهات البصرية والإخراجية [B-Roll / أداء] بدقة.
4. في النهاية، أضف فقرة صغيرة مخصصة لملاحظات المراجعة أو المصادر.

ابدأ بكتابة السكريبت النهائي مباشرة دون أي مقدمات.
""",
    },
]


# ============================================================
# تمرير السياق بين العقول
# ============================================================

ROUTES = {
    1: [],
    2: [1],
    3: [1, 2],
    4: [2, 3],
    5: [1, 2, 3, 4],
    6: [1, 2, 3, 5],
    7: [3, 4, 5, 6],
    8: [1, 2, 3, 4, 5, 6, 7],
    9: [2, 3, 4, 7, 8],
    10: [1, 2, 3, 4, 5, 6, 7, 8, 9],
}


# ============================================================
# أدوات مساعدة
# ============================================================

def trim_text(text, max_chars=12000):
    if not text:
        return ""

    if len(text) <= max_chars:
        return text

    head_size = int(max_chars * 0.65)
    tail_size = max_chars - head_size

    return (
        text[:head_size]
        + "\n\n"
        + "[... تم اختصار جزء من المخرج للحفاظ على حجم السياق ...]"
        + "\n\n"
        + text[-tail_size:]
    )


def format_context(selected_outputs):
    if not selected_outputs:
        return "لا توجد مخرجات سابقة مرتبطة بهذه المهمة."

    parts = []

    for label, value in selected_outputs.items():
        parts.append(
            f"""
================ {label} ================

{trim_text(value)}

================ نهاية {label} ================
"""
        )

    return "\n".join(parts)


def extract_retry_delay(error_text, default_delay):
    match = re.search(
        r"retry(?:\s+in)?\s+([0-9]+(?:\.[0-9]+)?)\s*s",
        error_text,
        flags=re.IGNORECASE,
    )

    if match:
        try:
            return max(1, float(match.group(1)))
        except ValueError:
            pass

    return default_delay


def clean_model_name(name):
    if not name:
        return ""
    name = name.strip()
    if name.startswith("models/"):
        name = name[len("models/"):]
    return name


def ask_gemini(
    client,
    prompt,
    requested_model,
    fallback_model,
    max_retries=6,
    base_delay=5,
    status_slot=None,
):
    req_cleaned = clean_model_name(requested_model)
    fall_cleaned = clean_model_name(fallback_model)

    current_model = req_cleaned if req_cleaned else fall_cleaned
    fallback = fall_cleaned if fall_cleaned else current_model

    last_exc = None

    for attempt in range(1, max_retries + 1):

        try:
            response = client.models.generate_content(
                model=current_model,
                contents=prompt,
            )

            text = getattr(response, "text", "") or ""

            if not text.strip():
                raise RuntimeError("تم استلام رد فارغ من الموديل.")

            return text

        except Exception as exc:

            last_exc = exc

            error_text = str(exc)
            error_lower = error_text.lower()

            not_found = (
                "404" in error_text
                or "not_found" in error_lower
                or "not found" in error_lower
                or "no longer available" in error_lower
            )

            overloaded = (
                "429" in error_text
                or "503" in error_text
                or "resource_exhausted" in error_lower
                or "unavailable" in error_lower
                or "overloaded" in error_lower
                or "high demand" in error_lower
                or "quota" in error_lower
            )

            if not_found and current_model != fallback:

                if status_slot is not None:
                    status_slot.warning(
                        f"⚠️ الموديل '{current_model}' غير متاح. "
                        f"جاري التجربة بالموديل البديل '{fallback}'."
                    )

                current_model = fallback
                continue

            if overloaded and attempt < max_retries:

                exponential_delay = base_delay * (2 ** (attempt - 1))

                retry_delay = extract_retry_delay(
                    error_text,
                    exponential_delay,
                )

                wait_time = max(retry_delay, exponential_delay)
                wait_time = min(wait_time, 120)

                if status_slot is not None:
                    status_slot.info(
                        f"⏳ Gemini طلب الانتظار بسبب ضغط أو حد استخدام. "
                        f"المحاولة {attempt}/{max_retries}. "
                        f"الانتظار حوالي {int(wait_time)} ثانية..."
                    )

                time.sleep(wait_time)
                continue

            raise

    raise last_exc


def build_prompt(
    mind,
    topic,
    audience_text,
    source_text,
    target_minutes,
    outputs,
):

    route_ids = ROUTES.get(mind["id"], [])

    selected_outputs = {}

    for mind_id in route_ids:
        key = f"العقل {mind_id}"

        if key in outputs and outputs[key].strip():
            selected_outputs[key] = outputs[key]

    project_context = COMMON_INPUTS.format(
        topic=topic,
        audience=audience_text,
        target_minutes=target_minutes,
        sources=source_text.strip()
        if source_text and source_text.strip()
        else "لا توجد مصادر إضافية قدمها المستخدم.",
    )

    return f"""
{GLOBAL_RULES}

{project_context}

================================================
اسم العقل:
{mind["name"]}

التخصص:
{mind["role"]}
================================================

تعليماتك الخاصة:

{mind["description"]}

================================================
مخرجات العقول السابقة المرتبطة بمهمتك
================================================

{format_context(selected_outputs)}

================================================
طريقة التعامل مع المخرجات السابقة
================================================

1. استخدم تحليل العقول السابقة للوصول إلى عمق سردي حقيقي.
2. لا تكرر الكلام السابق بشكل تلخيصي؛ بل ابدَأ من حيث انتهوا وأضف القيمة الخاصة بعقلك.
3. التزم بالروح السردية البشرية والشفهية المطلوبة.
4. أنجز مهمة عقلك بأعلى جودة ممكنة.
"""


# ============================================================
# Session State
# ============================================================

if "pipeline_outputs" not in st.session_state:
    st.session_state.pipeline_outputs = {}

if "pipeline_topic" not in st.session_state:
    st.session_state.pipeline_topic = ""

if "last_error" not in st.session_state:
    st.session_state.last_error = ""


# ============================================================
# إدخال الموضوع
# ============================================================

topic = st.text_area(
    "🎯 اكتب فكرة أو عنوان الفيديو",
    height=150,
    placeholder=(
        "مثال: ليه بنسوّف الحاجات اللي بنحبها؟\n"
        "أو: أزمة التشتت والدوبامين: ليه بقيت تمل من كل حاجة بسرعة؟"
    ),
)


# ============================================================
# أزرار التحكم
# ============================================================

has_progress = len(st.session_state.pipeline_outputs) > 0

if has_progress:
    run_label = "▶️ كمّل من آخر عقل وقفنا عنده"
else:
    run_label = "🚀 شغّل نظام الـ10 عقول المطور"

col_run, col_reset = st.columns([3, 1])

with col_run:
    run_button = st.button(
        run_label,
        type="primary",
        use_container_width=True,
    )

with col_reset:
    reset_button = st.button(
        "🔄 ابدأ من جديد",
        use_container_width=True,
    )


if reset_button:

    st.session_state.pipeline_outputs = {}
    st.session_state.pipeline_topic = ""
    st.session_state.last_error = ""

    st.rerun()


if has_progress:

    completed = len(st.session_state.pipeline_outputs)

    st.info(
        f"📌 تم حفظ {completed} من {len(MINDS)} عقول. "
        "تقدر تكمل العملية في أي وقت."
    )


# ============================================================
# التشغيل
# ============================================================

if run_button:

    if not api_key.strip():
        st.error("❌ اكتب Gemini API Key الأول.")
        st.stop()

    if not topic.strip():
        st.warning("⚠️ اكتب فكرة الفيديو أو العنوان الأول.")
        st.stop()

    if (
        st.session_state.pipeline_topic
        and st.session_state.pipeline_topic != topic.strip()
    ):

        st.warning(
            "⚠️ تم تغيير موضوع الفيديو، لذلك سيتم بدء Pipeline جديد."
        )

        st.session_state.pipeline_outputs = {}

    st.session_state.pipeline_topic = topic.strip()
    st.session_state.last_error = ""

    try:

        client = genai.Client(
            api_key=api_key.strip()
        )

        outputs = st.session_state.pipeline_outputs

        total_minds = len(MINDS)
        completed_count = len(outputs)

        progress = st.progress(
            completed_count / total_minds
            if completed_count
            else 0
        )

        status = st.empty()

        st.divider()
        st.subheader("🧠 غرفة الكتابة")

        for index, mind in enumerate(MINDS):

            mind_key = f"العقل {mind['id']}"

            if mind_key in outputs:

                if show_all_outputs:

                    with st.expander(
                        f"✅ {mind['name']} — محفوظ",
                        expanded=False,
                    ):
                        st.markdown(outputs[mind_key])

                progress.progress(
                    (index + 1) / total_minds
                )

                continue

            status.info(
                f"🧠 العقل {mind['id']}/{total_minds} يعمل الآن: "
                f"{mind['name']}"
            )

            prompt = build_prompt(
                mind=mind,
                topic=topic.strip(),
                audience_text=audience,
                source_text=sources,
                target_minutes=target_minutes,
                outputs=outputs,
            )

            result = ask_gemini(
                client=client,
                prompt=prompt,
                requested_model=model_name,
                fallback_model=fallback_model,
                status_slot=status,
            )

            if not result.strip():
                raise RuntimeError(
                    f"العقل {mind['id']} أعاد نتيجة فارغة."
                )

            outputs[mind_key] = result

            st.session_state.pipeline_outputs = outputs

            if show_all_outputs:

                with st.expander(
                    f"🧠 {mind['name']}",
                    expanded=(mind["id"] >= 8),
                ):
                    st.markdown(result)

            progress.progress(
                (index + 1) / total_minds
            )

        # ====================================================
        # السكريبت النهائي
        # ====================================================

        final_script = outputs.get(
            "العقل 10",
            ""
        )

        status.success(
            "🎉 اكتمل نظام الـ10 عقول والسكريبت النهائي المطور جاهز."
        )

        st.divider()

        st.header("🎬 MASTER SCRIPT")

        st.text_area(
            "📜 النسخة النهائية المعتمدة للتسجيل",
            value=final_script,
            height=1000,
        )

        st.download_button(
            label="⬇️ تحميل السكريبت النهائي TXT",
            data=final_script,
            file_name="master_youtube_script.txt",
            mime="text/plain",
            use_container_width=True,
        )

        all_outputs_text = []

        for mind in MINDS:

            key = f"العقل {mind['id']}"

            if key in outputs:

                all_outputs_text.append(
                    f"""
====================================================
{mind["name"]}
====================================================

{outputs[key]}
"""
                )

        st.download_button(
            label="⬇️ تحميل تقرير جميع العقول بالكامل TXT",
            data="\n\n".join(all_outputs_text),
            file_name="all_minds_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    except Exception as e:
        st.session_state.last_error = str(e)
        st.error(f"❌ حدث خطأ أثناء المعالجة: {str(e)}")
