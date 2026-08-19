import streamlit as st
import google.generativeai as genai
import time

# ============================================================
# 1. إعدادات الصفحة (يجب أن يكون أول سطر)
# ============================================================
st.set_page_config(page_title="غرفة الـ 10 عقول", layout="wide")

def main():
    st.title("🎬 نظام الـ 10 عقول - سكريبتات احترافية")
    st.write("النظام ده هيطلع لك سكريبت 30 دقيقة بالعامية المصرية الصايعة، بجذب كل 15 ثانية.")

    # القائمة الجانبية
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        api_key = st.text_input("Gemini API Key", type="password")
        
        # اختيار الموديل يدوياً لضمان عدم حدوث 404
        # الـ flash-1.5 هو الأكثر استقراراً حالياً
        model_name = st.selectbox("اختر الموديل", 
                                ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"])
        
        target_mins = st.slider("مدة الفيديو (دقائق)", 10, 60, 30)
        
        if st.button("🔄 مسح الذاكرة"):
            st.session_state.clear()
            st.rerun()

    # المدخلات
    topic = st.text_area("🎯 عنوان الفيديو أو الفكرة:", placeholder="مثلاً: ليه مش عارف أحافظ على عادة جديدة؟")

    # --- تعريف العقول (نفس المهمات القوية بالعامية) ---
    MINDS = [
        {"id": 1, "name": "المُنقب", "task": "حلل علم الأعصاب وطلع 5 حقائق صادمة و10 مواقف مصرية واقعية."},
        {"id": 2, "name": "المحلل النفسي", "task": "اكتب 15 اعتراف نفسي بلسان المشاهد (الوجع الحقيقي)."},
        {"id": 3, "name": "صائد الزاوية", "task": "لاقي فكرة تقلب دماغ المشاهد وتخليه ينبهر."},
        {"id": 4, "name": "ملك الهوك", "task": "اكتب أقوى مقدمة 90 ثانية تخطف المشاهد بالعامية الصارخة."},
        {"id": 5, "name": "المهندس", "task": "ابني هيكل الفيديو (8 فصول) وازرع قنابل فضول."},
        {"id": 6, "name": "الحكواتي", "task": "حول الشرح لقصص مصرية وتشبيهات من الشارع (ميكروباص، قهوة)."},
        {"id": 7, "name": "حارس الاستبقاء", "task": "ازرع محفزات انتباه كل 15 ثانية (إيفيه، سؤال، مفاجأة)."},
        {"id": 8, "name": "الكاتب الرئيسي", "task": "اكتب المسودة الكاملة بالعامية المصرية (بشرية 100%)."},
        {"id": 9, "name": "المشرط القاسي", "task": "نقي الكلام من أي روح روبوتية واقطع الحشو الملل."},
        {"id": 10, "name": "المخرج النهائي", "task": "النسخة النهائية الجاهزة للتصوير مع توجيهات بصرية."}
    ]

    if "history" not in st.session_state:
        st.session_state.history = {}

    if st.button("🚀 ابدأ غرفة العمليات", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ حط الـ API Key في الجنب")
            return
        if not topic:
            st.warning("⚠️ اكتب موضوع الفيديو")
            return

        try:
            # الإعداد الصحيح للمكتبة
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            progress_bar = st.progress(0)
            
            for i, mind in enumerate(MINDS):
                key = f"m{mind['id']}"
                if key in st.session_state.history:
                    progress_bar.progress((i+1)/len(MINDS))
                    continue
                
                with st.status(f"🧠 {mind['name']} بيفكر دلوقت...", expanded=False) as status:
                    # سياق العقول السابقة
                    prev_text = "\n".join([f"نتائج {MINDS[j]['name']}: {st.session_state.history.get(f'm{j+1}', '')[:500]}..." for j in range(i)])
                    
                    prompt = f"""
                    أنت كاتب محتوى مصري عبقري. اللغة: عامية مصرية شيك (لغة مثقفين).
                    الموضوع: {topic}
                    مهمتك الحالية كـ ({mind['name']}): {mind['task']}
                    قاعدة: جذب كل 15 ثانية، ممنوع الفصحى، فيديو {target_mins} دقيقة.
                    سياق سابق: {prev_text}
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state.history[key] = response.text
                    st.markdown(response.text)
                    status.update(label=f"✅ {mind['name']} خلص", state="complete")
                
                progress_bar.progress((i+1)/len(MINDS))

            st.success("🎉 السكريبت النهائي جاهز!")
            st.markdown(st.session_state.history.get("m10", ""))
            
        except Exception as e:
            st.error(f"⚠️ حصلت مشكلة: {str(e)}")
            st.info("لو الخطأ 404، جرب تغير 'اسم الموديل' من القائمة الجانبية.")

if __name__ == "__main__":
    main()
