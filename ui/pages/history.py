import streamlit as st
from ui.components import title
def render(repo,settings):
 title('History','كل إصدار محفوظ داخل كل مشروع.')
 for p in repo.list_projects(settings.workspace_id):
  st.subheader(p['title'])
  for v in repo.versions(p['id']): st.write(f"v{v['version_no']} — {v['stage']} — {v['label']}")
