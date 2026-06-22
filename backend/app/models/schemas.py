from pydantic import BaseModel
from typing import Optional, List


class SkillInfo(BaseModel):
    id: str
    name: str
    description: str
    skill_path: str
    avatar: Optional[str] = None


class VoiceInfo(BaseModel):
    id: str
    display_name: str
    voicebox_profile_id: str
    language: str
    engine: Optional[str] = None
    linked_skill_id: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str
    skill_id: str
    voice_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    reply_text: str
    audio_url: Optional[str] = None
    emotion: str = "neutral"
    motion: str = "idle"