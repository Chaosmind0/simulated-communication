from fastapi import HTTPException, status

from app.core.config import (
    CHAT_MODE_LOCAL,
    CHAT_MODE_MOCK,
    CHAT_MODE_OPENAI,
    SUPPORTED_CHAT_MODES,
    SUPPORTED_VOICE_MODES,
    VOICE_MODE_MOCK,
    VOICE_MODE_VOICEBOX,
    get_runtime_settings,
)
from app.models.schemas import ChatRequest, ChatResponse
from app.services.conversation_store import (
    MAX_HISTORY_MESSAGES,
    append_exchange,
    clear_session,
    get_message_count,
    get_recent_messages,
)
from app.services.llm_client import (
    LLMConfigurationError,
    LLMEmptyResponseError,
    LLMProviderError,
    generate_local_reply,
    generate_reply,
)
from app.services.skill_loader import find_skill, load_skill_prompt
from app.services.voicebox_client import find_voice, generate_mock_speech, generate_voicebox_speech


MOCK_REPLY_TEXT = (
    "……我在。你的话，我已经听见了。"
    "现在这是一个测试回复，之后会由角色 Skill 和 LLM 生成真正的回答。"
)


async def _generate_reply_text(
    chat_mode: str, skill_prompt: str, user_message: str, history_messages: list[dict]
) -> str:
    if chat_mode == CHAT_MODE_MOCK:
        return MOCK_REPLY_TEXT

    if chat_mode == CHAT_MODE_OPENAI:
        return await _generate_provider_reply(generate_reply, skill_prompt, user_message, history_messages)

    if chat_mode == CHAT_MODE_LOCAL:
        return await _generate_provider_reply(generate_local_reply, skill_prompt, user_message, history_messages)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported CHAT_MODE: {chat_mode}. Supported values: {sorted(SUPPORTED_CHAT_MODES)}",
    )


async def _generate_provider_reply(
    provider, skill_prompt: str, user_message: str, history_messages: list[dict]
) -> str:
    try:
        return await provider(skill_prompt, user_message, history_messages)
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except LLMEmptyResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


async def _generate_audio_url(voice_mode: str, reply_text: str, voice_id: str | None) -> str | None:
    if voice_mode == VOICE_MODE_MOCK:
        return await generate_mock_speech(reply_text, voice_id)

    if voice_mode == VOICE_MODE_VOICEBOX:
        try:
            return await generate_voicebox_speech(reply_text, voice_id)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=str(exc),
            ) from exc

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported VOICE_MODE: {voice_mode}. Supported values: {sorted(SUPPORTED_VOICE_MODES)}",
    )


async def generate_chat_reply(request: ChatRequest) -> ChatResponse:
    settings = get_runtime_settings()

    try:
        selected_skill = find_skill(request.skill_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill not found: {request.skill_id}",
        ) from exc

    if request.voice_id and find_voice(request.voice_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice not found: {request.voice_id}",
        )

    skill_prompt = load_skill_prompt(selected_skill["id"])
    history_messages = get_recent_messages(request.session_id)
    reply_text = await _generate_reply_text(
        settings.chat_mode, skill_prompt, request.message, history_messages
    )
    audio_url = await _generate_audio_url(settings.voice_mode, reply_text, request.voice_id)

    append_exchange(request.session_id, request.message, reply_text)

    return ChatResponse(
        reply_text=reply_text,
        audio_url=audio_url,
        emotion="neutral",
        motion="idle",
    )


def reset_chat_history(session_id: str) -> None:
    clear_session(session_id)


def get_chat_session_status(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "message_count": get_message_count(session_id),
        "max_history_messages": MAX_HISTORY_MESSAGES,
    }
