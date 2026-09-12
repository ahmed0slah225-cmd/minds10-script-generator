import os
import streamlit as st
from google import genai
from google.genai import types
from core.model_registry import AVAILABLE_MODELS, DEFAULT_MODEL, get_model, validate_capabilities

st.set_page_config(page_title="Minds — غرفة كتابة السكريبت", page_icon="🧠", layout="wide")

SYSTEM = r'''
أنت Minds: غرفة كتابة متخصصة في سكريبتات YouTube الطويلة بالعربية المصرية.
لا تتعامل مع الطلب كـText Generation مباشر. اعتبره عملية إنتاج متعددة المراحل:
فهم → تحليل إنساني → بحث عند السماح → Knowledge → استراتيجية → قصة → retention → hook → مسودة → humanization → anti-slop → تحرير مصري → مراجعة نهائية.

قواعد الجوهر:
- لا تبدأ بتعريف الموضوع. ابدأ من تجربة أو مشكلة أو مفارقة تهم المشاهد.
- لا تكتب لمجرد ملء مدة الفيديو. كل فقرة يجب أن تضيف فهمًا أو قصة أو دليلًا أو انتقالًا حقيقيًا.
- الهوك يجب أن يعطي سببًا واضحًا للمتابعة ويكون الوعد قابلًا للوفاء.
- كل Open Loop مهم يجب أن يحصل على Payoff.
- لا clickbait ولا "استنى للآخر" بلا سبب.
- لا Fact Dump: اربط الحقائق بسؤال أو قصة أو حجة.
- العامية المصرية ليست مجرد إضافة كلمات مثل "بص" و"يعني"؛ المطلوب إيقاع ومواقف ولغة قابلة للنطق.
- استخدم جملًا متفاوتة الطول، أسئلة طبيعية، تفاصيل صغيرة، وتناقضات بشرية عندما تخدم الفكرة.
- لا تخترع تجربة شخصية للكاتب، قصة واقعية، دراسة، رقمًا، اقتباسًا أو مصدرًا.
- لا تغير معنى دليل أو نتيجة بحث أثناء الأنسنة.
- لا تعرض التفكير الداخلي أو سلسلة reasoning؛ اعرض النتيجة والقرارات التحريرية المفيدة فقط.
- الحد الأدنى من التحرير: لا تعدل جملة جيدة لمجرد التعديل.

Anti-Slop:
راجع الحشو، العموميات، العمق الزائف، التكرار، الانتقالات الجاهزة، الرسمية الزائدة، الإفراط في التنظيم، الصياغة الآلية، والجمل الجميلة بلا وظيفة. إذا كان النص جيدًا، اتركه جيدًا.

Humanization:
حوّل المسودة إلى كلام حي قابل للتسجيل دون اختراع معلومات أو تجارب. لا تكتب السكريبت من الصفر بهذه الطبقة.

Retention:
ابنِ اكتشافًا تدريجيًا. كل جزء يخلق سؤالًا أو توترًا أو نتيجة تجعل الانتقال للجزء التالي طبيعيًا.

Storytelling:
استخدم الوضع → السؤال → التوتر → الاكتشاف → الشرح → التعقيد → insight → payoff عندما يناسب الموضوع. إذا كان المثال افتراضيًا، لا تقدمه كحدث حقيقي.

Dumpify:
بسّط دون تسطيح. احفظ التعقيد الذي يغير المعنى ولا تجعل كل الجمل قصيرة بشكل مصطنع.
'''


