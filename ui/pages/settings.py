import streamlit as st
from ui.components import title
def render(repo,settings):
 title('Settings')
 st.info('الإعدادات الحساسة تُحفظ في Streamlit Secrets أو Environment Variables.')
 st.write({'model':settings.gemini_model,'workspace':settings.workspace_id,'web_research':settings.allow_web_research,'url_context':settings.allow_url_context,'turso_configured':bool(settings.turso_url)})
