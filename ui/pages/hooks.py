import streamlit as st
from ui.components import title

def render(repo, settings):
    title('Hooks', 'مراجعة وصناعة الهوك بشكل مستقل عند الحاجة.')
    if not st.session_state.get('current_project_id'):
        st.info('افتح مشروعًا أولًا.')
        return
    st.info('توليد الهوك الكامل يتم داخل خط الإنتاج في Workspace للحفاظ على نفس المعرفة والسياق.')
