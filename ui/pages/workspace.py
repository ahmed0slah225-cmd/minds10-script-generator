import streamlit as st
from ui.components import title, download_text
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
from engines.research_engine import ResearchEngine
from engines.knowledge_engine import KnowledgeEngine


def _run_pipeline(repo, settings, pid, p, text, urls_text):
    urls = [u.strip() for u in (urls_text or '').splitlines() if u.strip()]
    client = GeminiClient().client

    analysis = analyze(text, has_file=bool(repo.sources(pid)))
    repo.update_project(pid, input_text=text, current_stage='input', status='active')

    st.write('✅ فهمت الطلب:', analysis.task_type)

    pdf = ''
    if analysis.task_type in ('explain_document', 'summarize_document', 'extract_ideas') and repo.sources(pid):
        src = repo.sources(pid)[0]
        pages = repo.pages(src['id'], analysis.page_start, analysis.page_end) if analysis.page_start else repo.pages(src['id'])
        pdf = '\n\n'.join(f"[صفحة {x['page_number']}]\n{x['text']}" for x in pages)
        st.write(f"📄 تم تجهيز {len(pages)} صفحة من المصدر.")

    research = ''
    if analysis.task_type in ('build_video', 'write_script', 'research_topic'):
        repo.update_project(pid, current_stage='research')
        st.write('🔎 1/7 البحث وتجميع المعلومات...')
        research = ResearchEngine(client).run(text, urls, analysis.task_type)['answer']

    repo.update_project(pid, current_stage='knowledge')
    st.write('🧠 2/7 بناء قاعدة المعرفة...')
    knowledge = KnowledgeEngine(client).run(text, pdf, research, urls_text)

    if analysis.task_type in ('build_video', 'write_script'):
        repo.update_project(pid, current_stage='strategy')
        st.write('🧭 3/7 بناء استراتيجية الفيديو...')
        strategy = StrategyEngine(client).run(text, knowledge, p['duration_minutes'] or 30, p['audience'])

        repo.update_project(pid, current_stage='hooks')
        st.write('🪝 4/7 بناء واختيار الهوك...')
        hooks = HookEngine(client).run(text, knowledge, p['audience'])
        chosen = hooks.get('recommended_id', 1)
        hook_list = hooks.get('hooks', [])
        hook = next((h.get('text', '') for h in hook_list if h.get('id') == chosen), '')
        if not hook and hook_list:
            hook = hook_list[0].get('text', '')

        repo.update_project(pid, current_stage='story')
        st.write('🎬 5/7 بناء الحكاية وتدفق السرد...')
        StoryEngine(client).run(text, knowledge, strategy.get('outline', []))

        repo.update_project(pid, current_stage='script')
        st.write('✍️ 6/7 كتابة السكريبت...')
        script = ScriptEngine(client).write(
            text,
            knowledge,
            strategy,
            hook,
            p['audience'],
            p['duration_minutes'] or 30,
        )

        repo.update_project(pid, current_stage='humanize')
        st.write('🧑 7/7 اللمسة الإنسانية والمراجعة النهائية...')
        human = HumanizationEngine(client).refine(script)
        review = ReviewEngine(client).review(human, knowledge)
        final = EditorEngine(client).finalize(human, review, knowledge)

        repo.save_version(pid, 'final', 'Final Script', final, {'review': review, 'strategy': strategy})
        repo.update_project(pid, current_stage='final', status='completed', input_text=text)
        st.success('🎉 السكريبت خلص واتحفظ في المشروع.')
        st.markdown(final)
        download_text('تحميل السكريبت TXT', final, f"{p['title']}.txt")
        return

    if analysis.task_type == 'research_topic':
        repo.update_project(pid, current_stage='final', status='completed')
        st.success('اكتمل البحث.')
        st.markdown(research)
        return

    if analysis.task_type in ('explain_document', 'summarize_document'):
        from services.gemini.generation import generate_text
        repo.update_project(pid, current_stage='final')
        out = generate_text(
            client,
            f"""اشرح المادة التالية بالعربية المصرية البسيطة. التزم فقط بالمادة. أشر إلى رقم الصفحة عند الإمكان. لا تخترع معلومات.\n{pdf}""",
            system='أنت شارح كتاب محترف، تبسط من غير تسطيح.',
            temperature=0.55,
            max_tokens=9000,
        )
        repo.save_version(pid, 'final', 'Document Explanation', out)
        repo.update_project(pid, current_stage='final', status='completed')
        st.success('تم تجهيز الشرح.')
        st.markdown(out)
        return

    st.json(knowledge)


