from core.models import ProjectSettings,ProjectState
from core.context import PipelineContext
from engines.research.engine import ResearchEngine
class Dummy:
    def generate(self,*args,**kwargs): raise AssertionError('external search was invoked while disabled')
def test_off_gate():
    s=ProjectState(project_id='x',settings=ProjectSettings(web_research=False),input_text='x')
    ResearchEngine().run(PipelineContext(s),Dummy())
    assert s.metadata['research_status']=='disabled_by_user'
