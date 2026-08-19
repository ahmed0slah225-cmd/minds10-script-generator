import streamlit as st
import google.generativeai as genai
import time

# ============================================================
# إعداد الصفحة - لازم تكون أول سطر كود
# ============================================================
st.set_page_config(
    page_title="غرفة الـ 10 عقول - سكريبتات احترافية",
    page_icon="🧠",
    layout="wide",
)

# ============================================================
# واجهة المستخدم
# ============================================================
st.title("🎬 نظام الـ 10 عقول لصناعة المحتوى البشري")
st.write("النظام ده هيطلع لك سكريبت 30 دقيقة بالعامية المصرية الصايعة، بجذب كل 15 ثانية.")

# الإعدادات الجانبية
with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("ادخل Gemini API Key", type="password")
    
    # قائمة الموديلات المضمونة
    model_choice = st.selectbox(
        "اختر الموديل (Flash أسرع و Pro أدق)",
        ["gemini-1.5-flash", "gemini-1.5-pro"]
    )
    
    target_minutes = st.slider("مدة الفيديو (دقائق)", 10, 60, 30)
    st.divider()
    if st.button("🔄 مسح الذاكرة"):
        st.session_state.clear()
        st.rerun()

# ============================================================
# البرومبتات المصرية الـ 10 (الخلاصة القوية)
# ============================================================
GLOBAL_RULES = """
أنت كاتب محتوى مصري عبقري. اللغة: عامية مصرية شيك جداً (لغة مثقفين). 
المهمة: سكريبت فيديو 30 دقيقة. 
القاعدة الذهبية: كل 15 ثانية لازم المشاهد يتخطف (سؤال، قصة، إيفيه، معلومة صادمة). 
ابعد تماماً عن الفصحى وعن كليشيهات الذكاء الاصطناعي.
"""

MINDS = [
    {"id": 1, "name": "العقل 1: المُنقب", "task": "ابحث في علم الأعصاب وعلم النفس عن 'زتونة' الموضوع وطلع 10 مواقف مصرية واقعية."},
    {"id": 2, "name": "العقل 2: المحلل النفسي", "task": "حلل وجع المشاهد واكتب اعترافات بلسانه (زي: أنا بضحك على نفسي)."},
    {"id": 3, "name": "العقل 3: صائد الزاوية", "task": "لاقي فكرة 'خارج الصندوق' تقلب مفهوم المشاهد عن الموضوع."},
    {"id": 4, "name": "العقل 4: ملك الهوك", "task": "اكتب أقوى مقدمة 90 ثانية تخطف المشاهد بالعامية الصارخة."},
    {"id": 5, "name": "العقل 5: المهندس", "task": "ابني هيكل الفيديو (8 فصول) وازرع 'قنابل فضول' في نهاية كل فصل."},
    {"id": 6, "name": "العقل 6: الحكواتي", "task": "حول الشرح لقصص مصرية وتشبيهات من الشارع (ميكروباص، قهوة)."},
    {"id": 7, "name": "العقل 7: حارس الاستبقاء", "task": "ازرع محفزات انتباه كل 15 ثانية (إيفيه، سؤال، مفاجأة)."},
    {"id": 8, "name": "العقل 8: الكاتب الرئيسي", "task": "اكتب مسودة السكريبت الكاملة بالعامية المصرية (بشرية 100%)."},
    {"id": 9, "name": "العقل 9: المشرط القاسي", "task": "نقي الكلام من أي روح روبوتية واقطع الحشو الملل."},
    {"id": 10, "name": "العقل 10: المخرج النهائي", "task": "النسخة النهائية الجاهزة للتصوير مع توجيهات بصرية [بين أقواس]."}
]

# ============================================================
# منطق التشغيل
# ============================================================
if "outputs" not in st.session_state:
    st.session_state.outputs = {}

topic = st.text_area("🎯 فكرة الفيديو أو العنوان:", placeholder="مثلاً: ليه مش عارف أحافظ على عادة جديدة؟")

if st.button("🚀 تشغيل غرفة العمليات", type="primary"):
    if not api_key:
        st.error("❌ دخل الـ API Key في القائمة الجانبية")
    elif not topic:
        st.warning("⚠️ اكتب عنوان الفيديو")
    else:
        # إعداد المكتبة
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_choice)
        
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        for i, mind in enumerate(MINDS):
            mind_key = f"mind_{mind['id']}"
            if mind_key in st.session_state.outputs:
                progress_bar.progress((i + 1) / len(MINDS))
                continue
            
            with st.status(f"🧠 جاري تشغيل {mind['name']}...", expanded=True) as status:
                # سياق العقول السابقة
                prev_context = "\n".join([f"{MINDS[idx]['name']}: {st.session_state.outputs[f'mind_{idx+1}'][:500]}..." 
                                         for idx in range(i)])
                
                full_prompt = f"""
                {GLOBAL_RULES}
                الموضوع: {topic}
                المدة المطلوبة: {target_minutes} دقيقة
                مهمتك كـ ({mind['name']}): {mind['task']}
                
                سياق من العقول السابقة:
                {prev_context}
                """
                
                try:
                    response = model.generate_content(full_prompt)
                    st.session_state.outputs[mind_key] = response.text
                    st.markdown(response.text)
                    status.update(label=f"✅ {mind['name']} خلص مهمته", state="complete")
                except Exception as e:
                    st.error(f"خطأ في {mind['name']}: {str(e)}")
                    st.stop()
            
            progress_bar.progress((i + 1) / len(MINDS))

        if "mind_10" in st.session_state.outputs:
            st.success("🎉 السكريبت النهائي جاهز!")
            st.divider()
            st.header("📜 MASTER SCRIPT")
            st.markdown(st.session_state.outputs["mind_10"])
            st.download_button("⬇️ تحميل السكريبت", st.session_state.outputs["mind_10"], "script.txt")
