from fastapi import APIRouter
from app.models.schemas import (
    ChatRequest,
    ChatResetRequest,
    ChatResetResponse,
    ChatResponse,
    ChatSessionStatusResponse,
)
from app.services.chat_service import generate_chat_reply, get_chat_session_status, reset_chat_history

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await generate_chat_reply(request)


@router.post("/chat/reset", response_model=ChatResetResponse)
async def reset_chat(request: ChatResetRequest):
    reset_chat_history(request.session_id)
    return ChatResetResponse(session_id=request.session_id)


@router.get("/chat/session/{session_id}", response_model=ChatSessionStatusResponse)
def get_chat_session(session_id: str):
    return get_chat_session_status(session_id)
