import streamlit as st, json
from ui.components import title,download_text
from core.session import set_project
from engines.input_engine import analyze
from services.gemini import GeminiClient
from engines.strategy_engine import StrategyEngine
from engines.hook_engine import HookEngine
from engines.story_engine import StoryEngine
from engines.script_engine import ScriptEngine
from engines.humanization_engine import HumanizationEngine
from engines.review_engine import ReviewEngine
from engines.editor_engine import EditorEngine
from engines.production_engine import ProductionEngine
from engines.research_engine import ResearchEngine
from engines.knowledge_engine import KnowledgeEngine

def render(repo,settings):
 title('Create / Workspace','هنا بتحدد المطلوب، والـRouter يختار مسار العمل.')
 projects=repo.list_projects(settings.workspace_id)
 choice=st.selectbox('مشروع', ['+ مشروع جديد']+[f"{p['title']}|{p['id']}" for p in projects])
 if choice=='+ مشروع جديد':
  title_text=st.text_input('اسم المشروع','مشروع جديد')
  task=st.selectbox('نوع المهمة',['build_video','write_script','explain_document','summarize_document','extract_ideas','research_topic','improve_script','write_hook'])
  inp=st.text_area('الموضوع / الطلب / النص',height=220,placeholder='مثال: اكتبلي فيديو عن الخوف... أو اشرح من الصفحة 1 للصفحة 20')
  duration=st.number_input('مدة الفيديو بالدقائق',1.0,180.0,30.0,0.5)
  audience=st.text_input('الجمهور','شباب وبنات يحبوا الحكي والأمثلة والمعلومات الواضحة')
  if st.button('إنشاء المشروع',type='primary'):
   pid=repo.create_project(settings.workspace_id,title_text,task,inp,duration,audience); set_project(pid); st.rerun()
  return
 pid=choice.split('|')[-1]; set_project(pid); p=repo.get_project(pid); st.subheader(p['title'])
 text=st.text_area('الطلب',p['input_text'],height=180)
 if st.button('تحليل الطلب'): st.json(analyze(text,has_file=bool(repo.sources(pid))))
 urls=st.text_area('روابط إضافية، رابط في كل سطر','',height=100)
 if st.button('تشغيل خط الإنتاج',type='primary'):
  with st.status('جاري التنفيذ...',expanded=True) as status:
   client=GeminiClient().client
   analysis=analyze(text,has_file=bool(repo.sources(pid))); st.write('نوع المهمة:',analysis.task_type)
   if analysis.task_type in ('explain_document','summarize_document','extract_ideas') and repo.sources(pid):
    src=repo.sources(pid)[0]; pages=repo.pages(src['id'],analysis.page_start,analysis.page_end) if analysis.page_start else repo.pages(src['id'])
    pdf='\n\n'.join(f"[صفحة {x['page_number']}]\n{x['text']}" for x in pages)
   else: pdf=''
   research=''
   if analysis.task_type in ('build_video','write_script','research_topic'):
    research=ResearchEngine(client).run(text,[u.strip() for u in urls.splitlines() if u.strip()],analysis.task_type)['answer']
   knowledge=KnowledgeEngine(client).run(text,pdf,research,urls)
   repo.update_project(pid,current_stage='knowledge',status='active')
   st.write('تم بناء المعرفة.')
   if analysis.task_type in ('build_video','write_script'):
    strategy=StrategyEngine(client).run(text,knowledge,p['duration_minutes'] or 30,p['audience'])
    hooks=HookEngine(client).run(text,knowledge,p['audience']); chosen=hooks.get('recommended_id',1)
    hook_list=hooks.get('hooks',[]); hook=next((h.get('text','') for h in hook_list if h.get('id')==chosen),'') or (hook_list[0].get('text','') if hook_list else '')
    story=StoryEngine(client).run(text,knowledge,strategy.get('outline',[]))
    script=ScriptEngine(client).write(text,knowledge,strategy,hook,p['audience'],p['duration_minutes'] or 30)
    human=HumanizationEngine(client).refine(script)
    review=ReviewEngine(client).review(human,knowledge)
    final=EditorEngine(client).finalize(human,review,knowledge)
    repo.save_version(pid,'final','Final Script',final,{'review':review,'strategy':strategy})
    repo.update_project(pid,current_stage='final',status='completed')
    st.success('تم إنشاء النسخة النهائية.')
    st.markdown(final)
    download_text('تحميل TXT',final,f"{p['title']}.txt")
   elif analysis.task_type=='research_topic': st.markdown(research)
   elif analysis.task_type in ('explain_document','summarize_document'):
    from services.gemini.generation import generate_text
    out=generate_text(client,f"""اشرح المادة التالية بالعربية المصرية البسيطة. التزم فقط بالمادة. أشر إلى رقم الصفحة عند الإمكان. لا تخترع معلومات.
{pdf}""",system='أنت شارح كتاب محترف، تبسط من غير تسطيح.',temperature=0.55,max_tokens=9000)
    repo.save_version(pid,'final','Document Explanation',out)
    repo.update_project(pid,current_stage='final',status='completed'); st.markdown(out)
   else: st.json(knowledge)
   status.update(label='اكتمل',state='complete')
