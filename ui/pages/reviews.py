import streamlit as st, json
from ui.components import title

def render(repo, settings):
    title('Reviews', 'مراجعات الاحتفاظ والطبيعية والحقائق والأسلوب.')
    pid=st.session_state.get('current_project_id')
    if not pid:
        st.info('افتح مشروعًا أولًا.')
        return
    for r in repo.reviews(pid):
        with st.expander(f"{r['review_type']} — {r['verdict']}"):
            st.json(json.loads(r['content_json']))
