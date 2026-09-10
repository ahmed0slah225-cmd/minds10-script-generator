import streamlit as st
from ui.components import title

def render(repo, settings):
    title('Ideas', 'مساحة لالتقاط زوايا وأفكار قابلة للتحويل إلى فيديو.')
    if not st.session_state.get('current_project_id'):
        st.info('افتح مشروعًا أولًا.')
        return
    idea = st.text_area('فكرة أو زاوية', height=150)
    if st.button('حفظ الفكرة') and idea.strip():
        st.success('تم الاحتفاظ بالفكرة داخل جلسة المشروع. يمكن تحويلها لاحقًا إلى استراتيجية أو سكريبت.')
        st.code(idea)
