from app.models.schemas import ChatRequest, ChatResponse
from app.services.skill_loader import load_skill_prompt


async def generate_chat_reply(request: ChatRequest) -> ChatResponse:
    skill_prompt = load_skill_prompt(request.skill_id)

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