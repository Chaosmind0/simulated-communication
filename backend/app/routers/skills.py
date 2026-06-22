from fastapi import APIRouter
from app.services.skill_loader import load_skills_config

router = APIRouter()


@router.get("/skills")
def get_skills():
    return load_skills_config()