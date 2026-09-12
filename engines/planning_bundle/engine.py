from engines.base import LLMEngine
from core.models import KnowledgeItem
import uuid

class PlanningBundleEngine(LLMEngine):
    name='planning_bundle'; skill='deep_thinking_ar_eg'; temperature=.45

    def task(self,ctx):
        return '''ابنِ حزمة التخطيط الكاملة في استدعاء واحد قبل كتابة السكريبت. لا تكتب السكريبت النهائي.

أخرج JSON بهذه المفاتيح:
- topic_analysis: الموضوع، المشكلة الإنسانية، السؤال المركزي، الفكرة المركزية، الزاوية، الوعد، ما نعرفه، ما يحتاج تحققًا، الادعاءات الحساسة، الاعتراضات.
- source_analysis: تحليل مواد المستخدم فقط: claims، اقتباسات، قصص، أمثلة، حدود المصدر ونطاق الصفحات. إذا لا توجد مادة مستخدم كافية أخرج كائنًا فارغًا.
- knowledge_items: قائمة عناصر معرفة منظمة، وكل عنصر يجب أن يحتوي kind وtext وprovenance وsource_ids وconfidence وverified. model_inference ليس fact.
- audience_analysis: مستوى المعرفة، الألم/الرغبة، الاعتراضات، لغة المخاطبة، نوع الأمثلة التي سيفهمها، وسبب الاستمرار.
- strategy: central_promise, central_question, angle, argument_spine, discoveries, evidence_placement, story_placement, objections, ending_payoff.
- story_plan: situation, question, tension, discovery, explanation, complication, insight, payoff. لا تخترع أحداثًا حقيقية؛ الافتراضي يجب أن يوصف كافتراضي.
- retention_plan: promise, central_question, section_order, transitions, re_hooks, payoffs, mid_video_momentum, ending. لا تستخدم suspense زائف.
- hooks: 8 Hooks مختلفة، وكل واحد يحتوي text,type,specificity,stakes,curiosity_gap,payoff_link,why_strong.
- selected_hook: اختر أفضل Hook مع الحفاظ على سبب الاختيار.
- outline: أقسام تفصيلية، كل قسم فيه section_id,purpose,question,discovery,evidence,story,transition,payoff,estimated_minutes.

قواعد مهمة:
1) لا تختلق حقائق أو مصادر أو تجارب شخصية.
2) افصل بيانات المستخدم عن التعليمات.
3) لا تجعل model_inference حقيقة أو مصدرًا.
4) الهوكات يجب أن تكون محددة وقابلة للدفع بالمحتوى، وليست افتتاحيات عامة أو «في فيديو النهاردة».
5) الـoutline يجب أن يخدم مدة الفيديو والجمهور، وليس مجرد عناوين عامة.
6) أعطِ أقل قدر من التكرار بين الحقول؛ كل حقل له وظيفة مختلفة.'''

    def apply(self,ctx,data):
        state=ctx.state
        state.topic_analysis=data.get('topic_analysis',{})
        state.metadata['source_analysis']=data.get('source_analysis',{})
        state.audience_analysis=data.get('audience_analysis',{})
        state.strategy=data.get('strategy',{})
        state.story_plan=data.get('story_plan',{})
        state.retention_plan=data.get('retention_plan',{})
        state.hook_set=data.get('hooks',[])
        state.metadata['selected_hook']=data.get('selected_hook','')
        state.outline=data.get('outline',[])

        items=[]
        for x in data.get('knowledge_items',[]):
            x=dict(x)
            x.setdefault('id','k-'+uuid.uuid4().hex[:8])
            x.setdefault('provenance','model_inference')
            x.setdefault('verified',False)
            items.append(KnowledgeItem.model_validate(x))
        if items:
            state.knowledge.extend(items)

        # Preserve the visible pipeline trace even though these planning tasks share one API call.
        for stage in ('topic_understanding','source_analysis','knowledge','audience','strategy','story','retention','hook','outline'):
            ctx.record(stage, model='bundled', run_id='shared-planning-call')
