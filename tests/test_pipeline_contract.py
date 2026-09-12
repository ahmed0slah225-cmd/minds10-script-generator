from core.models import ProjectSettings
from core.pipeline import new_project

def test_new_project_builds_context():
    ctx=new_project('عنوان',ProjectSettings(), 'مادة')
    assert ctx.state.input_text=='عنوان'
    assert ctx.state.sources[0].provenance=='user_provided'
