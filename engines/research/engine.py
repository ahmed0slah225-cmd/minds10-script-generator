from engines.base import LLMEngine
from core.prompting import skill_prompt
from core.llm_provider import parse_json
from core.output_normalizer import normalize_structured_output, StructuredOutputError


class ResearchEngine(LLMEngine):
    name='research'; skill='deep_research_ar_eg'; temperature=.35

    def task(self,ctx):
        return f'ابحث خارجيًا فقط عما تحتاجه الاستراتيجية. عمق البحث={ctx.settings.research_depth}. ابدأ بأسئلة المعرفة الناقصة. أخرج JSON يحتوي research_questions, findings, sources، مع provenance وURL ووقت الجمع وconfidence. لا تخترع روابط أو تحققًا.'

    def run(self,ctx,llm):
        if not ctx.settings.web_research:
            ctx.state.metadata['research_status']='disabled_by_user'
            return
        r=llm.generate(
            skill_prompt(self.skill,self.task(ctx),self.context_text(ctx),ctx.state.voice_dna),
            model_label=ctx.settings.model_label,
            json_mode=True,
            web_search=True,
            temperature=self.temperature,
        )
        try:
            d=normalize_structured_output(self.name, parse_json(r.text))
        except StructuredOutputError as exc:
            raise RuntimeError(str(exc)) from exc
        except Exception as exc:
            raise RuntimeError(f'{self.name}: structured output غير صالح: {exc}') from exc
        self.apply(ctx,d)
        ctx.record(self.name,model=r.model_id,run_id=r.run_id)

    def apply(self,ctx,d):
        from core.models import Source,KnowledgeItem
        for i,s in enumerate(d.get('sources',[])):
            ctx.state.sources.append(Source(id=s.get('id',f'web-{i}'),title=s.get('title','مصدر'),url=s.get('url'),kind='web',provenance='web_research',collected_at=s.get('collected_at'),original=s.get('original'),confidence=float(s.get('confidence',0))))
        for i,x in enumerate(d.get('findings',[])):
            ctx.state.knowledge.append(KnowledgeItem(id=x.get('id',f'kw-{i}'),kind='evidence',text=x.get('claim',''),provenance='web_research',source_ids=[x['source_id']] if x.get('source_id') else [],confidence=float(x.get('confidence',0)),verified=bool(x.get('verified',False))))
        ctx.state.metadata['research_questions']=d.get('research_questions',[]); ctx.state.metadata['research_status']='completed'
