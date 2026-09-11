import streamlit as st
PAGES=['Dashboard','Projects','Create / Workspace','Sources & PDF','Research','Voice DNA','History','Settings']
def nav(): return st.sidebar.radio('المكان', PAGES)