def render(repo, settings):
    title('Workspace', 'هنا المكان الرئيسي: اكتب فكرتك، وبعدها ابدأ بناء السكريبت.')

    projects = repo.list_projects(settings.workspace_id)
    choice = st.selectbox(
        'المشروع الحالي',
        ['+ مشروع جديد'] + [f"{p['title']}|{p['id']}" for p in projects],
        help='اختار مشروع قديم لاستكماله أو اعمل مشروع جديد من الصفر.'
    )

    if choice == '+ مشروع جديد':
        st.subheader('ابدأ مشروع جديد')
        title_text = st.text_input('اسم المشروع', 'فيديو جديد')
        task = st.selectbox(
            'إنت عايز تعمل إيه؟',
            ['build_video', 'write_script', 'explain_document', 'summarize_document', 'extract_ideas', 'research_topic'],
            format_func=lambda x: {
                'build_video': 'فيديو يوتيوب كامل',
                'write_script': 'سكريبت كامل',
                'explain_document': 'شرح كتاب / PDF',
                'summarize_document': 'تلخيص كتاب / PDF',
                'extract_ideas': 'استخراج أفكار من المصدر',
                'research_topic': 'بحث عن موضوع',
            }[x]
        )
        inp = st.text_area(
            'الفكرة / الطلب / النص',
            height=220,
            placeholder='مثال: اكتبلي فيديو عن ليه بنفقد الشغف بالحياة؟ أو: اشرح من الصفحة 1 إلى الصفحة 20.'
        )
        duration = st.number_input('مدة الفيديو بالدقائق', 1.0, 180.0, 30.0, 0.5)
        audience = st.text_input('الجمهور', 'شباب وبنات يحبوا الحكي والأمثلة والمعلومات الواضحة')

        st.info('بعد إنشاء المشروع هتقدر ترفع PDF من صفحة «Sources & PDF». ولو الفكرة جاهزة، الزر الأول هيعمل المشروع ويبدأ الكتابة مباشرة.')

        c1, c2 = st.columns(2)
        with c1:
            start_now = st.button('🚀 إنشاء المشروع وابدأ الكتابة', type='primary', use_container_width=True)
        with c2:
            create_only = st.button('إنشاء المشروع فقط', use_container_width=True)

        if start_now or create_only:
            if not title_text.strip():
                st.error('اكتب اسم للمشروع الأول.')
                return
            if not inp.strip():
                st.error('اكتب الفكرة أو الطلب الأول.')
                return
            pid = repo.create_project(settings.workspace_id, title_text.strip(), task, inp.strip(), duration, audience.strip())
            set_project(pid)
            p = repo.get_project(pid)
            if start_now:
                st.session_state['auto_start_project'] = pid
                st.rerun()
            st.success('تم إنشاء المشروع. افتح المشروع من القائمة ثم اضغط «ابدأ بناء السكريبت».')
        return

    pid = choice.split('|')[-1]
    set_project(pid)
    p = repo.get_project(pid)
    if not p:
        st.error('المشروع غير موجود أو تم حذفه من قاعدة البيانات.')
        return

    st.subheader(p['title'])
    st.caption(f"الحالة: {p['status']} · المرحلة الحالية: {p['current_stage']}")

    text = st.text_area('الفكرة / الطلب', p.get('input_text', ''), height=180)
    urls = st.text_area('روابط إضافية (اختياري — رابط في كل سطر)', '', height=90)

    c1, c2 = st.columns(2)
    with c1:
        if st.button('🔍 تحليل الطلب', use_container_width=True):
            repo.update_project(pid, input_text=text)
            st.json(analyze(text, has_file=bool(repo.sources(pid))).__dict__)
    with c2:
        start = st.button('🚀 ابدأ بناء السكريبت', type='primary', use_container_width=True)

    st.divider()
    st.markdown('**الخطوة المناسبة دلوقتي:**')
    st.write('1) لو عندك PDF، روح «Sources & PDF» وارفعه للمشروع.')
    st.write('2) ارجع هنا واضغط «🚀 ابدأ بناء السكريبت».')
    st.write('3) لو عندك موضوع فقط، اضغط الزر وهنبدأ البحث والكتابة مباشرة.')

    auto = st.session_state.pop('auto_start_project', None)
    if auto == pid:
        start = True

    if start:
        if not text.strip():
            st.error('اكتب الفكرة أو الطلب الأول.')
            return
        repo.update_project(pid, input_text=text)
        try:
            with st.status('جاري بناء السكريبت...', expanded=True) as status:
                _run_pipeline(repo, settings, pid, p, text, urls)
                status.update(label='اكتمل', state='complete')
        except Exception as e:
            repo.update_project(pid, status='error')
            st.error(f'حصل خطأ أثناء التنفيذ: {e}')
