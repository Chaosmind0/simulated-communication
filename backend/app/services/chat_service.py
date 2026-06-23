from fastapi import HTTPException, status

from app.models.schemas import ChatRequest, ChatResponse
from app.services.skill_loader import find_skill, load_skill_prompt
from app.services.voicebox_client import find_voice


async def generate_chat_reply(request: ChatRequest) -> ChatResponse:
    try:
        find_skill(request.skill_id)
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

    # Mock mode: load the selected Skill prompt only to validate local configuration.
    # Do not call the LLM or Voicebox services during the testing stage.
    load_skill_prompt(request.skill_id)

    reply_text = (
        "……我在。你的话，我已经听见了。"
        "现在这是一个测试回复，之后会由角色 Skill 和 LLM 生成真正的回答。"
    )

    return ChatResponse(
        reply_text=reply_text,
        audio_url=None,
        emotion="neutral",
        motion="idle",
    )
