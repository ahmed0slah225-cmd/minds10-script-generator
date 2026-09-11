import streamlit as st
from engines.research_engine import ResearchEngine
from services.web.links import normalize_urls
from services.gemini import GeminiClient
from ui.components import title

def render(repo, settings):
    title('Research', 'بحث خارجي اختياري، مع فصل واضح بين نتائج الويب ومصادر المشروع.')
    st.session_state.setdefault('selected_gemini_model', settings.gemini_model if settings.gemini_model in {'gemini-3.7-flash','gemini-3.6-flash'} else 'gemini-3.7-flash')
    st.session_state.setdefault('use_web_search', False)
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox('موديل Gemini', ['gemini-3.7-flash','gemini-3.6-flash'], index=0 if st.session_state['selected_gemini_model']=='gemini-3.7-flash' else 1, format_func=lambda x: 'Gemini 3.7 Flash' if x=='gemini-3.7-flash' else 'Gemini 3.6 Flash', key='selected_gemini_model')
    with c2:
        st.checkbox('🔎 البحث المباشر من الإنترنت', key='use_web_search')
    pid = st.session_state.get('current_project_id')
    if not pid:
        st.info('افتح مشروعًا أولًا من Workspace.')
        return
    q = st.text_area('سؤال البحث', height=130)
    urls = st.text_area('روابط محددة (اختياري)', height=100)
    if st.button('ابدأ البحث', type='primary') and q.strip():
        try:
            result = ResearchEngine(GeminiClient().client).run(q, normalize_urls(urls), purpose='content research', use_google_search=bool(st.session_state.get('use_web_search', False)))
            st.session_state['last_research'] = result
            st.markdown(result['answer'])
            for u in result['urls']:
                st.write('-', u)
        except Exception as e:
            st.error(str(e))
