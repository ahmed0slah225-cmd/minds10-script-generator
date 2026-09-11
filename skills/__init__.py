"""
تسجيل كل الـSkills في الـSkillRegistry المركزي.
لا تُستخدم الـSkills مباشرة خارج الـPipeline المُسجّل — دي مرجع.
"""
from core.registry import skill_registry  # noqa: F401
from skills.humanize_ar_eg import MANIFEST as HUMANIZE_MANIFEST  # noqa: F401
from skills.anti_slop_ar_eg import MANIFEST as ANTI_SLOP_MANIFEST  # noqa: F401
from skills.retention_ar_eg import MANIFEST as RETENTION_MANIFEST  # noqa: F401
from skills.viral_hooks_ar_eg import MANIFEST as HOOKS_MANIFEST  # noqa: F401
from skills.storytelling_ar_eg import MANIFEST as STORY_MANIFEST  # noqa: F401
from skills.dumpify_ar_eg import MANIFEST as DUMPIFY_MANIFEST  # noqa: F401
from skills.voice_dna_ar_eg import MANIFEST as VOICE_DNA_MANIFEST  # noqa: F401

# تسجيل كل skill بدون Handler (الـEngines هي المنفذ الفعلي)
for m in (
    HUMANIZE_MANIFEST,
    ANTI_SLOP_MANIFEST,
    RETENTION_MANIFEST,
    HOOKS_MANIFEST,
    STORY_MANIFEST,
    DUMPIFY_MANIFEST,
    VOICE_DNA_MANIFEST,
):
    skill_registry.register(m, handler=lambda *a, **kw: None)