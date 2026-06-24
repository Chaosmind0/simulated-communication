from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResetRequest, ChatResetResponse, ChatResponse
from app.services.chat_service import generate_chat_reply, reset_chat_history

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return await generate_chat_reply(request)


@router.post("/chat/reset", response_model=ChatResetResponse)
async def reset_chat(request: ChatResetRequest):
    reset_chat_history(request.session_id)
    return ChatResetResponse(session_id=request.session_id)
