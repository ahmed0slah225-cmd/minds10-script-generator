# ---- DIAGNOSTIC BLOCK ----
import traceback
import streamlit as st

for _mod, _cls in [
    ("engines.input_engine", "InputEngine"),
    ("engines.topic_engine", "TopicEngine"),
    ("engines.research_engine", "ResearchEngine"),
    ("engines.knowledge_engine", "KnowledgeEngine"),
    ("engines.audience_engine", "AudienceEngine"),
    ("engines.strategy_engine", "StrategyEngine"),
    ("engines.story_engine", "StoryEngine"),
    ("engines.hook_engine", "HookEngine"),
    ("engines.script_engine", "ScriptEngine"),
    ("engines.humanize_engine", "HumanizeEngine"),
    ("engines.anti_slop_engine", "AntiSlopEngine"),
    ("engines.retention_engine", "RetentionEngine"),
    ("engines.final_editor_engine", "FinalEditorEngine"),
]:
    try:
        __import__(_mod, fromlist=[_cls])
    except Exception as e:
        st.error(f"❌ فشل: {_mod}.{_cls} → {type(e).__name__}: {e}")
        st.code(traceback.format_exc())
        st.stop()

from engines.input_engine import InputEngine
from engines.topic_engine import TopicEngine
from engines.research_engine import ResearchEngine
from engines.knowledge_engine import KnowledgeEngine
from engines.audience_engine import AudienceEngine
from engines.strategy_engine import StrategyEngine
from engines.story_engine import StoryEngine
from engines.hook_engine import HookEngine
from engines.script_engine import ScriptEngine
from engines.humanize_engine import HumanizeEngine
from engines.anti_slop_engine import AntiSlopEngine
from engines.retention_engine import RetentionEngine
from engines.final_editor_engine import FinalEditorEngine
# ---- END DIAGNOSTIC ----
