import time
import streamlit as st
from google import genai

# ============================================================
# إعداد الصفحة
# ============================================================

st.set_page_config(
    page_title="غرفة عمليات اليوتيوب - الـ 10 عقول",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 نظام الـ 10 عقول لصناعة اسكريبتات خاطفة")
st.write(
    "هذا النظام مصمم لإنتاج فيديوهات طويلة (حتى 30 دقيقة) بأسلوب بشري مصري، "
    "بيخطف المشاهد في أول 15 ثانية وبيحافظ عليه مستمتع لآخر ثانية."
)

# ============================================================
# الإعدادات في الشريط الجانبي
# ============================================================

with st.sidebar:
    st.header("⚙️ الإعدادات")

    api_key = st.text_input("Google Gemini API Key", type="password")
    model_name = st.text_input("اسم الموديل الأساسي", value="gemini-2.0-flash")
    fallback_model = st.text_input("الموديل البديل", value="gemini-1.5-flash")
    target_minutes = st.slider("مدة الفيديو المستهدفة (بالدقائق)", 10, 60, 30, 5)

    audience = st.text_area(
        "الجمهور المستهدف",
        value="شباب وبنات مصريين وعرب، أذكياء، بيكرهوا الكلام المكرر والتنمية البشرية السطحية."
    )

    sources = st.text_area("مصادر إضافية (اختياري)", placeholder="كتاب، بحث، أو ملاحظات...")

    st.divider()
    show_all_outputs = st.checkbox("عرض مخرجات كل العقول", value=True)

# ============================================================
# القواعد والبرومبتات (تم تصحيح علامات التنصيص)
# ============================================================

GLOBAL_RULES = """
أنت كاتب محتوى بشري مصري محترف. مهمتك إنتاج فيديو يوتيوب خاطف للانتباه.
القواعد:
1. اللغة: عامية مصرية شيك، لغة مثقفين. ابعد عن الفصحى تماماً.
2. الـ 15 ثانية: كل 15 ثانية لازم يكون فيه تغيير (سؤال، قصة، معلومة، نكتة).
3. لا للمقدمات: ادخل في الموضوع فوراً.
4. التشبيهات: من الشارع المصري (الميكروباص، الموبايل، الكورة).
"""

MINDS = [
    {"id": 1, "name": "العقل 1: المُنقب عن الزتونة", "role": "Researcher", "description": "ابحث في علم الأعصاب وعلم النفس عن الموضوع. طلع الزتونة من كتب تقيلة زي Dopamine Nation. استخرج 5 حقائق صادمة و10 مواقف مصرية واقعية."},
    {"id": 2, "name": "العقل 2: المحلل النفسي", "role": "Psychologist", "description": "ادخل جوه دماغ المشاهد. هو بيحس بإيه؟ اكتب 15 جملة اعتراف بالعامية (زي: أنا بضحك على نفسي). حدد أعمق خوف عنده."},
    {"id": 3, "name": "العقل 3: صائد الزاوية الصايعة", "role": "Strategist", "description": "لاقي خبطة مختلفة. لو الموضوع عن الثقة، متقولش ازاي تبقى واثق، قول ليه الثقة فخ؟ حدد التحول المركزي للمشاهد."},
    {"id": 4, "name": "العقل 4: ملك الهوك المصري", "role": "Hook Master", "description": "اكتب 10 مقدمات (Hooks) بالعامية الصارخة. ابدأ بجملة تخلي المشاهد يتصدم أو يحس إنك مراقبه. ابني أفضل هوك لـ 90 ثانية."},
    {"id": 5, "name": "العقل 5: مهندس الرحلة", "role": "Architect", "description": "قسم الفيديو لـ 8 فصول بأسماء مثيرة. ازرع قنابل فضول (Open Loops) في آخر كل فصل عشان يكمل للآخر."},
    {"id": 6, "name": "العقل 6: الحكواتي المصري", "role": "Storyteller", "description": "حول العلم لقصص ناس من الشارع. استخدم تشبيهات مصرية عبقرية. خلي الكلام يلمس القلب قبل الدماغ."},
    {"id": 7, "name": "العقل 7: مهندس الـ 15 ثانية", "role": "Retention", "description": "حط محفزات انتباه كل 15 ثانية حرفياً (إيفيه، سؤال مفاجئ). طبق اختبار الخسارة على كل جزء."},
    {"id": 8, "name": "العقل 8: الكاتب الرئيسي", "role": "Lead Writer", "description": "اكتب سكريبت كامل (حوالي 4500 كلمة). اللغة عامية مصرية حية. ادمج العلم بالقصص بالتشويق في نسيج واحد."},
    {"id": 9, "name": "العقل 9: المشرط القاسي", "role": "Script Doctor", "description": "طلع أي جملة تحس إنها روبوت أو كلام كتب وحولها لمصري أصلي. اقطع الحشو وطلع 10 نقط ضعف."},
    {"id": 10, "name": "العقل 10: المخرج النهائي", "role": "Final Master", "description": "أعد كتابة السكريبت النهائي. ضيف توجيهات إخراجية وبصرية [بين أقواس]. الناتج لازم يكون بشري ومصري 100%."},
]

ROUTES = {1:[], 2:[1], 3:[1,2], 4:[2,3], 5:[1,2,3,4], 6:[1,2,3,5], 7:[3,4,5,6], 8:[1,2,3,4,5,6,7], 9:[2,3,4,7,8], 10:[1,2,3,4,5,6,7,8,9]}

# ============================================================
# منطق التشغيل
# ============================================================

if "pipeline_outputs" not in st.session_state:
    st.session_state.pipeline_outputs = {}

topic = st.text_area("🎯 عنوان الفيديو أو الفكرة اللي في دماغك:", height=100)

if st.button("🚀 ابدأ غرفة العمليات", type="primary", use_container_width=True):
    if not api_key:
        st.error("❌ من فضلك دخل الـ API Key في القائمة الجانبية.")
    elif not topic:
        st.warning("⚠️ دخل الموضوع الأول.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            outputs = st.session_state.pipeline_outputs
            progress = st.progress(0)
            status = st.empty()
            
            for i, mind in enumerate(MINDS):
                mind_key = f"العقل {mind['id']}"
                if mind_key in outputs:
                    progress.progress((i+1)/len(MINDS))
                    continue
                
                status.info(f"جاري عمل {mind['name']}...")
                
                # بناء السياق
                prev_context = ""
                for mid in ROUTES[mind['id']]:
                    prev_context += f"\nمخرج العقل {mid}:\n{outputs.get(f'العقل {mid}', '')}\n"
                
                prompt = f"{GLOBAL_RULES}\nالموضوع: {topic}\n{mind['description']}\nسياق سابق:\n{prev_context}"
                
                # استدعاء الموديل
                response = client.models.generate_content(model=model_name, contents=prompt)
                outputs[mind_key] = response.text
                st.session_state.pipeline_outputs = outputs
                
                if show_all_outputs:
                    with st.expander(f"✅ {mind['name']}"):
                        st.markdown(outputs[mind_key])
                progress.progress((i+1)/len(MINDS))
            
            status.success("🎉 اكتمل الاسكريبت النهائي!")
            st.divider()
            st.header("📜 الاسكريبت النهائي")
            st.markdown(outputs["العقل 10"])
            st.download_button("⬇️ تحميل الاسكريبت", outputs["العقل 10"], file_name="final_script.txt")
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

if st.button("🔄 مسح الذاكرة"):
    st.session_state.pipeline_outputs = {}
    st.rerun()
