from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import FileResponse

from app.services.skill_importer import UploadedSkillFile
from app.services.skill_loader import PROJECT_ROOT, find_skill

AVATAR_TYPES = {"ai", "user"}
AVATAR_EXTENSIONS = ("png", "jpg", "jpeg", "webp", "gif")
AVATAR_MEDIA_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
}
MAX_AVATAR_BYTES = 5 * 1024 * 1024


def avatar_url(skill_id: str, avatar_type: str) -> str:
    return f"/api/skills/{skill_id}/avatar/{avatar_type}"


def _validate_avatar_type(avatar_type: str) -> str:
    if avatar_type not in AVATAR_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="avatar_type must be 'ai' or 'user'.")
    return avatar_type


def _resolve_skill_dir(skill_id: str) -> Path:
    try:
        skill = find_skill(skill_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    project_root = PROJECT_ROOT.resolve()
    skill_dir = (PROJECT_ROOT / skill["skill_path"]).resolve()
    if not skill_dir.is_relative_to(project_root):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsafe Skill path.")
    if not skill_dir.exists() or not skill_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill folder not found: {skill_id}")
    return skill_dir


def _detect_image_extension(upload: UploadedSkillFile) -> str:
    filename_suffix = Path(upload.filename or "").suffix.lower().lstrip(".")
    content = upload.content

    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        detected = "png"
    elif content.startswith(b"\xff\xd8\xff"):
        detected = "jpg"
    elif content.startswith((b"GIF87a", b"GIF89a")):
        detected = "gif"
    elif len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        detected = "webp"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded avatar must be a PNG, JPG, WEBP, or GIF image.")

    if filename_suffix and filename_suffix not in AVATAR_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported avatar file extension.")
    return detected


def _avatar_path(skill_dir: Path, avatar_type: str, extension: str) -> Path:
    return skill_dir / f"avatar_{avatar_type}.{extension}"


def find_avatar_file(skill_id: str, avatar_type: str) -> Path | None:
    avatar_type = _validate_avatar_type(avatar_type)
    skill_dir = _resolve_skill_dir(skill_id)
    for extension in AVATAR_EXTENSIONS:
        candidate = _avatar_path(skill_dir, avatar_type, extension)
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def get_skill_avatar_urls(skill_id: str) -> dict[str, str | None]:
    try:
        ai_avatar_exists = find_avatar_file(skill_id, "ai") is not None
        user_avatar_exists = find_avatar_file(skill_id, "user") is not None
    except HTTPException:
        ai_avatar_exists = False
        user_avatar_exists = False

    return {
        "ai_avatar_url": avatar_url(skill_id, "ai") if ai_avatar_exists else None,
        "user_avatar_url": avatar_url(skill_id, "user") if user_avatar_exists else None,
    }


async def save_skill_avatar(skill_id: str, avatar_type: str, upload: UploadedSkillFile) -> dict:
    avatar_type = _validate_avatar_type(avatar_type)
    skill_dir = _resolve_skill_dir(skill_id)

    if len(upload.content) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Avatar image is too large.")
    if not upload.content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Avatar image is empty.")

    extension = _detect_image_extension(upload)

    for old_extension in AVATAR_EXTENSIONS:
        old_path = _avatar_path(skill_dir, avatar_type, old_extension)
        if old_path.exists():
            old_path.unlink()

    destination = _avatar_path(skill_dir, avatar_type, extension).resolve()
    if not destination.is_relative_to(skill_dir.resolve()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsafe avatar path.")
    destination.write_bytes(upload.content)

    return {
        "status": "ok",
        "skill_id": skill_id,
        "avatar_type": avatar_type,
        "avatar_url": avatar_url(skill_id, avatar_type),
    }


def serve_skill_avatar(skill_id: str, avatar_type: str) -> FileResponse:
    avatar_type = _validate_avatar_type(avatar_type)
    avatar_file = find_avatar_file(skill_id, avatar_type)
    if avatar_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar image not found.")

    extension = avatar_file.suffix.lower().lstrip(".")
    return FileResponse(avatar_file, media_type=AVATAR_MEDIA_TYPES.get(extension, "application/octet-stream"))
