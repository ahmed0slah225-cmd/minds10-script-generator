import streamlit as st
from ui.components import title
from core.session import set_project
def render(repo,settings):
 title('المشاريع')
 for p in repo.list_projects(settings.workspace_id):
  with st.container(border=True):
   st.write(f"**{p['title']}**")
   st.caption(f"{p['task_type']} · {p['current_stage']} · {p['status']}")
   if st.button('فتح',key=f"open_{p['id']}"): set_project(p['id']); st.rerun()
