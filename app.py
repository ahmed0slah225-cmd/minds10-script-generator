from __future__ import annotations
import os
import streamlit as st
from core.model_registry import AVAILABLE_MODELS, DEFAULT_MODEL, get_model, validate_capabilities
from core.llm_provider import GeminiProvider
from core.pipeline import new_project
from core.orchestrator import Orchestrator
from core.models import ProjectSettings, VoiceDNA
from core.document_loader import extract_uploaded_file
from engines.voice.engine import VoiceDNAEngine
from storage.storage_factory import get_store

st.set_page_config(page_title='Minds — منصة ذكاء المحتوى', page_icon='🧠', layout='wide')
st.title('🧠 Minds — منصة ذكاء المحتوى')
st.caption('من المادة الخام إلى غرفة كتابة كاملة: فهم → معرفة → استراتيجية → قصة → احتفاظ → Hook → Script → مراجعات → نسخة نهائية.')

@st.cache_resource
def get_store_cached(turso_url: str, turso_token: str):
    return get_store({'TURSO_DATABASE_URL':turso_url,'TURSO_AUTH_TOKEN':turso_token})

api_key=st.secrets.get('GEMINI_API_KEY',os.getenv('GEMINI_API_KEY',''))
turso_url=st.secrets.get('TURSO_DATABASE_URL',os.getenv('TURSO_DATABASE_URL',''))
turso_token=st.secrets.get('TURSO_AUTH_TOKEN',os.getenv('TURSO_AUTH_TOKEN',''))
store=get_store_cached(turso_url,turso_token)

with st.sidebar:
    st.header('إعدادات المشروع')
    project_name=st.text_input('اسم المشروع','مشروع جديد')
    duration=st.slider('مدة الفيديو (دقيقة)',5,90,30)
    audience=st.text_area('الجمهور المستهدف','شباب وبنات مصريين يحبوا الحكي والأمثلة ومش المحاضرات',height=80)
    model_label=st.selectbox('الموديل',list(AVAILABLE_MODELS),index=list(AVAILABLE_MODELS).index(DEFAULT_MODEL))
    web_enabled=st.checkbox('🔎 تفعيل البحث المباشر من الإنترنت',value=False,help='OFF يعني لا يوجد بحث خارجي من أي Engine.')
    depth_label=st.selectbox('عمق البحث',['أساسي','قياسي','عميق'],index=1,disabled=not web_enabled)
    depth={'أساسي':'basic','قياسي':'standard','عميق':'deep'}[depth_label]
    st.divider(); st.write(f'**Model:** `{get_model(model_label).model_id}`'); st.write(f'**Web Research:** `{"ON" if web_enabled else "OFF"}`')
    projects=store.list_projects(); existing=st.selectbox('استكمال مشروع',['+ مشروع جديد']+[p[0] for p in projects])

if existing != '+ مشروع جديد':
    loaded=store.load_project(existing)
    if loaded: st.session_state['last_state']=loaded.model_dump()

