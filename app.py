import streamlit as st
import google.generativeai as genai

# 1. يجب أن يكون هذا أول أمر في Streamlit
st.set_page_config(page_title="Writer Room", layout="wide")

# --- منع التحميل المستمر وتحسين الأداء ---
def main():
    st.title("🎬 غرفة صناعة المحتوى (الـ 10 عقول)")
    st.write("النظام ده بيحول فكرتك لسكريبت يوتيوب بشري بأسلوب مصري صايع.")

    # --- القائمة الجانبية ---
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        api_key = st.text_input("Gemini API Key", type="password")
        model_choice = st.selectbox("الموديل", ["gemini-1.5-flash", "gemini-1.5-pro"])
        target_mins = st.slider("مدة الفيديو (دقائق)", 10, 60, 30)
        
        if st.button("🔄 مسح الذاكرة"):
            st.session_state.clear()
            st.rerun()

    # --- المدخلات ---
    topic = st.text_area("🎯 فكرة الفيديو أو العنوان اللي في دماغك:", 
                         placeholder="مثلاً: ليه مش عارف أحافظ على عادة جديدة؟")

    # --- تعريف العقول ببرومبتات صريحة ---
    minds_config = [
        {"id": 1, "name": "المُنقب", "task": "استخراج الحقائق الصادمة والمواقف المصرية الواقعية."},
        {"id": 2, "name": "المحلل النفسي", "task": "تحليل وجع المشاهد واعترافاته الشخصية بالعامية."},
        {"id": 3, "name": "صائد الزاوية", "task": "إيجاد زاوية غير مكررة تقلب مفهوم المشاهد."},
        {"id": 4, "name": "ملك الهوك", "task": "كتابة مقدمة 90 ثانية تخطف المشاهد فوراً."},
        {"id": 5, "name": "المهندس", "task": "بناء هيكل الفيديو (8 فصول) مع قنابل فضول."},
        {"id": 6, "name": "الحكواتي", "task": "تحويل الشرح لقصص وتشبيهات من الشارع المصري."},
        {"id": 7, "name": "حارس الاستبقاء", "task": "إضافة محفزات انتباه كل 15 ثانية (إيفيهات وأسئلة)."},
        {"id": 8, "name": "الكاتب الرئيسي", "task": "كتابة المسودة الكاملة بأسلوب بشري مصري 100%."},
        {"id": 9, "name": "المشرط القاسي", "task": "تنقية الكلام من أي روح روبوتية وحذف الحشو."},
        {"id": 10, "name": "المخرج النهائي", "task": "إنتاج السكريبت النهائي وتوجيهات التصوير."}
    ]

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    # --- زر التشغيل ---
    if st.button("🚀 تشغيل غرفة العمليات", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ دخل الـ API Key من الجنب")
            return
        if not topic:
            st.warning("⚠️ دخل عنوان الفيديو")
            return

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_choice)
            
            progress_bar = st.progress(0)
            
            for i, m in enumerate(minds_config):
                key = f"m{m['id']}"
                if key in st.session_state.responses:
                    continue
                
                with st.status(f"🧠 جاري تشغيل {m['name']}...", expanded=False) as status:
                    # بناء البرومبت
                    prev_data = "\n".join([st.session_state.responses.get(f"m{idx}", "")[:400] for idx in range(1, m['id'])])
                    
                    final_prompt = f"""
                    أنت خبير كاتب سكريبتات يوتيوب مصري.
                    الموضوع: {topic}
                    مهمتك الحالية كـ ({m['name']}): {m['task']}
                    الهدف: فيديو {target_mins} دقيقة، جذب كل 15 ثانية، لغة عامية مصرية بشرية تماماً.
                    بيانات من العقول السابقة:
                    {prev_data}
                    """
                    
                    response = model.generate_content(final_prompt)
                    st.session_state.responses[key] = response.text
                    st.write(response.text)
                    status.update(label=f"✅ {m['name']} خلص مهمته", state="complete")
                
                progress_bar.progress((i + 1) / len(minds_config))

            st.success("🎉 المهمة تمت بنجاح!")
            st.subheader("📜 السكريبت النهائي")
            st.markdown(st.session_state.responses.get("m10", "حدث خطأ في استخراج النص النهائي"))
            
        except Exception as e:
            st.error(f"حدث خطأ تقني: {e}")

if __name__ == "__main__":
    main()
