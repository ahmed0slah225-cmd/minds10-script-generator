import streamlit as st

def init():
 defaults={'current_project_id':None,'flash':'','selected_task':'build_video'}
 for k,v in defaults.items(): st.session_state.setdefault(k,v)
def set_project(pid): st.session_state['current_project_id']=pid
