import streamlit as st
import google.generativeai as genai
import time

# ============================================================
# إعداد الصفحة - لازم تكون أول سطر
# ============================================================
st.set_page_config(
    page_title="غرفة الـ 10 عقول - Script Master",
    page_icon="🎬",
    layout="wide",
)

# ============================================================
# واجهة المستخدم والأسلوب البصري
# ============================================================
st.title("🎬 نظام الـ 10 عقول لصناعة الاسكريبتات البشرية")
st.write("الهدف: سكريبت 30 دقيقة، جذب كل 15 ثانية، لغة مصرية 'صايعة' ومستفزة فكرياً.")

# الإعدادات الجانبية
with st.sidebar:
    st.header("⚙️ الإعدادات التقنية")
    api_key = st.text_input("Google API Key", type="password")
    
    # تم تعيين gemini-3.6-flash كديفولت بناءً على طلبك
    model_choice = st.text_input("اسم الموديل", value="gemini-3.6-flash")
    
    target_minutes = st.slider("مدة الفيديو المستهدفة (دقائق)", 10, 60, 30)
    
    st.divider()
    if st.button("🔄 مسح الذاكرة وابدأ موضوع جديد"):
        st.session_state.clear()
        st.rerun()

# ============================================================
# البرومبتات المصرية الـ 10 (التفصيل الممل)
# ============================================================
GLOBAL_RULES = """
أنت كاتب محتوى مصري محترف جداً. 
اللغة: عامية مصرية شيك (لغة شباب مثقفين بيقعدوا على القهوة). 
الممنوعات: الفصحى تماماً، كليشيهات الذكاء الاصطناعي (مثل: دعنا نستكشف، في عالم مليء بـ). 
القاعدة الذهبية: كل 15 ثانية لازم يحصل 'خطف' لانتباه المشاهد (سؤال مفاجئ، إيفيه مصري، قصة سريعة، معلومة صادمة).
الهدف: فيديو 30 دقيقة المشاهد مبيزهقش منه ولا ثانية.
"""

MINDS = [
    {"id": 1, "name": "المُنقب عن الزتونة", "task": "ابحث في علم الأعصاب وعلم النفس عن 'أعمق أسباب' الموضوع. استخرج 5 حقائق علمية صادمة و10 مواقف مصرية واقعية المشاهد بيعيشها يومياً."},
    {"id": 2, "name": "المحلل النفسي", "task": "حلل وجع المشاهد النفسي. هو بيحس بإيه وهو لوحده؟ اكتب 15 جملة اعتراف بلسانه (زي: أنا بضحك على نفسي وبقول هبدأ بكره)."},
    {"id": 3, "name": "صائد الزاوية الصايعة", "task": "أوجد زاوية 'غير مكررة' للفيديو. لو الموضوع مكرر، اقلبه. حدد 'السر' اللي مش هنقوله غير في نص الفيديو عشان يكمل للآخر."},
    {"id": 4, "name": "ملك الهوك المصري", "task": "اكتب أقوى مقدمة 90 ثانية. ابدأ بجملة تخلي المشاهد يفرمل وهو بيقلب. لازم يحس إنك مراقبه وعارف اللي جواه."},
    {"id": 5, "name": "المهندس المعماري", "task": "ابني هيكل الفيديو (8 فصول). ازرع 'قنابل فضول' (Open Loops) في آخر كل فصل عشان المشاهد ميقدرش يقفل الفيديو."},
    {"id": 6, "name": "الحكواتي المصري", "task": "حول الشرح العلمي لقصص وتشبيهات من الشارع المصري (ميكروباص، شاحن موبايل، ماتش كورة). خلي الكلام ليه روح بشرية."},
    {"id": 7, "name": "حارس الاستبقاء", "task": "راجع الكلام وازرع محفزات انتباه كل 15 ثانية حرفياً (إيفيه ذكي، سؤال يلمس الوجع، تغيير رتم الكلام)."},
    {"id": 8, "name": "الكاتب الرئيسي (المسودة)", "task": "اكتب سكريبت كامل لـ 30 دقيقة بالعامية المصرية. ادمج العلم بالقصص بالهوك في نسيج واحد ممتع جداً وبشري تماماً."},
    {"id": 9, "name": "المشرط القاسي", "task": "أنت المحرر اللي بيكره الروبوتات. أي جملة ريحتها AI اقطعها. حول أي كلام رسمي لعامية مصرية 'صايعة'. احذف الملل."},
    {"id": 10, "name": "المخرج النهائي", "task": "النسخة النهائية الجاهزة للتصوير. ضيف توجيهات بصرية [بين أقواس] للجرافيك والحركات. الناتج لازم يكون بشري ومصري 100%."}
]

