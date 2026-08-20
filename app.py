import streamlit as st
import google.generativeai as genai
import time

# إعداد الصفحة - لازم أول سطر
st.set_page_config(page_title="غرفة الـ 10 عقول", layout="wide")

def main():
    st.title("🎬 نظام الـ 10 عقول لصناعة المحتوى البشري")
    st.write("الهدف: سكريبت 30 دقيقة، لغة مصرية صايعة، جذب كل 15 ثانية.")

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
    topic = st.text_area("🎯 عنوان الفيديو أو الفكرة:", placeholder="مثلاً: ليه مش عارف أحافظ على عادة جديدة؟")

    # --- البرومبتات الـ 10 (محقونة بروح الاسكريبتات الـ 3) ---
    GLOBAL_RULES = "أنت كاتب محتوى مصري عبقري. اللغة: عامية مصرية شيك (لغة مثقفين). الأسلوب: بشري، دافئ، وصادق. ابعد تماماً عن الفصحى وكليشيهات الـ AI. القاعدة الذهبية: كل 15 ثانية 'اخطف' المشاهد (سؤال مفاجئ، إيفيه، صدمة، قصة). المهمة: سكريبت طويل بأسلوب 'رحلة اكتشاف'."

    MINDS = [
        {"id": 1, "name": "العقل 1: المُنقب", "task": "حلل علم الأعصاب وطلع 'الزتونة' و10 مواقف مصرية واقعية المشاهد بيعيشها."},
        {"id": 2, "name": "العقل 2: المحلل النفسي", "task": "اكتب 15 اعتراف بلسان المشاهد بالعامية (الوجع الحقيقي) زي: 'أنا بضحك على نفسي'. خلي المشاهد يحس إنك مراقبه."},
        {"id": 3, "name": "العقل 3: صائد الزاوية", "task": "أوجد زاوية 'صادمة' وغير مكررة تقلب مفهوم المشاهد (زي أسلوب سكريبت نظام التفاهة). متقولش 'ازاي تنجح'، قول 'ليه النجاح فخ؟'."},
        {"id": 4, "name": "العقل 4: ملك الهوك", "task": "اكتب أقوى مقدمة 90 ثانية. ابدأ بجملة تخلي المشاهد يفرمل وهو بيقلب. لازم الهوك يكون فيه 'تحدي' لمعتقدات المشاهد القديمة."},
        {"id": 5, "name": "العقل 5: المهندس", "task": "ابني هيكل الفيديو (8 فصول). ازرع 'قنابل فضول' (Open Loops) في آخر كل فصل عشان المشاهد ميقدرش يقفل الفيديو."},
        {"id": 6, "name": "العقل 6: الحكواتي", "task": "حول الشرح العلمي لقصص مصرية وتشبيهات من الشارع المصري (شبه الدماغ بالميكروباص، أو العادة بشاحن الموبايل)."},
        {"id": 7, "name": "العقل 7: حارس الاستبقاء", "task": "راجع الكلام وازرع محفزات انتباه كل 15 ثانية (إيفيه ذكي، سؤال يلمس الوجع، تغيير رتم الكلام)."},
        {"id": 8, "name": "العقل 8: الكاتب الرئيسي", "task": "اكتب السكريبت الكامل بالعامية المصرية. ادمج العلم بالقصص بالهوك في نسيج واحد بشري جداً وممتع."},
        {"id": 9, "name": "العقل 9: المشرط القاسي", "task": "أنت المحرر اللي بيكره الروبوتات. أي جملة ريحتها AI اقطعها. حول أي كلام رسمي لعامية مصرية 'صايعة'."},
        {"id": 10, "name": "العقل 10: المخرج النهائي", "task": "النسخة النهائية الجاهزة للتصوير. ضيف توجيهات بصرية [بين أقواس]. الناتج لازم يكون بشري ومصري 100%."}
    ]

    if "history" not in st.session_state:
        st.session_state.history = {}

    # --- زر التشغيل ---
    if st.button("🚀 ابدأ غرفة العمليات", type="primary", use_container_width=True):
        if not api_key:
            st.error("ادخل API Key")
            return
        if not topic:
            st.warning("ادخل العنوان")
            return

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_choice)
            
            progress_bar = st.progress(0)
            
            for i, mind in enumerate(MINDS):
                key = "m" + str(mind["id"])
                if key in st.session_state.history:
                    progress_bar.progress((i + 1) / len(MINDS))
                    continue
                
                with st.status("جاري تشغيل " + mind["name"] + "...", expanded=True) as status:
                    # بناء السياق
                    prev_text = ""
                    for j in range(i):
                        prev_key = "m" + str(j + 1)
                        prev_text += "\n--- مخرج العقل السابق ---\n" + st.session_state.history.get(prev_key, "")[:1000] + "\n"
                    
                    full_prompt = GLOBAL_RULES + "\nالموضوع: " + topic + "\nالمهمة: " + mind["task"] + "\nسياق سابق: " + prev_text
                    
                    response = model.generate_content(full_prompt)
                    
                    if response.text:
                        st.session_state.history[key] = response.text
                        st.markdown(response.text)
                        status.update(label=mind["name"] + " خلص مهمته", state="complete")
                    else:
                        st.error("خطأ في رد الموديل")
                        return
                
                progress_bar.progress((i + 1) / len(MINDS))

            st.success("🎉 السكريبت النهائي جاهز!")
            st.divider()
            st.subheader("📜 MASTER SCRIPT")
            st.markdown(st.session_state.history.get("m10", ""))
            st.download_button("⬇️ تحميل السكريبت", st.session_state.history.get("m10", ""), "script.txt")
            
        except Exception as e:
            st.error("حصلت مشكلة تقنية: " + str(e))

if __name__ == "__main__":
    main()
