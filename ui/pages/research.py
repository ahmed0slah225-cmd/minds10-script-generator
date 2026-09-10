import streamlit as st
from engines.research_engine import ResearchEngine
from services.web.links import normalize_urls
from services.gemini import GeminiClient
from ui.components import title

def render(repo, settings):
    title('Research', 'بحث خارجي اختياري، مع فصل واضح بين نتائج الويب ومصادر المشروع.')
    pid = st.session_state.get('current_project_id')
    if not pid:
        st.info('افتح مشروعًا أولًا من Workspace.')
        return
    q = st.text_area('سؤال البحث', height=130)
    urls = st.text_area('روابط محددة (اختياري)', height=100)
    if st.button('ابدأ البحث', type='primary') and q.strip():
        try:
            result = ResearchEngine(GeminiClient().client).run(q, normalize_urls(urls), purpose='content research')
            st.session_state['last_research'] = result
            st.markdown(result['answer'])
            for u in result['urls']:
                st.write('-', u)
        except Exception as e:
            st.error(str(e))