left,right=st.columns([1,2])
with left:
    st.subheader('1) المادة الخام')
    topic=st.text_area('الموضوع / السؤال / الفكرة / المسودة',height=240,placeholder='حتى جملة واحدة. النظام يفهمها قبل الكتابة.')
    uploaded=st.file_uploader('إرفاق PDF أو TXT أو Markdown',type=['pdf','txt','md'])
    c1,c2=st.columns(2)
    with c1: page_start=st.number_input('بداية PDF',1,100000,1,disabled=not uploaded or not uploaded.name.lower().endswith('.pdf'))
    with c2: page_end=st.number_input('نهاية PDF',1,100000,20,disabled=not uploaded or not uploaded.name.lower().endswith('.pdf'))
    source_text=''
    if uploaded:
        try: source_text=extract_uploaded_file(uploaded,int(page_start),int(page_end))
        except Exception as exc: st.error(str(exc))
    st.caption(f'المصدر المستخرج: {len(source_text):,} حرف')

    st.subheader('2) Voice DNA')
    voice_samples=st.text_area('عينات حقيقية من كتابتك السابقة',height=140,placeholder='الصق نماذجك. النظام يستخرج سمات الأسلوب ولا ينسخ النصوص.')
    if st.button('🧬 بناء Voice DNA',use_container_width=True):
        if not api_key: st.error('أضف GEMINI_API_KEY في Streamlit Secrets.')
        elif not voice_samples.strip(): st.warning('أضف عينات أولًا.')
        else:
            try:
                settings=ProjectSettings(name='voice-profile',model_label=model_label)
                ctx=new_project('voice-profile',settings,voice_samples); ctx.state.metadata['voice_samples']=voice_samples
                VoiceDNAEngine().run(ctx,GeminiProvider(api_key)); st.session_state['voice_dna']=ctx.state.voice_dna.model_dump(); st.success('تم بناء Voice DNA.')
            except Exception as exc: st.error(f'فشل Voice DNA: {exc}')

    st.subheader('3) تشغيل المنصة')
    if st.button('🚀 تشغيل غرفة الكتابة كاملة',type='primary',use_container_width=True):
        if not api_key: st.error('أضف GEMINI_API_KEY في Secrets.')
        elif not topic.strip(): st.error('اكتب المادة الخام أولًا.')
        else:
            try:
                validate_capabilities(model_label,web_enabled)
                settings=ProjectSettings(name=project_name,duration_minutes=duration,audience=audience,model_label=model_label,web_research=web_enabled,research_depth=depth,pdf_page_start=int(page_start) if uploaded and uploaded.name.lower().endswith('.pdf') else None,pdf_page_end=int(page_end) if uploaded and uploaded.name.lower().endswith('.pdf') else None)
                ctx=new_project(topic,settings,source_text)
                if 'voice_dna' in st.session_state: ctx.state.voice_dna=VoiceDNA.model_validate(st.session_state['voice_dna'])
                with st.spinner('المنصة بتبني المشروع مرحلة مرحلة...'): ctx=Orchestrator(GeminiProvider(api_key),store).run(ctx)
                st.session_state['last_state']=ctx.state.model_dump(); st.session_state['last_trace']=ctx.trace; st.success('اكتمل خط الإنتاج.')
            except Exception as exc: st.exception(exc)

with right:
    st.subheader('لوحة التشغيل')
    state=st.session_state.get('last_state')
    if state:
        stages=['input_router','topic_understanding','source_analysis','research','knowledge','audience','strategy','story','retention','hook','script','humanize','anti_slop_review','repetition_review','egyptian_editor','voice_check','truth_check','final_editor']
        trace=st.session_state.get('last_trace',[]); done={x.get('stage') for x in trace if x.get('status')=='ok'}
        cols=st.columns(3)
        for i,s in enumerate(stages): cols[i%3].write(('✅ ' if s in done else '○ ')+s)
        st.divider(); ta=state.get('topic_analysis',{}); strategy=state.get('strategy',{})
        st.write('**المشكلة الإنسانية:**',ta.get('human_problem','')); st.write('**الزاوية:**',ta.get('angle','')); st.write('**الوعد:**',strategy.get('central_promise',''))
        with st.expander('Hooks',False): st.json(state.get('hook_set',[]))
        with st.expander('Anti-Slop Review',False): st.json(state.get('metadata',{}).get('anti_slop',{}))
        with st.expander('Truth Check',False): st.json(state.get('metadata',{}).get('truth_check',{}))
        st.subheader('النص النهائي'); final=state.get('final_script',''); st.markdown(final); st.download_button('⬇️ تحميل النسخة النهائية',final,file_name='minds_final_script.txt',mime='text/plain')
    else: st.info('ابدأ بإدخال موضوع. المنصة لن تبدأ بالكتابة مباشرة؛ ستبني Context ثم تمر بالمحركات والمراجعات.')

with st.expander('المصادر وResearch State'):
    if state:
        st.write('Web Research:',state.get('settings',{}).get('web_research')); st.write('Status:',state.get('metadata',{}).get('research_status'))
        for src in state.get('sources',[]): st.write(f"- {src.get('title')} | {src.get('url','')} | {src.get('provenance')} | confidence={src.get('confidence')}")
