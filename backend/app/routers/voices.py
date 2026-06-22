from fastapi import APIRouter
from app.services.voicebox_client import load_voices_config

router = APIRouter()


@router.get("/voices")
def get_voices():
    return load_voices_config()