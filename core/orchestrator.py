from __future__ import annotations
import uuid,time
from .context import PipelineContext
from .llm_provider import LLMProvider
from .observability import RunLog,now_iso
from .validation import final_gate
from .storage import ProjectStore
from engines.input.router import route_input
from engines.topic.engine import TopicEngine
from engines.source.engine import SourceEngine
from engines.research.engine import ResearchEngine
from engines.knowledge.engine import KnowledgeEngine
from engines.audience.engine import AudienceEngine
from engines.strategy.engine import StrategyEngine
from engines.story.engine import StoryEngine
from engines.retention.engine import RetentionEngine
from engines.hook.engine import HookEngine
from engines.script.engine import ScriptEngine
from engines.humanize.engine import HumanizeEngine
from engines.review.engine import ReviewEngine
from engines.repetition.engine import RepetitionEngine
from engines.egyptian.engine import EgyptianEngine
from engines.voice.engine import VoiceEngine
from engines.truth.engine import TruthEngine
from engines.final_editor.engine import FinalEditorEngine

class Orchestrator:
    def __init__(self,llm:LLMProvider,store:ProjectStore|None=None):
        self.llm=llm; self.store=store
        self.stages=[route_input,TopicEngine(),SourceEngine(),ResearchEngine(),KnowledgeEngine(),AudienceEngine(),StrategyEngine(),StoryEngine(),RetentionEngine(),HookEngine(),ScriptEngine(),HumanizeEngine(),ReviewEngine(),RepetitionEngine(),EgyptianEngine(),VoiceEngine(),TruthEngine(),FinalEditorEngine()]
    def run(self,ctx:PipelineContext,start_at:int=0):
        for stage in self.stages[start_at:]:
            name=getattr(stage,'name',getattr(stage,'__name__','stage')); run_id=str(uuid.uuid4()); started=time.perf_counter(); ts=now_iso()
            try:
                stage.run(ctx,self.llm) if not (stage is route_input) else stage(ctx,self.llm)
                elapsed=int((time.perf_counter()-started)*1000); ctx.record(name,status='ok',elapsed_ms=elapsed)
                if self.store: self.store.save_run(run_id,ctx.state.project_id,RunLog(run_id,ctx.state.project_id,name,name,getattr(stage,'skill',None),ctx.settings.model_label,ts,elapsed,'ok',input_chars=len(ctx.state.input_text),output_chars=len(ctx.state.draft or ctx.state.final_script)).as_dict())
            except Exception as exc:
                ctx.record(name,status='error',error=str(exc))
                if self.store:
                    self.store.save_run(
                        run_id,
                        ctx.state.project_id,
                        {'status':'error','stage':name,'error':str(exc)}
                    )
                raise
        ctx.state.metadata['trace']=ctx.trace
        ok,errors=final_gate(ctx.state); ctx.state.metadata['final_gate']={'passed':ok,'errors':errors}
        if not ok: raise RuntimeError('Final quality gate failed: '+' | '.join(errors))
        ctx.state.version+=1
        if self.store: self.store.save_project(ctx.state)
        return ctx
