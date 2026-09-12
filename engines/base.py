from __future__ import annotations
from core.context import PipelineContext
from core.llm_provider import LLMProvider,parse_json
from core.output_normalizer import normalize_structured_output, StructuredOutputError
from core.prompting import skill_prompt

class LLMEngine:
    name='base'; skill=''; temperature=.55; json_mode=True
    def task(self,ctx): raise NotImplementedError
    def context_text(self,ctx): return str(ctx.state.model_dump(exclude={'final_script'}))[:180000]
    def run(self,ctx,llm):
        result=llm.generate(skill_prompt(self.skill,self.task(ctx),self.context_text(ctx),ctx.state.voice_dna),model_label=ctx.settings.model_label,json_mode=self.json_mode,web_search=False,temperature=self.temperature)
        try:
            data=parse_json(result.text)
            data=normalize_structured_output(self.name,data)
        except StructuredOutputError as exc:
            raise RuntimeError(str(exc)) from exc
        except Exception as exc:
            raise RuntimeError(f'{self.name}: structured output غير صالح: {exc}') from exc
        self.apply(ctx,data); ctx.record(self.name,model=result.model_id,run_id=result.run_id)
    def apply(self,ctx,data): raise NotImplementedError

class TextEngine(LLMEngine):
    json_mode=False
    def run_text(self,ctx,llm,skill,task,temperature=.65):
        r=llm.generate(skill_prompt(skill,task,self.context_text(ctx),ctx.state.voice_dna),model_label=ctx.settings.model_label,temperature=temperature,web_search=False); return r.text
