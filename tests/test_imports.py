def test_core_imports():
    import config
    from core.models import Project, PipelineState
    from engines.pipeline import Pipeline
    assert config.APP_TITLE
    assert Project and PipelineState and Pipeline
