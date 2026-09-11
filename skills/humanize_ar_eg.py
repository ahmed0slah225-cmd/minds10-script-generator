from core.contracts import SkillManifest

MANIFEST = SkillManifest(
    name="humanize_ar_eg",
    version="1.0.0",
    skill_type="rewrite",
    stage="post_write",
    engine="humanize",
    description="تحسين النص إنسانيًا بدون اختراع أو تغيير معنى.",
    depends_on=["voice_dna_ar_eg", "script"],
    requires_llm=True,
    input_schema={"draft": "str", "voice_dna": "dict", "audience": "dict"},
    output_schema={"humanized": "str", "warnings": "list"},
)