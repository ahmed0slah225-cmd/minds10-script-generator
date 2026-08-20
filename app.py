import time
import re
import streamlit as st
from google import genai

# ============================================================
# إعداد الصفحة
# ============================================================

st.set_page_config(
    page_title="غرفة كتابة يوتيوب - 10 عقول",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 غرفة كتابة سكريبت يوتيوب - نظام 10 عقول")
st.write(
    "نظام كتابة متعدد المراحل: بحث وفهم للمشاهد ← زاوية جديدة ← هوك ← رحلة سردية "
    "← قصص وأمثلة ← هندسة الاستبقاء ← مسودة كاملة ← Humanization ← نقد قاسٍ "
    "← إعادة كتابة نهائية جاهزة للتسجيل."
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
    
    st.info("💡 تم ضبط النظام ليستخدم gemini-3.6-flash السريع للعقول الأولى، وgemini-3.1-pro-preview العبقري للعقول الأخيرة مع تحويل تلقائي عند ضغط الكوتا.")

    target_minutes = st.slider(
        "مدة الفيديو المستهدفة بالدقائق",
        min_value=10,
        max_value=60,
        value=15,
        step=5,
    )

    audience = st.text_area(
        "الجمهور المستهدف",
        value=(
            "شباب وبنات من 18 إلى 35 سنة، عايزين يفهموا نفسهم ويحسنوا حياتهم، "
            "لكن بيكرهوا الكلام الوعظي والتنمية البشرية المكررة، وبيخرجوا بسرعة "
            "لو حسوا إن الفيديو بيحاضر عليهم أو بيقول كلام عام."
        ),
        height=130,
    )

    sources = st.text_area(
        "مصادر أو كتب أو ملاحظات اختيارية",
        placeholder="اكتب هنا كتاب، بحث، ملاحظات، أفكار، أو أي مادة عايز السكريبت يعتمد عليها.",
        height=140,
    )

    st.divider()

    show_all_outputs = st.checkbox(
        "عرض مخرجات كل العقول",
        value=True,
    )

# ============================================================
# القواعد العامة
# ============================================================

GLOBAL_RULES = """
أنت عضو داخل غرفة كتابة حقيقية لفيديو يوتيوب طويل.

الهدف النهائي ليس إنتاج مقال، ولا تلخيص كتاب، ولا محاضرة في علم النفس.
الهدف هو بناء تجربة مشاهدة تجعل شخصًا حقيقيًا يشعر في أول لحظات أن:
"الفيديو ده بيتكلم عن حاجة أنا عايشها فعلاً"
ثم يكمل لأنه يريد أن يعرف كيف تتكشف الفكرة.

اكتب بالعربية العامية المصرية الطبيعية المناسبة للكلام أمام الكاميرا.

القواعد غير القابلة للكسر:
1. لا تبدأ بتحية.
2. لا تبدأ بتعريف أكاديمي.
3. ممنوع: "في الفيديو ده هنتكلم عن".
4. ممنوع: "متعرفش إن..." و"هل تعلم أن..." وأي كليشيه مشابه.
5. ممنوع استخدام "استنى للنهاية" كحيلة للاستبقاء.
6. لا تخترع دراسة أو رقمًا أو تجربة أو اسم عالم.
7. ابدأ بما يعيشه الإنسان، ثم فسّر لماذا قد يحدث.
8. المقصود بالاستبقاء: تغيير حقيقي في الحالة (موقف، اكتشاف، قصة، مثال).
9. لا تعامل المشاهد كأنه غبي، ولا تحاضر عليه.
10. لا تستخدم لغة مقالات مثل: "في عالم يتسم بـ"، "من الجدير بالذكر".
11. الفيديو يجب أن يكون رحلة اكتشاف واحدة لها بداية وتحول ونهاية.
"""

COMMON_INPUTS = """
================ بيانات المشروع ================
فكرة أو عنوان الفيديو:
{topic}
الجمهور المستهدف:
{audience}
المدة المستهدفة:
{target_minutes} دقيقة
مصادر أو كتب:
{sources}
=================================================
"""

# ============================================================
# العقول العشرة
# ============================================================

MINDS = [
    {
        "id": 1,
        "name": "العقل 1 — الباحث ومفكك المشكلة",
        "role": "Researcher + Problem Deconstructor",
        "description": "حلل المشكلة التي يعيشها المشاهد، استخرج الطبقات النفسية العميقة، والأفكار الشائعة الخاطئة. لا تكتب سكريبت، فقط تحليل."
    },
    {
        "id": 2,
        "name": "العقل 2 — محلل نفسية المشاهد",
        "role": "Viewer Psychologist",
        "description": "ابنِ شخصية المشاهد النفسية من الداخل وقم بتفكيك الصراعات الدفينة التي يخجل من الاعتراف بها. استخرج أعمق ألم وأكبر سوء فهم عن نفسه."
    },
    {
        "id": 3,
        "name": "العقل 3 — صائد الزاوية والاختراق",
        "role": "Big Idea + Unique Angle Strategist",
        "description": "ابحث عن زاوية فيها تناقض أو إعادة تفسير لسبب المشكلة. حدد 'التحول المركزي للفيديو'. لا تكتب الهوك النهائي."
    },
    {
        "id": 4,
        "name": "العقل 4 — مهندس الهوك والبداية",
        "role": "Hook + Opening Specialist",
        "description": "اكتب 3 افتتاحيات قوية بالعامية المصرية تخطف المشاهد في أول 90 ثانية. اختر أفضل واحدة واكتبها بالتفصيل."
    },
    {
        "id": 5,
        "name": "العقل 5 — مهندس الرحلة السردية",
        "role": "Narrative Architect",
        "description": "قسّم الفيديو إلى فصول (Chapters) تتناسب مع المدة المطلوبة. حدد لكل فصل الزمن، الهدف الدرامي، وما سيكتشفه المشاهد."
    },
    {
        "id": 6,
        "name": "العقل 6 — راوي القصص ومترجم الأفكار",
        "role": "Storyteller + Human Examples",
        "description": "أخرج بنك مشاهد وقصص وأمثلة وتشبيهات من الواقع المصري لكل فصل من فصول الرحلة."
    },
    {
        "id": 7,
        "name": "العقل 7 — مهندس الاستبقاء والإيقاع",
        "role": "Retention + Rhythm Architect",
        "description": "ابنِ Retention Blueprint. حدد أخطر 10 أماكن قد يمل فيها المشاهد وضع حلولاً وتوجيهات لكسر النمط."
    },
    {
        "id": 8,
        "name": "العقل 8 — الكاتب الرئيسي للمسودة",
        "role": "Long-form YouTube Script Writer",
        "description": "أنت الكاتب الرئيسي. بناءً على كل ما سبق، اكتب المسودة الأولى الكاملة للسكريبت بالعامية المصرية الطبيعية."
    },
    {
        "id": 9,
        "name": "العقل 9 — المحرر البشري القاسي",
        "role": "Humanization Editor + Brutal Script Doctor",
        "description": "افحص المسودة بقسوة كأنك مشاهد غير صبور. أخرج تقرير بأخطر 15 نقطة ضعف، ملل، أو تصنع في اللهجة واقترح تعديلات."
    },
    {
        "id": 10,
        "name": "العقل 10 — الكاتب النهائي والمخرج الداخلي",
        "role": "Final Master Writer + Viewer Advocate",
        "description": "أنت الساحر الأخير. أعد كتابة النسخة النهائية الكاملة للسكريبت بالعامية المصرية بناءً على المسودة وتعديلات المحرر القاسي، وأضف توجيهات بصرية [B-Roll]."
    },
]

ROUTES = {
    1: [], 2: [1], 3: [1, 2], 4: [2, 3], 5: [1, 2, 3, 4],
    6: [1, 2, 3, 5], 7: [3, 4, 5, 6], 8: [1, 2, 3, 4, 5, 6, 7],
    9: [2, 3, 4, 7, 8], 10: [1, 2, 3, 4, 5, 6, 7, 8, 9],
}

# ============================================================
# أدوات مساعدة
# ============================================================

def trim_text(text, max_chars=12000):
    if not text: return ""
    if len(text) <= max_chars: return text
    return text[:int(max_chars * 0.65)] + "\n\n[... تم اختصار جزء ...]\n\n" + text[-(max_chars - int(max_chars * 0.65)):]

def format_context(selected_outputs):
    if not selected_outputs: return "لا توجد مخرجات سابقة."
    return "\n".join([f"==== {k} ====\n{trim_text(v)}\n" for k, v in selected_outputs.items()])

def ask_gemini(client, prompt, mind_id, status_slot):
    # استخدام الموديلات الحديثة المطلوبة من جوجل
    primary_model = "gemini-3.1-pro-preview" if mind_id >= 8 else "gemini-3.6-flash"
    fallback_model = "gemini-3.6-flash"
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=primary_model,
                contents=prompt,
            )
            text = getattr(response, "text", "") or ""
            if not text.strip(): raise RuntimeError("رد فارغ من النموذج")
            return text
        except Exception as exc:
            error_text = str(exc).lower()
            
            # التحويل التلقائي عند انتهاء الكوتا أو عدم توفر الموديل
            if ("429" in error_text or "quota" in error_text or "exhausted" in error_text or "404" in error_text) and primary_model != fallback_model:
                status_slot.warning(f"⚠️ يتعذر استخدام {primary_model}. جاري التحويل التلقائي إلى {fallback_model} لتكملة السكريبت...")
                primary_model = fallback_model
                time.sleep(2)
                continue
                
            if attempt < max_retries:
                wait_time = 10 * attempt
                status_slot.warning(f"⏳ الانتظار {wait_time} ثواني ثم إعادة المحاولة... ({attempt}/{max_retries})")
                time.sleep(wait_time)
                continue
                
            raise RuntimeError(f"فشل الاتصال بـ Gemini: {str(exc)}")

def build_prompt(mind, topic, audience_text, source_text, target_minutes, outputs):
    selected_outputs = {f"العقل {i}": outputs[f"العقل {i}"] for i in ROUTES.get(mind["id"], []) if f"العقل {i}" in outputs}
    project_context = COMMON_INPUTS.format(
        topic=topic, audience=audience_text, target_minutes=target_minutes,
        sources=source_text.strip() if source_text else "لا توجد مصادر إضافية."
    )
    return f"{GLOBAL_RULES}\n{project_context}\n==== اسم العقل: {mind['name']} ====\nتعليماتك: {mind['description']}\n\nمخرجات سابقة:\n{format_context(selected_outputs)}"

# ============================================================
# Session State & UI
# ============================================================

if "pipeline_outputs" not in st.session_state: st.session_state.pipeline_outputs = {}
if "pipeline_topic" not in st.session_state: st.session_state.pipeline_topic = ""

topic = st.text_area("🎯 اكتب فكرة أو عنوان الفيديو", height=100)

has_progress = len(st.session_state.pipeline_outputs) > 0
col1, col2 = st.columns([3, 1])

with col1:
    run_btn = st.button("▶️ كمّل من آخر عقل" if has_progress else "🚀 شغّل نظام الـ10 عقول", type="primary", use_container_width=True)
with col2:
    if st.button("🔄 ابدأ من جديد", use_container_width=True):
        st.session_state.pipeline_outputs = {}
        st.session_state.pipeline_topic = ""
        st.rerun()

# ============================================================
# التشغيل الرئيسي
# ============================================================

if run_btn:
    if not api_key: st.error("❌ اكتب API Key أولاً."); st.stop()
    if not topic: st.warning("⚠️ اكتب فكرة الفيديو."); st.stop()

    if st.session_state.pipeline_topic and st.session_state.pipeline_topic != topic.strip():
        st.session_state.pipeline_outputs = {}
    st.session_state.pipeline_topic = topic.strip()

    try:
        client = genai.Client(api_key=api_key.strip())
        outputs = st.session_state.pipeline_outputs
        progress_bar = st.progress(len(outputs) / len(MINDS) if outputs else 0)
        status_msg = st.empty()

        for index, mind in enumerate(MINDS):
            m_key = f"العقل {mind['id']}"
            if m_key in outputs:
                progress_bar.progress((index + 1) / len(MINDS))
                continue

            status_msg.info(f"🧠 جاري تشغيل: {mind['name']}...")
            prompt = build_prompt(mind, topic, audience, sources, target_minutes, outputs)
            
            result = ask_gemini(client, prompt, mind["id"], status_msg)
            outputs[m_key] = result
            st.session_state.pipeline_outputs = outputs
            
            if show_all_outputs:
                with st.expander(f"✅ {mind['name']}", expanded=(mind["id"] >= 8)):
                    st.markdown(result)
                    
            progress_bar.progress((index + 1) / len(MINDS))

        status_msg.success("🎉 السكريبت النهائي جاهز!")
        st.subheader("🎬 النسخة النهائية (Master Script)")
        st.text_area("", value=outputs.get("العقل 10", ""), height=600)
        
    except Exception as e:
        st.error(f"❌ حدث خطأ: {str(e)}")
