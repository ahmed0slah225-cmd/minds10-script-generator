import streamlit as st
import google.generativeai as genai

# إعداد الصفحة - لازم أول سطر
st.set_page_config(page_title="Writer Room 10 Minds", layout="wide")

def main():
    st.title("🎬 نظام الـ 10 عقول - سكريبتات احترافية")
    st.write("الهدف: سكريبت 30 دقيقة، لغة مصرية صايعة، جذب كل 15 ثانية.")

    # القائمة الجانبية
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("Gemini API Key", type="password")
        
        # اختيار الموديل يدوي أو تلقائي
        model_name = st.text_input("Model Name", value="gemini-1.5-flash")
        st.info("لو ظهر خطأ 404، جرب تغير الاسم لـ gemini-1.5-pro")
        
        target_mins = st.slider("Target Minutes", 10, 60, 30)
        
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

    # المدخلات
    topic = st.text_area("🎯 عنوان الفيديو أو الفكرة:", placeholder="اكتب هنا...")

    # البرومبتات الـ 10 (بالمصري الصايع)
    MINDS = [
        {"id": 1, "name": "Researcher", "task": "حلل علم الأعصاب وطلع الزتونة و10 مواقف مصرية واقعية."},
        {"id": 2, "name": "Psychologist", "task": "اكتب 15 اعتراف بلسان المشاهد بالعامية (الوجع الحقيقي)."},
        {"id": 3, "name": "Unique Angle", "task": "أوجد زاوية صادمة وغير مكررة تقلب مفهوم المشاهد (زي سكريبت نظام التفاهة)."},
        {"id": 4, "name": "Hook Master", "task": "اكتب أقوى مقدمة 90 ثانية تخطف المشاهد بالعامية الصارخة."},
        {"id": 5, "name": "Architect", "task": "ابني هيكل الفيديو (8 فصول) وازرع قنابل فضول في نهاية كل فصل."},
        {"id": 6, "name": "Storyteller", "task": "حول الشرح لقصص مصرية وتشبيهات (ميكروباص، قهوة، شاحن)."},
        {"id": 7, "name": "Retention", "task": "راجع الكلام وازرع محفزات انتباه كل 15 ثانية (إيفيه، سؤال، مفاجأة)."},
        {"id": 8, "name": "Lead Writer", "task": "اكتب السكريبت الكامل لـ " + str(target_mins) + " دقيقة بالعامية المصرية بشرية 100%."},
        {"id": 9, "name": "Script Doctor", "task": "نقي الكلام من أي روح روبوتية واقطع الحشو الملل."},
        {"id": 10, "name": "Final Director", "task": "النسخة النهائية الجاهزة للتصوير مع توجيهات بصرية [بين أقواس]."}
    ]

    if "history" not in st.session_state:
        st.session_state.history = {}

    if st.button("🚀 تشغيل غرفة العمليات", type="primary"):
        if not api_key:
            st.error("Please enter API Key")
            return
        if not topic:
            st.warning("Please enter topic")
            return

        try:
            # إعداد المكتبة
            genai.configure(api_key=api_key)
            
            # محاولة بناء الموديل
            model = genai.GenerativeModel(model_name)
            
            progress_bar = st.progress(0)
            
            for i, mind in enumerate(MINDS):
                key = "mind_" + str(mind["id"])
                if key in st.session_state.history:
                    progress_bar.progress((i + 1) / len(MINDS))
                    continue
                
                with st.status("Running: " + mind["name"] + "...", expanded=True) as status:
                    # تجميع السياق
                    context = ""
                    for j in range(i):
                        prev_key = "mind_" + str(j + 1)
                        context += "\n--- Prev Mind Result ---\n" + st.session_state.history.get(prev_key, "")[:1000]
                    
                    prompt = (
                        "أنت كاتب محتوى مصري عبقري. اللغة: عامية مصرية شيك جداً. "
                        "القاعدة: جذب كل 15 ثانية، ممنوع الفصحى تماماً. "
                        "الموضوع: " + topic + "\n"
                        "مهمتك الحالية كـ " + mind["name"] + ": " + mind["task"] + "\n"
                        "سياق العقول السابقة: " + context
                    )
                    
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        st.session_state.history[key] = response.text
                        st.markdown("### " + mind["name"])
                        st.markdown(response.text)
                        status.update(label=mind["name"] + " Done!", state="complete")
                    else:
                        st.error("Error: No response from model.")
                        return
                
                progress_bar.progress((i + 1) / len(MINDS))

            st.success("🎉 FINAL SCRIPT READY!")
            st.divider()
            final_script = st.session_state.history.get("mind_10", "")
            st.subheader("MASTER SCRIPT")
            st.write(final_script)
            st.download_button("Download Script", final_script, "script.txt")
            
        except Exception as e:
            error_msg = str(e)
            st.error("Technical Error: " + error_msg)
            if "404" in error_msg:
                st.info("💡 نصيحة: الـ API بيقول إن الموديل ده مش عنده. جرب تكتب gemini-1.5-pro في خانة Model Name.")

if __name__ == "__main__":
    main()
