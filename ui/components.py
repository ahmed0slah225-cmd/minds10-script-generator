import streamlit as st

def title(text,caption=''):
 st.markdown(f'<div class="brand">{text}</div>',unsafe_allow_html=True)
 if caption: st.caption(caption)

def card(title,body=''):
 st.markdown(f'<div class="card"><b>{title}</b><br>{body}</div>',unsafe_allow_html=True)

def download_text(label,text,filename): st.download_button(label,text,file_name=filename,mime='text/plain',use_container_width=True)
