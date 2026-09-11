import streamlit as st, json
from ui.components import title
def render(repo,settings):
 title('Voice DNA','أدخل عينات من كتابتك ليبقى صوتك محفوظًا للمشاريع القادمة.')
 name=st.text_input('اسم الصوت',value='صوتي الرئيسي')
 samples=st.text_area('عينات الكتابة','',height=250,placeholder='الصق هنا 1-3 نصوص قصيرة من كتابتك.')
 if st.button('حفظ Voice DNA',type='primary') and samples.strip():
  profile={'language':'ar-EG','notes':'صوت مصري شخصي مستخرج من عينات المستخدم'}
  repo.save_voice(settings.workspace_id,name,profile,[('sample',samples)]); st.success('تم الحفظ.')
 for p in repo.list_voice(settings.workspace_id):
  st.write('•',p['name'])