# ============================================================
# منطق التشغيل
# ============================================================
if "outputs" not in st.session_state:
    st.session_state.outputs = {}

topic = st.text_area("🎯 عنوان الفيديو أو الفكرة اللي في دماغك:", placeholder="مثلاً: ليه مش عارف أحافظ على عادة جديدة؟")

if st.button("🚀 ابدأ غرفة العمليات (10 عقول)", type="primary", use_container_width=True):
    if not api_key:
        st.error("❌ من فضلك دخل الـ API Key في الجنب الأول.")
    elif not topic:
        st.warning("⚠️ دخل موضوع الفيديو الأول.")
    else:
        try:
            # إعداد Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_choice)
            
            progress_bar = st.progress(0)
            status_container = st.container()
            
            for i, mind in enumerate(MINDS):
                mind_key = f"mind_{mind['id']}"
                
                # تخطي لو العقل ده خلص قبل كدة
                if mind_key in st.session_state.outputs:
                    progress_bar.progress((i + 1) / len(MINDS))
                    continue
                
                with st.status(f"🧠 جاري تشغيل {mind['name']}...", expanded=True) as status:
                    # بناء السياق من العقول السابقة (بشكل مختصر لعدم تخطي الليميت)
                    prev_context = ""
                    for idx in range(1, mind['id']):
                        prev_context += f"\n--- نتائج {MINDS[idx-1]['name']} ---\n{st.session_state.outputs.get(f'mind_{idx}', '')[:600]}...\n"
                    
                    full_prompt = f"""
                    {GLOBAL_RULES}
                    الموضوع: {topic}
                    مدة الفيديو الكلية: {target_minutes} دقيقة.
                    مهمتك الحالية كـ ({mind['name']}): {mind['task']}
                    
                    سياق من العقول السابقة لمساعدتك:
                    {prev_context}
                    """
                    
                    # استدعاء الموديل
                    response = model.generate_content(full_prompt)
                    
                    if response.text:
                        st.session_state.outputs[mind_key] = response.text
                        st.markdown(response.text)
                        status.update(label=f"✅ {mind['name']} أنجز مهمته بنجاح", state="complete")
                    else:
                        st.error(f"الموديل مارجعش رد في خطوة {mind['name']}")
                        st.stop()
                
                progress_bar.progress((i + 1) / len(MINDS))
            
            if "mind_10" in st.session_state.outputs:
                st.success("🎉 مبروك! الاسكريبت النهائي للـ 30 دقيقة جاهز.")
                st.divider()
                st.header("🎬 MASTER SCRIPT (النسخة النهائية)")
                st.markdown(st.session_state.outputs["mind_10"])
                st.download_button(
                    label="⬇️ تحميل الاسكريبت النهائي TXT",
                    data=st.session_state.outputs["mind_10"],
                    file_name="final_script_egyptian.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"حدث خطأ تقني: {e}")
            if "404" in str(e):
                st.info("💡 الموديل 3.6 قد لا يكون متاحاً في منطقتك حالياً، جرب كتابة gemini-1.5-flash في الخانة الجانبية.")
