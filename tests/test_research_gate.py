from core.models import ProjectSettings,ProjectState
from core.context import PipelineContext
from engines.research.engine import ResearchEngine
class Dummy:
    def generate(self,*args,**kwargs): raise AssertionError('Search must not execute when OFF')
def test_web_search_off_is_hard_gate():
    state=ProjectState(project_id='p',settings=ProjectSettings(web_research=False),input_text='x')
    ResearchEngine().run(PipelineContext(state),Dummy())
    assert state.metadata['research_status']=='disabled_by_user'
