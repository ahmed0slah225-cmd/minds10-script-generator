import streamlit as st
import google.generativeai as genai
import time

# ============================================================
# 1. إعداد الصفحة (يجب أن يكون أول سطر كود)
# ============================================================
st.set_page_config(page_title="غرفة الـ 10 عقول - Script Master", layout="wide")

# --- منع الأخطاء الشائعة وتحسين الواجهة ---
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #00ff00; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🎬 نظام الـ 10 عقول لصناعة المحتوى البشري")
    st.write("الهدف: سكريبت 30 دقيقة، جذب كل 15 ثانية، لغة مصرية 'صايعة' زي اسكريبتات مشاعل وأحمد أبوزيد.")

    # --- القائمة الجانبية ---
    with st.sidebar:
        st.header("⚙️ الإعدادات التقنية")
        api_key = st.text_input("ادخل Gemini API Key", type="password")
        
        # اختيار الموديل المستقر (Flash للسرعة أو Pro للدقة)
        model_choice = st.selectbox("اختر الموديل", 
                                  ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"])
        
        target_mins = st.slider("مدة الفيديو (دقائق)", 10, 60, 30)
        
        st.divider()
        if st.button("🔄 مسح الذاكرة وابدأ من جديد"):
            st.session_state.clear()
            st.rerun()

    # --- المدخلات ---
    topic = st.text_area("🎯 عنوان الفيديو أو الفكرة اللي في دماغك:", 
                         placeholder="مثلاً: ليه مش عارف أحافظ على عادة جديدة؟")

    # ============================================================
    # 2. الدستور والبرومبتات الـ 10 (تم تحديثها لتطابق الاسكريبتات الـ 3)
    # ============================================================
    GLOBAL_RULES = """
    أنت كاتب محتوى مصري عبقري. 
    اللغة: عامية مصرية شيك (لغة مثقفين بيقعدوا على القهوة). 
    الأسلوب: بشري تماماً، دافئ، وصادق. ابعد عن الفصحى تماماً وعن كليشيهات الـ AI.
    القاعدة الذهبية: كل 15 ثانية لازم 'تخطف' المشاهد (سؤال مفاجئ، إيفيه، صدمة، قصة).
    المهمة: بناء فيديو {mins} دقيقة بأسلوب (رحلة اكتشاف) مش محاضرة.
    """.format(mins=target_mins)

    MINDS = [
        {"id": 1, "name": "العقل 1: المُنقب عن الزتونة", "task": "حلل علم الأعصاب وعلم النفس وطلع 'الزتونة' اللي محدش يعرفها. استخرج 5 حقائق صادمة و10 مواقف مصرية واقعية المشاهد بيعيشها."},
        {"id": 2, "name": "العقل 2: المحلل النفسي", "task": "ادخل جوه 'وجع' المشاهد. اكتب 15 اعتراف بلسانه بالعامية (confessional storytelling) زي: 'أنا بضحك على نفسي'. خلي المشاهد يحس إنك مراقبه."},
        {"id": 3, "name": "العقل 3: صائد الزاوية (نظام التفاهة)", "task": "أوجد زاوية 'صادمة' وغير مكررة تقلب مفهوم المشاهد. متقولش 'ازاي تنجح'، قول 'ليه النجاح فخ؟' (زي أسلوب سكريبت نظام التفاهة)."},
        {"id": 4, "name": "العقل 4: ملك الهوك (البداية)", "task": "اكتب أقوى مقدمة 90 ثانية. ابدأ بجملة تخلي المشاهد يفرمل وهو بيقلب. لازم الهوك يكون فيه 'تحدي' لمعتقدات المشاهد القديمة."},
        {"id": 5, "name": "العقل 5: المهندس المعماري", "task": "ابني هيكل الفيديو (8 فصول). ازرع 'قنابل فضول' (Open Loops) في آخر كل فصل عشان المشاهد ميقدرش يقفل الفيديو."},
        {"id": 6, "name": "العقل 6: الحكواتي (ملك التشبيهات)", "task": "حول الشرح العلمي لقصص وتشبيهات من الشارع المصري (شبه الدماغ بالميكروباص، أو العادة بشاحن الموبايل)."},
        {"id": 7, "name": "العقل 7: حارس الاستبقاء", "task": "راجع الكلام وازرع محفزات انتباه كل 15 ثانية (إيفيه ذكي، سؤال يلمس الوجع، تغيير رتم الكلام). ممنوع الملل."},
        {"id": 8, "name": "العقل 8: الكاتب الرئيسي (المسودة)", "task": "اكتب السكريبت الكامل لـ {mins} دقيقة بالعامية المصرية. ادمج العلم بالقصص بالهوك في نسيج واحد بشري جداً.".format(mins=target_mins)},
        {"id": 9, "name": "العقل 9: المشرط القاسي", "task": "أنت المحرر اللي بيكره الروبوتات. أي جملة ريحتها AI اقطعها. حول أي كلام رسمي لعامية مصرية 'صايعة'. احذف الحشو."},
        {"id": 10, "name": "العقل 10: المخرج النهائي", "task": "النسخة النهائية الجاهزة للتصوير. ضيف توجيهات بصرية [بين أقواس]. الناتج لازم يكون بشري ومصري 100%."}
    ]

    if "history" not in st.session_state:
        st.session_state.history = {}

    # --- زر التشغيل ---
    if st.button("🚀 ابدأ غرفة العمليات", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ من فضلك دخل الـ API Key من القائمة الجانبية.")
            return
        if not topic:
            st.warning("⚠️ دخل موضوع الفيديو الأول.")
            return

        try:
            # الإعداد الصحيح للمكتبة المستقرة
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_choice)
            
            progress_bar = st.progress(0)
            
            for i, mind in enumerate(MINDS):
                key = f"m{mind['id']}"
                if key in st.session_state.history:
                    progress_bar.progress((i+1)/len(MINDS))
                    continue
                
                with st.status(f"🧠 {mind['name']} شغال دلوقت...", expanded=True) as status:
                    # بناء السياق (نرسل ملخصات فقط لتجنب تخطي الليميت)
                    prev_text = ""
                    for j in range(i):
                        prev_text += f"\n--- مخرج {MINDS[j]['name']} ---\n{st.session_state.history.get(f'm{j+1}', '')[:1000]}...\n"
                    
                    full_prompt = f"""
                    {GLOBAL_RULES}
                    الموضوع: {topic}
                    المهمة: {mind['task']}
                    
                    سياق العقول السابقة:
                    {prev_text}
                    """
                    
                    # طلب النتيجة
                    response = model.generate_content(full_prompt)
                    
                    if response.text:
                        st.session_state.history[key] = response.text
                        st.markdown(response.text)
                        status.update(label=f"✅ {mind['name']} خلص مهمته", state="complete")
                    else:
                        st.error(f"الموديل لم يستجب في مرحلة {mind['name']}")
                        return
                
                progress_bar.progress((i+1)/len(MINDS))

            st.success("🎉 السكريبت النهائي جاهز!")
            st.divider()
            st.header("📜 MASTER SCRIPT (النسخة النهائية)")
            st.markdown(st.session_state.history.get("m10", ""))
            st.download_button("⬇️ تحميل السكريبت النهائي", st.session_state.history.get("m10", ""), "final_script.txt")
            
        except Exception as e:
            st.error(f"⚠️ حصل خطأ تقني: {str(e)}")
            st.info("نصيحة: تأكد من تثبيت مكتبة google-generativeai وتحديثها.")

if __name__ == "__main__":
    main()
