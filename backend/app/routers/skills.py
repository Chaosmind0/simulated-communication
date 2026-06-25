import re

from fastapi import APIRouter, HTTPException, Request, status

from app.services.skill_avatar_service import get_skill_avatar_urls, save_skill_avatar, serve_skill_avatar
from app.services.skill_importer import UploadedSkillFile, import_skill_folder
from app.services.skill_loader import load_skills_config

router = APIRouter()


def _parse_content_disposition(value: str) -> dict[str, str]:
    result = {}
    for part in value.split(";"):
        if "=" not in part:
            continue
        key, raw_value = part.strip().split("=", 1)
        result[key.lower()] = raw_value.strip().strip('"')
    return result


def _parse_multipart_form(content_type: str, body: bytes) -> tuple[list[UploadedSkillFile], dict[str, str]]:
    boundary_match = re.search(r"boundary=([^;]+)", content_type)
    if not boundary_match:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing multipart boundary.")

    boundary = boundary_match.group(1).strip().strip('"').encode()
    files: list[UploadedSkillFile] = []
    fields: dict[str, str] = {}

    for part in body.split(b"--" + boundary):
        part = part.strip()
        if not part or part == b"--":
            continue
        if part.endswith(b"--"):
            part = part[:-2].strip()
        if b"\r\n\r\n" not in part:
            continue
        raw_headers, content = part.split(b"\r\n\r\n", 1)
        content = content.removesuffix(b"\r\n")
        headers = {}
        for header_line in raw_headers.decode("utf-8", errors="replace").split("\r\n"):
            if ":" not in header_line:
                continue
            key, value = header_line.split(":", 1)
            headers[key.lower()] = value.strip()

        disposition = _parse_content_disposition(headers.get("content-disposition", ""))
        name = disposition.get("name")
        filename = disposition.get("filename")
        if name in {"files", "file"} and filename:
            files.append(
                UploadedSkillFile(
                    filename=filename,
                    content=content,
                    content_type=headers.get("content-type"),
                )
            )
        elif name:
            fields[name] = content.decode("utf-8", errors="replace")

    return files, fields


@router.get("/skills")
def get_skills():
    return [{**skill, **get_skill_avatar_urls(skill["id"])} for skill in load_skills_config()]


@router.post("/skills/import")
async def import_skill(request: Request):
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("multipart/form-data"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expected multipart/form-data.")

    files, fields = _parse_multipart_form(content_type, await request.body())
    return await import_skill_folder(
        files,
        display_name=fields.get("display_name") or None,
        skill_id=fields.get("skill_id") or None,
    )


@router.post("/skills/{skill_id}/avatar")
async def upload_skill_avatar(skill_id: str, request: Request):
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("multipart/form-data"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expected multipart/form-data.")

    files, fields = _parse_multipart_form(content_type, await request.body())
    avatar_type = fields.get("avatar_type")
    if not avatar_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing avatar_type field.")
    if len(files) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload exactly one avatar file.")

    return await save_skill_avatar(skill_id, avatar_type, files[0])


@router.get("/skills/{skill_id}/avatar/{avatar_type}")
def get_skill_avatar(skill_id: str, avatar_type: str):
    return serve_skill_avatar(skill_id, avatar_type)
