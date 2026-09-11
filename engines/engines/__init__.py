"""
كل الـEngines تُصدَّر من هنا — نقطة استيراد واحدة آمنة.
أي فشل يظهر باسم المحرك وسبب الفشل بدون ما يكسر باقي التطبيق.
"""
import traceback

ENGINE_IMPORT_ERRORS: list = []

def _safe_import(module_name: str, class_name: str):
    try:
        mod = __import__(module_name, fromlist=[class_name])
        return getattr(mod, class_name)
    except Exception as e:
        ENGINE_IMPORT_ERRORS.append({
            "module": module_name,
            "class": class_name,
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
        })
        return None


InputEngine        = _safe_import("engines.input_engine",        "InputEngine")
TopicEngine        = _safe_import("engines.topic_engine",        "TopicEngine")
ResearchEngine     = _safe_import("engines.research_engine",     "ResearchEngine")
KnowledgeEngine    = _safe_import("engines.knowledge_engine",    "KnowledgeEngine")
AudienceEngine     = _safe_import("engines.audience_engine",     "AudienceEngine")
StrategyEngine     = _safe_import("engines.strategy_engine",     "StrategyEngine")
StoryEngine        = _safe_import("engines.story_engine",        "StoryEngine")
HookEngine         = _safe_import("engines.hook_engine",         "HookEngine")
ScriptEngine       = _safe_import("engines.script_engine",       "ScriptEngine")
HumanizeEngine     = _safe_import("engines.humanize_engine",     "HumanizeEngine")
AntiSlopEngine     = _safe_import("engines.anti_slop_engine",    "AntiSlopEngine")
RetentionEngine    = _safe_import("engines.retention_engine",    "RetentionEngine")
FinalEditorEngine  = _safe_import("engines.final_editor_engine", "FinalEditorEngine")


__all__ = [
    "InputEngine", "TopicEngine", "ResearchEngine", "KnowledgeEngine",
    "AudienceEngine", "StrategyEngine", "StoryEngine", "HookEngine",
    "ScriptEngine", "HumanizeEngine", "AntiSlopEngine", "RetentionEngine",
    "FinalEditorEngine", "ENGINE_IMPORT_ERRORS",
]
