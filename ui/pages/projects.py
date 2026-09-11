import streamlit as st
from ui.components import title
from core.session import set_project

def render(repo, settings):
    title('المشاريع', 'كل مشاريعك المحفوظة، مع إمكانية فتحها أو حذفها.')
    projects = repo.list_projects(settings.workspace_id)
    if not projects:
        st.info('مفيش مشاريع محفوظة لسه.')
        return

    for p in projects:
        with st.container(border=True):
            st.write(f"**{p['title']}**")
            st.caption(f"{p['task_type']} · المرحلة: {p['current_stage']} · الحالة: {p['status']}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button('فتح المشروع', key=f"open_{p['id']}", use_container_width=True):
                    set_project(p['id'])
                    st.session_state['workspace_project_id'] = p['id']
                    st.rerun()
            with c2:
                confirm = st.checkbox('تأكيد الحذف', key=f"confirm_delete_{p['id']}")
                if st.button('🗑️ حذف المشروع نهائيًا', key=f"delete_{p['id']}", type='secondary', use_container_width=True):
                    if not confirm:
                        st.warning('فعّل «تأكيد الحذف» الأول.')
                    else:
                        repo.delete_project(p['id'])
                        if st.session_state.get('current_project_id') == p['id']:
                            st.session_state.pop('current_project_id', None)
                        if st.session_state.get('workspace_project_id') == p['id']:
                            st.session_state.pop('workspace_project_id', None)
                        st.success('تم حذف المشروع وكل البيانات التابعة له.')
                        st.rerun()
