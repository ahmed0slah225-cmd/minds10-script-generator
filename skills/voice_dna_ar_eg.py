from core.contracts import SkillManifest

MANIFEST = SkillManifest(
    name="voice_dna_ar_eg",
    version="1.0.0",
    skill_type="analysis",
    stage="pre_write",
    engine="voice",  # لا يعمل تلقائيًا — يُستخدم كمرجع
    description="استخراج سمات أسلوبية من عينات سابقة (طول جمل، إيقاع، مفردات، ...).",
    depends_on=[],
    requires_llm=True,
    input_schema={"samples": "list[str]"},
    output_schema={
        "sentence_length": "str",
        "rhythm": "str",
        "vocabulary_level": "str",
        "formality": "str",
        "spontaneity": "str",
    },
)