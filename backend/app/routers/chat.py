from typing import Optional

from fastapi import APIRouter, Query
from app.models.schemas import (
    ChatHistoryMessage,
    ChatRequest,
    ChatResetRequest,
    ChatResetResponse,
    ChatResponse,
    ChatSessionStatusResponse,
)
from app.services.chat_service import generate_chat_reply, get_chat_history, get_chat_session_status, reset_chat_history

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await generate_chat_reply(request)


@router.post("/chat/reset", response_model=ChatResetResponse)
async def reset_chat(request: ChatResetRequest):
    reset_chat_history(request.session_id, request.skill_id)
    return ChatResetResponse(session_id=request.session_id)


@router.get("/chat/session/{session_id}", response_model=ChatSessionStatusResponse)
def get_chat_session(session_id: str):
    return get_chat_session_status(session_id)


@router.get("/chat/history", response_model=list[ChatHistoryMessage])
def chat_history(skill_id: str = Query(...), session_id: Optional[str] = None):
    return get_chat_history(skill_id, session_id)
