def test_architecture_imports():
    from core.orchestrator import Orchestrator
    from engines.hook.engine import HookEngine
    from engines.retention.engine import RetentionEngine
    from engines.research.engine import ResearchEngine
    assert Orchestrator and HookEngine and RetentionEngine and ResearchEngine
