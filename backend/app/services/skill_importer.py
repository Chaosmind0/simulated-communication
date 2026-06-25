import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Optional

from fastapi import HTTPException, status

from app.services.skill_loader import PROJECT_ROOT, SKILLS_CONFIG_PATH, load_skills_config


@dataclass
class UploadedSkillFile:
    filename: str
    content: bytes


IMPORTED_SKILLS_DIR = PROJECT_ROOT / "skills" / "imported"
REQUIRED_SKILL_FILES = {"SKILL.md", "persona.md", "knowledge.md"}
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_BYTES = 5_000_000


def sanitize_skill_id(value: str) -> str:
    safe = re.sub(r"[^a-z0-9_-]+", "-", value.strip().lower())
    safe = re.sub(r"-+", "-", safe).strip("-_")
    return safe or "imported-skill"


def _safe_relative_path(filename: str) -> PurePosixPath:
    normalized = filename.replace("\\", "/").lstrip("/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsafe upload path: {filename}",
        )
    return path


def _strip_common_folder(paths: Iterable[PurePosixPath]) -> dict[PurePosixPath, PurePosixPath]:
    paths = list(paths)
    root_names = {path.parts[0] for path in paths if len(path.parts) > 1}
    required_at_root = {path.name for path in paths if len(path.parts) == 1} & REQUIRED_SKILL_FILES

    if required_at_root == REQUIRED_SKILL_FILES or len(root_names) != 1:
        return {path: path for path in paths}

    common_root = next(iter(root_names))
    stripped = {}
    for path in paths:
        if path.parts[0] != common_root or len(path.parts) == 1:
            stripped[path] = path
            continue
        stripped[path] = PurePosixPath(*path.parts[1:])
    return stripped


def _parse_front_matter(skill_md: str) -> tuple[Optional[str], Optional[str]]:
    if not skill_md.startswith("---"):
        return None, None

    end = skill_md.find("\n---", 3)
    if end == -1:
        return None, None

    name = None
    description = None
    for line in skill_md[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip('"\'')
        if key == "name":
            name = value
        elif key == "description":
            description = value
    return name, description


def _unique_skill_id(base_skill_id: str, existing_ids: set[str]) -> str:
    candidate = base_skill_id
    suffix = 2
    while candidate in existing_ids or (IMPORTED_SKILLS_DIR / candidate).exists():
        candidate = f"{base_skill_id}-{suffix}"
        suffix += 1
    return candidate


async def import_skill_folder(
    files: list[UploadedSkillFile], display_name: Optional[str] = None, skill_id: Optional[str] = None
) -> dict:
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded.")

    raw_files: dict[PurePosixPath, bytes] = {}
    total_bytes = 0
    for upload in files:
        original_path = _safe_relative_path(upload.filename or "uploaded-file")
        content = upload.content
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Uploaded file is too large: {original_path}",
            )
        if b"\x00" in content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported binary file: {original_path}",
            )
        total_bytes += len(content)
        if total_bytes > MAX_TOTAL_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Uploaded Skill folder is too large.",
            )
        raw_files[original_path] = content

    path_map = _strip_common_folder(raw_files.keys())
    relative_files = {safe_path: raw_files[original_path] for original_path, safe_path in path_map.items()}
    present_required = {path.as_posix() for path in relative_files.keys()} & REQUIRED_SKILL_FILES
    if present_required != REQUIRED_SKILL_FILES:
        missing = sorted(REQUIRED_SKILL_FILES - present_required)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded Skill folder is missing required files: {', '.join(missing)}",
        )

    skill_md = relative_files[PurePosixPath("SKILL.md")].decode("utf-8", errors="replace")
    front_matter_name, front_matter_description = _parse_front_matter(skill_md)

    inferred_folder_name = next(iter(raw_files.keys())).parts[0]
    name = display_name or front_matter_name or inferred_folder_name.replace("_", " ").replace("-", " ").title()
    description = front_matter_description or "Imported character skill."

    existing_skills = load_skills_config()
    existing_ids = {skill["id"] for skill in existing_skills}
    base_skill_id = sanitize_skill_id(skill_id or name)
    safe_skill_id = _unique_skill_id(base_skill_id, existing_ids)
    target_dir = IMPORTED_SKILLS_DIR / safe_skill_id
    target_dir.mkdir(parents=True, exist_ok=False)

    for relative_path, content in relative_files.items():
        destination = (target_dir / Path(relative_path.as_posix())).resolve()
        if not destination.is_relative_to(target_dir.resolve()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsafe upload path.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    imported_skill = {
        "id": safe_skill_id,
        "name": name,
        "description": description,
        "skill_path": f"skills/imported/{safe_skill_id}",
        "avatar": None,
    }
    updated_skills = [skill for skill in existing_skills if skill["id"] != safe_skill_id]
    updated_skills.append(imported_skill)

    SKILLS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SKILLS_CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(updated_skills, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return imported_skill
