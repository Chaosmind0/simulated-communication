import os

from openai import AsyncOpenAI

from app.core.config import get_runtime_settings


def get_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required only when CHAT_MODE=openai.")

    return AsyncOpenAI(api_key=api_key)


async def generate_reply(system_prompt: str, user_message: str) -> str:
    settings = get_runtime_settings()
    client = get_client()

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.8,
    )

    return response.choices[0].message.content or ""
