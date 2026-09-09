import streamlit as st
from engines.document_engine import DocumentEngine
from ui.components import title

def render(repo,settings):
 title('Sources & PDF','ارفع PDF نصي، والنظام يحتفظ بالصفحات منفصلة.')
 pid=st.session_state.get('current_project_id')
 if not pid: st.warning('افتح مشروعًا من Workspace أولًا.'); return
 up=st.file_uploader('PDF / TXT / MD',type=['pdf','txt','md'])
 if up and st.button('إضافة المصدر',type='primary'):
  sid=repo.add_source(pid,up.name,'pdf' if up.name.lower().endswith('.pdf') else 'text', '')
  if up.name.lower().endswith('.pdf'):
   doc=DocumentEngine().inspect_pdf(up.getvalue(),up.name,sid)
   for page in doc.pages: repo.add_page(sid,page.page_number,page.text)
   st.success(f'تم إضافة {doc.page_count} صفحة.')
  else:
   text=up.getvalue().decode('utf-8','ignore'); repo.db.execute('UPDATE sources SET content=? WHERE id=?',(text,sid)); st.success('تم إضافة النص.')
 for s in repo.sources(pid):
  st.write(f"**{s['title']}** · {s['source_type']}")
