from core.models import ProjectSettings,ProjectState,KnowledgeItem

def test_project_defaults():
    s=ProjectState(project_id='p1',settings=ProjectSettings())
    assert s.settings.model_label=='Gemini 3.6 Flash'; assert s.settings.web_research is False

def test_provenance_is_explicit():
    k=KnowledgeItem(id='k',kind='fact',text='x',provenance='user_provided',confidence=1,verified=True)
    assert k.verified and k.provenance=='user_provided'
