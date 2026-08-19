import time
import streamlit as st
from google import genai
from google.genai import errors

# ============================================================
# إعداد الصفحة
# ============================================================

st.set_page_config(
    page_title="غرفة عمليات الـ 10 عقول",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 نظام الـ 10 عقول - Script Master")
st.write("سكريبتات بشرية 100% بالعامية المصرية الصايعة، جذب كل 15 ثانية.")

# ============================================================
# الإعدادات في الشريط الجانبي
# ============================================================

with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("Google Gemini API Key", type="password")
    
    # حطينا الـ 3.6 اللي إنت عايزه كخيار أول
    model_name_input = st.text_input("اسم الموديل", value="gemini-3.6-flash")
    
    target_minutes = st.slider("مدة الفيديو المستهدفة (بالدقائق)", 10, 60, 30, 5)
    audience = st.text_area("الجمهور المستهدف", value="شباب مصريين، بيحبوا الزتونة، بيكرهوا الكلام الرسمي والملل.")
    
    st.divider()
    show_all_outputs = st.checkbox("عرض مخرجات العقول بالتفصيل", value=True)

# ============================================================
# الدستور والبرومبتات (تم دمج "الروح المصرية" في كل عقل)
# ============================================================

GLOBAL_RULES = """
أنت كاتب بشري مصري 'برنس'. اللغة: عامية المثقفين المصرية. 
ممنوع الفصحى أو كلام الـ AI الممل. 
كل 15 ثانية لازم 'تخطف' المشاهد: سؤال، إيفيه، صدمة، قصة. 
ادخل في الوجع النفسي للمشاهد فوراً من غير مقدمات.
"""

MINDS = [
    {"id": 1, "name": "العقل 1: المُنقب", "description": "طلع الحقائق العلمية الصادمة (الزتونة) و10 مواقف مصرية واقعية بتلمس المشكلة دي."},
    {"id": 2, "name": "العقل 2: المحلل النفسي", "description": "حلل وجع المشاهد واكتب اعترافات بلسانه بالعامية المصرية (كلام من القلب)."},
    {"id": 3, "name": "العقل 3: صائد الزاوية", "description": "أوجد زاوية 'صايعة' للفيديو تقلب دماغ المشاهد. متكررش كلام غيرك."},
    {"id": 4, "name": "العقل 4: ملك الهوك", "description": "اكتب أقوى مقدمة 90 ثانية. جملة تخلي المشاهد يفرمل وهو بيسكرول."},
    {"id": 5, "name": "العقل 5: المهندس", "description": "ابني هيكل الفيديو (8 فصول). ازرع قنابل فضول في آخر كل فصل."},
    {"id": 6, "name": "العقل 6: الحكواتي", "description": "حول الشرح لقصص مصرية وتشبيهات من الشارع (ميكروباص، قهوة، شاحن)."},
    {"id": 7, "name": "العقل 7: حارس الاستبقاء", "description": "ازرع محفزات انتباه كل 15 ثانية (إيفيه، سؤال مفاجئ، تغيير رتم)."},
    {"id": 8, "name": "العقل 8: الكاتب الرئيسي", "description": "اكتب السكريبت الكامل (30 دقيقة) بالعامية المصرية. لغة بشرية 100%."},
    {"id": 9, "name": "العقل 9: المشرط القاسي", "description": "نقي الكلام من أي ريحة AI. اقطع الحشو وخليه 'صايع' ومصري أصلي."},
    {"id": 10, "name": "العقل 10: المخرج النهائي", "description": "النسخة النهائية مع توجيهات بصرية [بين أقواس]. سكريبت جاهز للتصوير."},
]

ROUTES = {1:[], 2:[1], 3:[1,2], 4:[2,3], 5:[1,2,3,4], 6:[1,2,3,5], 7:[3,4,5,6], 8:[1,2,3,4,5,6,7], 9:[2,3,4,7,8], 10:[1,2,3,4,5,6,7,8,9]}

# ============================================================
# منطق التشغيل
# ============================================================

if "pipeline_outputs" not in st.session_state:
    st.session_state.pipeline_outputs = {}

topic = st.text_area("🎯 عنوان الفيديو أو الفكرة:", placeholder="مثلاً: ليه مش عارف أحافظ على عادة جديدة؟")

col_run, col_reset = st.columns([3, 1])
with col_run: run_btn = st.button("🚀 ابدأ غرفة العمليات", type="primary", use_container_width=True)
with col_reset: reset_btn = st.button("🔄 ابدأ موضوع جديد", use_container_width=True)

if reset_btn:
    st.session_state.pipeline_outputs = {}
    st.rerun()

if run_btn:
    if not api_key:
        st.error("❌ دخل الـ API Key")
    elif not topic:
        st.warning("⚠️ اكتب العنوان")
    else:
        try:
            client = genai.Client(api_key=api_key.strip())
            outputs = st.session_state.pipeline_outputs
            progress = st.progress(0)
            status_text = st.empty()
            
            # معالجة اسم الموديل
            selected_model = model_name_input.strip()
            
            for i, mind in enumerate(MINDS):
                mind_key = f"العقل {mind['id']}"
                if mind_key in outputs:
                    progress.progress((i+1)/len(MINDS))
                    continue
                
                status_text.info(f"🧠 {mind['name']} بيفكر دلوقت...")
                
                # بناء السياق (قص النص لضمان عدم حدوث Error)
                prev_context = ""
                for mid in ROUTES[mind['id']]:
                    prev_context += f"\n[نتائج العقل {mid}]:\n{outputs.get(f'العقل {mid}', '')[:1500]}...\n"
                
                final_prompt = f"""
                {GLOBAL_RULES}
                الموضوع: {topic}
                الجمهور: {audience}
                المدة: {target_minutes} دقيقة
                مهمتك كـ ({mind['name']}): {mind['description']}
                ---
                سياق العقول السابقة:
                {prev_context}
                """
                
                try:
                    # محاولة الاتصال بالموديل المختار
                    response = client.models.generate_content(model=selected_model, contents=final_prompt)
                except Exception:
                    # لو فشل (404)، جرب الموديل المستقر تلقائياً
                    status_text.warning(f"⚠️ الموديل {selected_model} غير متاح، بنجرب gemini-1.5-flash...")
                    response = client.models.generate_content(model="gemini-1.5-flash", contents=final_prompt)
                
                if response.text:
                    outputs[mind_key] = response.text
                    st.session_state.pipeline_outputs = outputs
                    if show_all_outputs:
                        with st.expander(f"✅ {mind['name']}"):
                            st.markdown(outputs[mind_key])
                
                progress.progress((i+1)/len(MINDS))
            
            if "العقل 10" in outputs:
                status_text.success("🎉 الاسكريبت النهائي جاهز!")
                st.markdown(outputs["العقل 10"])
                st.download_button("⬇️ تحميل الاسكريبت", outputs["العقل 10"], file_name="final_script.txt")
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
