from pydantic import BaseModel
from typing import Optional, List


class SkillInfo(BaseModel):
    id: str
    name: str
    description: str
    skill_path: str
    avatar: Optional[str] = None
    ai_avatar_url: Optional[str] = None
    user_avatar_url: Optional[str] = None


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


class ChatResetRequest(BaseModel):
    session_id: str
    skill_id: Optional[str] = None


class ChatResetResponse(BaseModel):
    status: str = "ok"
    cleared: bool = True
    session_id: str


class ChatSessionStatusResponse(BaseModel):
    session_id: str
    message_count: int
    max_history_messages: int


class ChatHistoryMessage(BaseModel):
    id: str
    role: str
    text: str
    created_at: str
    session_id: str
    skill_id: str


class MemoryClearRequest(BaseModel):
    session_id: Optional[str] = None
    skill_id: Optional[str] = None


class MemoryActionResponse(BaseModel):
    status: str = "ok"
    affected_count: int = 0
