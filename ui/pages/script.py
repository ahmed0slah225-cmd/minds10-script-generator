import streamlit as st
from ui.components import title, download_text

def render(repo, settings):
    title('Script', 'آخر نسخة نهائية محفوظة للمشروع الحالي.')
    pid = st.session_state.get('current_project_id')
    if not pid:
        st.info('افتح مشروعًا أولًا.')
        return
    versions = repo.versions(pid)
    final = next((v for v in versions if v['stage']=='final' and v['content']), None)
    if not final:
        st.info('لسه مفيش سكريبت نهائي محفوظ.')
        return
    st.markdown(final['content'])
    download_text('تحميل TXT', final['content'], 'minds10-script.txt')
