import streamlit as st
from ui.components import title,card
def render(repo,settings):
 title('لوحة التحكم','مساحة العمل الرئيسية للمشاريع والمصادر والسكريبتات.')
 projects=repo.list_projects(settings.workspace_id)
 c1,c2,c3=st.columns(3); c1.metric('المشاريع',len(projects)); c2.metric('مشاريع نشطة',sum(1 for p in projects if p['status']=='active')); c3.metric('الإصدارات المحفوظة',sum(len(repo.versions(p['id'])) for p in projects))
 if not projects: card('ابدأ من مشروع جديد','من Create / Workspace أنشئ أول مشروع.')
 else:
  for p in projects[:6]: card(p['title'],f"{p['task_type']} — آخر مرحلة: {p['current_stage']}")
