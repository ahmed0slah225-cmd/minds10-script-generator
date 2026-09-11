from pathlib import Path

SKILLS = {
    "humanize": "skills/humanize_ar_eg/SKILL.md",
    "addictive": "skills/addictive_writing_ar_eg/SKILL.md",
    "stop_slop": "skills/stop_slop_ar_eg/SKILL.md",
    "general_writing": "skills/general_writing_ar_eg/SKILL.md",
    "storytelling": "skills/storytelling_ar_eg/SKILL.md",
    "hooks": "skills/viral_hooks_ar_eg/SKILL.md",
    "dumbify": "skills/dumbify_ar_eg/SKILL.md",
    "voice_dna": "skills/voice_dna_ar_eg/SKILL.md",
}

def load(names):
    root = Path(__file__).resolve().parents[1]
    blocks = []
    for name in names:
        path = root / SKILLS[name]
        if path.exists():
            blocks.append(path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(blocks)
