import streamlit as st
from config.settings import get_settings
from ui.styles import inject
from ui.navigation import nav

def shell():
 st.set_page_config(page_title='Minds10',page_icon='🎬',layout='wide')
 inject(); st.sidebar.markdown('## 🎬 Minds10'); st.sidebar.caption('Content Intelligence Platform'); return nav()
