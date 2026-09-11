from core.contracts import SkillManifest

MANIFEST = SkillManifest(
    name="storytelling_ar_eg",
    version="1.0.0",
    skill_type="planning",
    stage="pre_write",
    engine="story",
    description="بناء قصصي للفيديو الطويل بدون اختراع وقائع.",
    depends_on=["topic", "strategy"],
    requires_llm=True,
    input_schema={"topic": "str", "strategy": "dict"},
    output_schema={
        "situation": "str",
        "tension": "str",
        "payoff": "str",
    },
)