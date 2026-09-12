from .models import ProjectSettings,ProjectState,Source
from .context import PipelineContext
from .orchestrator import Orchestrator
import uuid

def new_project(input_text:str,settings:ProjectSettings,source_text:str='')->PipelineContext:
    state=ProjectState(project_id='p-'+uuid.uuid4().hex[:10],settings=settings,input_text=input_text,source_text=source_text)
    if source_text.strip(): state.sources.append(Source(id='user-source',title='مواد المستخدم',kind='user_text',provenance='user_provided',confidence=1.0,content=source_text))
    return PipelineContext(state)

def run_pipeline(input_text,settings,source_text,llm,store=None): return Orchestrator(llm,store).run(new_project(input_text,settings,source_text))
