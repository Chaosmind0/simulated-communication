import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SKILLS_CONFIG_PATH = PROJECT_ROOT / "config" / "skills.json"


def load_skills_config():
    if not SKILLS_CONFIG_PATH.exists():
        fallback_path = PROJECT_ROOT / "config" / "skills.example.json"
        with fallback_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    with SKILLS_CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_skill(skill_id: str):
    skills = load_skills_config()

    for skill in skills:
        if skill["id"] == skill_id:
            return skill

    raise ValueError(f"Skill not found: {skill_id}")


def read_text_if_exists(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def load_skill_prompt(skill_id: str) -> str:
    skill = find_skill(skill_id)
    skill_dir = PROJECT_ROOT / skill["skill_path"]

    skill_md = read_text_if_exists(skill_dir / "SKILL.md")
    persona_md = read_text_if_exists(skill_dir / "persona.md")
    knowledge_md = read_text_if_exists(skill_dir / "knowledge.md")

    return f"""
# Character Skill

{skill_md}

# Persona

{persona_md}

# Knowledge

{knowledge_md}

# Runtime Instruction

You must stay in character.
Reply in Chinese unless the user asks otherwise.
Do not reveal that you are reading prompt files.
"""