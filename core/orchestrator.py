from __future__ import annotations
import time
import uuid
from .context import PipelineContext
from .llm_provider import LLMProvider, GeminiProvider
from .observability import RunLog, now_iso
from .validation import final_gate
from .storage import ProjectStore
from engines.input.router import input_router
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
    AUTO_RETRY_DELAY_SECONDS = 5
    DEFAULT_AUTO_RETRIES = 6

    def __init__(self, llm: LLMProvider, store: ProjectStore | None = None):
        self.llm = llm
        self.store = store
        self.stages = [
            input_router, TopicEngine(), SourceEngine(), ResearchEngine(),
            KnowledgeEngine(), AudienceEngine(), StrategyEngine(), StoryEngine(),
            RetentionEngine(), HookEngine(), ScriptEngine(), HumanizeEngine(),
            ReviewEngine(), RepetitionEngine(), EgyptianEngine(), VoiceEngine(),
            TruthEngine(), FinalEditorEngine()
        ]

    @staticmethod
    def _stage_name(stage) -> str:
        return getattr(stage, 'name', getattr(stage, '__name__', 'stage'))

    @staticmethod
    def _save_checkpoint(ctx: PipelineContext, store: ProjectStore | None) -> None:
        ctx.state.metadata['trace'] = ctx.trace
        ctx.state.updated_at = now_iso()
        ctx.state.version += 1
        if store:
            store.save_project(ctx.state)

    def run(
        self,
        ctx: PipelineContext,
        start_at: int | None = None,
        retry_delay: int = AUTO_RETRY_DELAY_SECONDS,
        max_auto_retries: int = DEFAULT_AUTO_RETRIES,
    ):
        if start_at is None:
            start_at = int(ctx.state.metadata.get('resume_stage_index', 0) or 0)
        start_at = max(0, min(start_at, len(self.stages)))

        ctx.state.metadata['run_status'] = 'running'
        ctx.state.metadata['last_error'] = ''
        ctx.state.metadata['last_error_retryable'] = False
        ctx.state.metadata['resume_stage_index'] = start_at
        self._save_checkpoint(ctx, self.store)

        for index in range(start_at, len(self.stages)):
            stage = self.stages[index]
            name = self._stage_name(stage)
            attempt = 0

            while True:
                run_id = str(uuid.uuid4())
                started = time.perf_counter()
                ts = now_iso()
                try:
                    if stage is input_router:
                        stage(ctx, self.llm)
                    else:
                        stage.run(ctx, self.llm)

                    elapsed = int((time.perf_counter() - started) * 1000)
                    ctx.record(name, status='ok', elapsed_ms=elapsed, attempt=attempt + 1)
                    if self.store:
                        self.store.save_run(
                            run_id,
                            ctx.state.project_id,
                            RunLog(
                                run_id, ctx.state.project_id, name, name,
                                getattr(stage, 'skill', None), ctx.settings.model_label,
                                ts, elapsed, 'ok',
                                input_chars=len(ctx.state.input_text),
                                output_chars=len(ctx.state.draft or ctx.state.final_script),
                            ).as_dict(),
                        )

                    ctx.state.metadata['resume_stage_index'] = index + 1
                    ctx.state.metadata['last_error'] = ''
                    ctx.state.metadata['last_error_retryable'] = False
                    self._save_checkpoint(ctx, self.store)
                    break

                except Exception as exc:
                    retryable = GeminiProvider.is_retryable_exception(exc)
                    ctx.record(
                        name,
                        status='error',
                        error=str(exc),
                        attempt=attempt + 1,
                        retryable=retryable,
                    )
                    ctx.state.metadata['resume_stage_index'] = index
                    ctx.state.metadata['failed_stage'] = name
                    ctx.state.metadata['last_error'] = str(exc)
                    ctx.state.metadata['last_error_retryable'] = retryable
                    ctx.state.metadata['auto_retry_attempt'] = attempt + 1
                    self._save_checkpoint(ctx, self.store)

                    if retryable and attempt < max_auto_retries:
                        attempt += 1
                        time.sleep(max(0, retry_delay))
                        continue
                    ctx.state.metadata['run_status'] = 'paused' if retryable else 'failed'
                    self._save_checkpoint(ctx, self.store)
                    raise

        ctx.state.metadata['trace'] = ctx.trace
        ok, errors = final_gate(ctx.state)
        ctx.state.metadata['final_gate'] = {'passed': ok, 'errors': errors}
        if not ok:
            ctx.state.metadata['run_status'] = 'failed'
            self._save_checkpoint(ctx, self.store)
            raise RuntimeError('Final quality gate failed: ' + ' | '.join(errors))

        ctx.state.metadata['resume_stage_index'] = len(self.stages)
        ctx.state.metadata['run_status'] = 'completed'
        ctx.state.metadata['last_error'] = ''
        ctx.state.metadata['last_error_retryable'] = False
        self._save_checkpoint(ctx, self.store)
        return ctx
