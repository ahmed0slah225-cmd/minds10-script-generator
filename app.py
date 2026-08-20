import streamlit as st
import google.generativeai as genai
import time

# 1. إعداد الصفحة - يجب أن يكون أول سطر
st.set_page_config(page_title="غرفة الـ 10 عقول", layout="wide")

def main():
    st.title("🎬 نظام الـ 10 عقول - سكريبتات بشرية 100%")
    st.write("الهدف: سكريبت 30 دقيقة، لغة مصرية صايعة، جذب كل 15 ثانية (روح الدوبامين ونظام التفاهة).")

    # --- القائمة الجانبية ---
    with st.sidebar:
        st.header("⚙️ الإعدادات التقنية")
        api_key = st.text_input("Gemini API Key", type="password")
        model_choice = st.selectbox("اختر الموديل", ["gemini-1.5-flash", "gemini-1.5-pro"])
        target_mins = st.slider("مدة الفيديو (دقائق)", 10, 60, 30)
        
        st.divider()
        if st.button("🔄 مسح الذاكرة وابدأ من جديد"):
            st.session_state.clear()
            st.rerun()

    # --- المدخلات ---
    topic = st.text_area("🎯 فكرة الفيديو أو العنوان:", placeholder="مثلاً: ليه مش عارف أحافظ على عادة جديدة؟")

    # --- تعريف العقول (البرومبتات المحقونة بروح الاسكريبتات الـ 3) ---
    GLOBAL_RULES = f"""
    أنت كاتب محتوى مصري عبقري. اللغة: عامية مصرية شيك (لغة مثقفين).
    الأسلوب: بشري، دافئ، وصادق. ابعد تماماً عن الفصحى وكليشيهات الـ AI.
    القاعدة الذهبية: كل 15 ثانية 'اخطف' المشاهد (سؤال مفاجئ، إيفيه، صدمة، قصة).
    المهمة: سكريبت {target_mins} دقيقة بأسلوب 'رحلة اكتشاف'.
    """

    MINDS = [
        {"id": 1, "name": "المُنقب", "task": "حلل علم الأعصاب وطلع 'الزتونة' و10 مواقف مصرية واقعية."},
        {"id": 2, "name": "المحلل النفسي", "task": "اكتب 15 اعتراف بلسان المشاهد بالعامية (الوجع الحقيقي) زي: 'أنا بضحك على نفسي'."},
        {"id": 3, "name": "صائد الزاوية", "task": "أوجد زاوية 'صادمة' تقلب مفهوم المشاهد (زي أسلوب سكريبت نظام التفاهة)."},
        {"id": 4, "name": "ملك الهوك", "task": "اكتب أقوى مقدمة 90 ثانية تخطف المشاهد وتتحداه يكمل الفيديو."},
        {"id": 5, "name": "المهندس", "task": "ابني هيكل الفيديو (8 فصول) وازرع 'قنابل فضول' في نهاية كل فصل."},
        {"id": 6, "name": "الحكواتي", "task": "حول الشرح لقصص مصرية وتشبيهات (شبه الدماغ بالميكروباص أو شاحن الموبايل)."},
        {"id": 7, "name": "حارس الاستبقاء", "task": "راجع الكلام وازرع محفزات انتباه كل 15 ثانية (إيفيه، سؤال، مفاجأة)."},
        {"id": 8, "name": "الكاتب الرئيسي", "task": f"اكتب السكريبت الكامل لـ {target_mins} دقيقة بالعامية المصرية (بشرية 100%)."},
        {"id": 9, "name": "المشرط القاسي", "task": "نقي الكلام من أي روح روبوتية واقطع الحشو الممل."},
        {"id": 10, "name": "المخرج النهائي", "task": "النسخة النهائية الجاهزة للتصوير مع توجيهات بصرية [بين أقواس]."}
    ]

    if "history" not in st.session_state:
        st.session_state.history = {}

    # --- زر التشغيل ---
    if st.button("🚀 ابدأ غرفة العمليات", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ حط الـ API Key في الجنب")
            return
        if not topic:
            st.warning("⚠️ اكتب موضوع الفيديو")
            return

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_choice)
            
            progress_bar = st.progress(0)
            
            for i, mind in enumerate(MINDS):
                key = f"m{mind['id']}"
                if key in st.session_state.history:
                    progress_bar.progress((i+1)/len(MINDS))
                    continue
                
                with st.status(f"🧠 {mind['name']} شغال دلوقت...", expanded=True) as status:
                    # بناء السياق
                    prev_text = ""
                    for j in range(i):
                        prev_text += f"\n--- مخرج {MINDS[j]['name']} ---\n{st.session_state.history.get(f'm{j+1}', '')[:800]}...\n"
                    
                    prompt = f"{GLOBAL_RULES}\nالموضوع: {topic}\nالمهمة: {mind['task']}\nسياق سابق: {prev_text}"
                    
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        st.session_state.history[key] = response.text
                        st.markdown(response.text)
                        status.update(label=f"✅ {mind['name']} خلص", state="complete")
                    else:
                        st.error(f"خ
