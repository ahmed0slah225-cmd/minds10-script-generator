import streamlit as st
from google import genai
from google.genai import types

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="مولد اسكريبتات يوتيوب العميقة",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 مولد اسكريبتات الفيديوهات الطويلة (أسلوب التفكيك والشرح)")
st.write("قم بإدخال نص أو موضوع الكتاب للحصول على اسكريبت مقسم إلى فصول بأسلوب شارح ومبسط للجمهور.")

# 2. القائمة الجانبية والإدخالات
with st.sidebar:
    st.header("⚙️ إعدادات الاتصال")
    api_key_input = st.text_input("أدخل GEMINI API KEY:", type="password")
    st.info("يمكنك الحصول على المفتاح من Google AI Studio.")

topic_input = st.text_area("أدخل موضوع الفيديو أو نص/خلاصة الكتاب المراد شرحه:", height=150)
notes_input = st.text_input("ملاحظات إضافية (أمثلة معينة، توجيهات إضافية):")

def create_script_generator(api_key: str):
    system_instruction = """
 أنت صانع محتوى خبير ومعدّ اسكريبتات للفيديوهات الطويلة (مثل يوتيوب).
 وظيفتك الرئيسية هي شرح وتبسيط الأفكار المفاهيمية أو النصوص والكتب للجمهور بأسلوب تفكيكي عميق وقريب من القلب.

 CRITICAL INSTRUCTION (تنبيه حاسم):
 - لا تتحدث إطلاقًا بصيغة المتحدث الأصلي للكتاب كأنك صاحب التجربة الشخصية المباشرة (إلا إذا تم استشهاده كطرف ثالث).
 - دورك دائمًا هو "الشارح والمبسط" الذي يأخذ يد المشاهد ("من عقلي لعقلك") ليغوص معه في رحلة فهم الكتاب أو الموضوع.

 خطة وهيئة الاسكريبت المطلوب لتطابق السلاسل الفكرية والعميقة:
 1. المقدمة (الفصل 1): تساؤلات وجودية ومقارنات تشويقية وعبارات تواصل دافئة.
 2. التأسيس العلمي والقصصي (الفصول الوسطى): تبسيط المفاهيم والأبحاث بأمثلة تشبيهية بسيطة، فضح كذبات الدماغ.
 3. الحلول والخطوات (الفصول الأخيرة): تقديم الحلول بالتدرج المنطقي ومخاطبة النفس التواقة.
 4. الخاتمة: عبارة ختامية دافئة، تقييم القيمة المقدمة، والدعوة لمشاركة المقطع.

 طابع اللغة والأسلوب:
 - لغة عربية بيضاء/سلسة تجمع بين العمق والتبسيط الشفهي.
 - تقسيم الاسكريبت إجباريًا إلى فصول مسمّاة (الفصل 1: ... ، الفصل 2: ...).
 """

    client = genai.Client(api_key=api_key)
    return client, system_instruction

# 3. التشغيل والتوليد
if st.button("🚀 توليد الاسكريبت الآن", type="primary"):
    if not api_key_input:
        st.error("⚠️ يرجى إدخال الـ API Key في القائمة الجانبية أولاً!")
    elif not topic_input.strip():
        st.warning("⚠️ يرجى إدخال موضوع أو نص الكتاب أولاً!")
    else:
        try:
            with st.spinner("جاري الاتصال بـ Gemini وتوليد الاسكريبت..."):
                client, system_instruction = create_script_generator(api_key_input)

                user_prompt = f"""
 المطلوب: كتابة اسكريبت فيديو طويل وشامل ومفصل بناءً على الموضوع/النص التالي:

 [الموضوع أو الكتاب/النص المراد شرحه]:
 {topic_input}

 [ملاحظات إضافية]:
 {notes_input}
 """

                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    top_p=0.95,
                )

                # استخدام موديل Flash المجاني والسريع لتفادي خطأ الكوتا (429)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_prompt,
                    config=config
                )

                st.success("✅ تم توليد الاسكريبت بنجاح!")
                st.markdown("---")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء الاتصال أو التوليد:\n\n`{str(e)}`")
            st.info("إذا استمر الخطأ، انتظر 30 ثانية وحاول مجددًا.")
