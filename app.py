import streamlit as st
from google import genai

# 1. إعداد واجهة الموقع والـ API
st.set_page_config(page_title="نظام العقول الـ 10 للسكريبتات", page_icon="🧠", layout="wide")

st.title("🧠 نظام الـ 10 عقول لكتابة السكريبتات")
st.write("أدخل الفكرة أو النص الأساسي، وسيقوم النظام بتمريرها على 10 عقول ذكاء اصطناعي متخصصة للوصول للسكريبت النهائي.")

# إدخال الـ API Key في الشريط الجانبي
with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("أدخل Google Gemini API Key:", type="password")
    st.info("المفتاح مجاني ويمكنك الحصول عليه من Google AI Studio.")

# 2. تعريف العقول الـ 10 (Prompts)
MINDS = [
    {
        "name": "العقل 1: خبير الخطاف (Hook Master)",
        "prompt": "أنت خبير في خطف انتباه المشاهد في أول 3 إلى 5 ثوانٍ. حلل الفكرة واكتب 3 اقتراحات لافتتاحية قوية جداً (Hook) بأسلوب تشويقي يناسب الفيديوهات القصيرة واليوتيوب."
    },
    {
        "name": "العقل 2: مهندس الهيكل والبناء (Structure Architect)",
        "prompt": "بناءً على الفكرة والافتتاحية المختارة، ضع هيكلاً متماسكاً للسكريبت مقسم إلى: (مقدمة، المشكلة الأساسية، الحل والتفاصيل، الخاتمة والدعوة للإجراء)."
    },
    {
        "name": "العقل 3: خبير الاحتفاظ بالمشاهد (Retention Expert)",
        "prompt": "راجع الهيكل وضِف نقاط تشويق (Open Loops/Pattern Interrupts) كل 15-20 ثانية للحفاظ على انتباه المشاهد وعدم التخطي."
    },
    {
        "name": "العقل 4: خبير النبرة والأسلوب (Tone & Voice)",
        "prompt": "عدّل أسلوب الكتابة ليكون بلغة عامية بسيطة، جذابة، قريبة من القلب، مع تجنب التعقيد والكلمات الصعبة."
    },
    {
        "name": "العقل 5: مخرج المؤثرات البصرية والسمعية (SFX/VFX Director)",
        "prompt": "أضف توجيهات المونتاج للسكريبت بين أقواس مثل: [صوت زجاج ينكسر]، [تغيير الزاوية]، [عرض نص على الشاشة]، [B-Roll لصورة معينة]."
    },
    {
        "name": "العقل 6: صانع التشبيهات والأمثلة (Relatability Engine)",
        "prompt": "ضِف تشبيهات قصيرة وأمثلة واقعية من الحياة اليومية توضح الفكرة للمشاهد بسرعة وبشكل ممتع."
    },
    {
        "name": "العقل 7: مراجع المنطق والسلاسة (Logic & Flow Checker)",
        "prompt": "راجع السكريبت للتأكد من منطقية الانتقال بين الجمل والفقرات، واحذف أي تكرار أو حشو غير ضروري."
    },
    {
        "name": "العقل 8: محفز التفاعل (CTA Specialist)",
        "prompt": "صمم خاتمة قوية تحتوي على دعوة ذكية للتفاعل (تعليق، مشاركة، أو سؤال يفتح نقاش في التعليقات) بدون أسلوب تقليدي ممل."
    },
    {
        "name": "العقل 9: المصحح والمصقل اللغوي (Polishing & Pacing)",
        "prompt": "راجع الإيقاع الصوتي للجمل لتكون سهلة القراءة والتحدث أثناء التسجيل، وتأكد من جودة الصياغة العامة."
    },
    {
        "name": "العقل 10: المخرج النهائي (Final Script Assembly)",
        "prompt": "قم بتجميع كل الإضافات والتعديلات السابقة في سكريبت نهائي متكامل وجاهز للقراءة فوراً أمام الكاميرا، موضحاً فيه نص المذيع وتوجيهات المونتاج بشكل منظم."
    }
]

# 3. واجهة المدخلات وتشغيل السلسلة
topic = st.text_area("أدخل موضوع أو فكرة الفيديو هنا:", height=120, placeholder="مثال: كيف تدير وقتك كصانع محتوى بدون ما تجيلك حالة احتراق شغف؟")

if st.button("🚀 ابدأ المعالجة عبر الـ 10 عقول", type="primary"):
    if not api_key:
        st.error("يرجى إدخال Gemini API Key في الشريط الجانبي أولاً!")
    elif not topic:
        st.warning("يرجى إدخال فكرة الفيديو!")
    else:
        try:
            client = genai.Client(api_key=api_key)
            current_context = f"الفكرة الأساسية للفيديو:\n{topic}"
            progress_bar = st.progress(0)
            status_text = st.empty()

            st.divider()
            st.subheader("📊 مراحل معالجة العقول:")

            # قائمة الموديلات البديلة بالترتيب
            candidate_models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-1.5-pro"]

            for i, mind in enumerate(MINDS):
                status_text.text(f"جاري المعالجة بواسطة: {mind['name']}...")
                
                prompt_text = f"""
                أنت تعمل كـ {mind['name']}.
                مهمتك المحددة: {mind['prompt']}

                السياق والمخرجات السابقة حتى الآن:
                ---
                {current_context}
                ---

                قم بإجراء مهمتك المحددة بناءً على كل ما سبق وتقديم النتيجة المحدثة أو المضافة.
                """

                # محاولة الاتصال بـ API عبر قائمة الموديلات البديلة
                response = None
                last_error = None
                for model_name in candidate_models:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt_text
                        )
                        if response:
                            break
                    except Exception as err:
                        last_error = err
                        continue

                if not response:
                    raise Exception(f"تعذر الاتصال بجميع الموديلات: {last_error}")

                mind_output = response.text
                current_context += f"\n\n--- [تعديلات {mind['name']}] ---\n{mind_output}"

                with st.expander(f"✅ {mind['name']}", expanded=(i == len(MINDS) - 1)):
                    st.markdown(mind_output)

                progress_bar.progress((i + 1) / len(MINDS))

            status_text.success("🎉 تم الانتهاء من إعداد السكريبت النهائي بنجاح!")
            
            st.divider()
            st.subheader("📜 السكريبت النهائي:")
            st.text_area("النتيجة النهائية جاهزة للنسخ:", value=mind_output, height=300)

        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بالـ API: {e}")