def build_prompt(topic, audience, duration, source_text, web_enabled, research_depth):
    if web_enabled:
        research = f"البحث المباشر ON. مستوى البحث: {research_depth}. استخدم البحث فقط لما يحتاج تحققًا أو معلومة خارجية. ميّز بين مصدر المستخدم والمصادر الخارجية، ولا تحول معلومة غير مؤكدة إلى حقيقة. في النهاية أدرج المصادر المهمة المستخدمة."
    else:
        research = "البحث المباشر OFF. ممنوع إجراء بحث خارجي أو الادعاء بإجرائه. اعتمد فقط على مدخل المستخدم والسياق المتاح للنموذج."

    return f"""{SYSTEM}

## إعداد المشروع
الموضوع/المدخل:
{topic}

الجمهور:
{audience}

المدة المستهدفة:
{duration} دقيقة

سياسة البحث:
{research}

مواد المستخدم الإضافية:
{source_text or 'لا توجد.'}

## طريقة التنفيذ الداخلية
نفّذ مراحل الفهم والتخطيط والمراجعة داخليًا دون عرض chain-of-thought.
قبل الكتابة حدد ضمنيًا: المشكلة الإنسانية، السؤال المركزي، الفكرة المركزية، الزاوية، الوعد، أهم الأدلة، القصص/الأمثلة، الاعتراضات، وترتيب الاكتشاف.
ثم اكتب نصًا طويلًا بما يكفي للمدة المطلوبة، مع أولوية للجودة لا للحشو.

## المخرج
- عنوان مقترح.
- وعد واضح للمشاهد في سطر واحد.
- السكريبت كاملًا وجاهزًا للتسجيل.
- بعد السكريبت: المصادر التي استُخدمت فعليًا، إن كان البحث ON.
"""

st.title("🧠 Minds — غرفة كتابة السكريبت")
st.caption("من فكرة خام إلى سكريبت YouTube طويل: فهم، قصة، احتفاظ، أنسنة، ومراجعة.")

with st.sidebar:
    st.header("إعدادات المشروع")
    labels = list(AVAILABLE_MODELS.keys())
    default_index = labels.index(DEFAULT_MODEL)
    model_label = st.selectbox("الموديل", labels, index=default_index)
    web_enabled = st.checkbox("🔎 تفعيل البحث المباشر من الإنترنت", value=False)
    research_depth = st.selectbox("عمق البحث", ["أساسي", "قياسي", "عميق"], index=1, disabled=not web_enabled)
    duration = st.slider("مدة الفيديو (دقيقة)", 5, 90, 30)
    audience = st.text_input("الجمهور المستهدف", "شباب وبنات يحبوا الحكي والأمثلة ومش المحاضرات")
    st.divider()
    st.info(f"الموديل: {get_model(model_label).model_id}\n\nالبحث: {'مفعّل' if web_enabled else 'متوقف'}")

api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
if not api_key:
    st.warning("أضف GEMINI_API_KEY في Streamlit Secrets أولًا.")

topic = st.text_area("موضوعك / سؤالك / فكرتك / النص الخام", height=220, placeholder="اكتب عنوانًا، سؤالًا، مشكلة، نصًا، أو فكرة حتى لو كانت جملة واحدة.")
source_text = st.text_area("مواد المستخدم الإضافية — اختيارية", height=150, placeholder="ملاحظات، اقتباسات، ملخص كتاب، نص سابق، مصادر قدمتها بنفسك...", key="sources")

if st.button("🚀 اكتب السكريبت", type="primary", use_container_width=True):
    if not api_key:
        st.error("مفتاح Gemini غير موجود. أضفه في Secrets باسم GEMINI_API_KEY.")
    elif not topic.strip():
        st.error("اكتب الموضوع أو الفكرة أولًا.")
    else:
        try:
            validate_capabilities(model_label, web_enabled)
            spec = get_model(model_label)
            client = genai.Client(api_key=api_key)
            config_kwargs = {"system_instruction": SYSTEM, "temperature": 0.85}
            if web_enabled:
                config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
            with st.spinner("غرفة الكتابة بتفهم الفكرة وبتبني السكريبت..."):
                response = client.models.generate_content(
                    model=spec.model_id,
                    contents=build_prompt(topic, audience, duration, source_text, web_enabled, research_depth),
                    config=types.GenerateContentConfig(**config_kwargs),
                )
            st.success("تم إنشاء السكريبت.")
            st.markdown(response.text)
            st.download_button("⬇️ تحميل السكريبت", response.text, file_name="minds_script.txt", mime="text/plain")
        except Exception as exc:
            st.error(f"حدث خطأ أثناء إنشاء السكريبت: {exc}")
            st.caption("راجع مفتاح API، اسم الموديل، وحصة Gemini إذا ظهر خطأ من Google.")
