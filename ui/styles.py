import streamlit as st

def inject():
    st.markdown("""<style>
    .block-container{max-width:1250px;padding-top:1.5rem}
    .brand{font-size:1.9rem;font-weight:800}
    .muted{opacity:.72}
    .card{padding:1rem;border:1px solid rgba(128,128,128,.22);border-radius:14px;margin-bottom:.8rem}
    </style>""", unsafe_allow_html=True)
