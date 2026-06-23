import os

from openai import AsyncOpenAI


def get_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required only when real LLM mode is enabled.")

    return AsyncOpenAI(api_key=api_key)


async def generate_reply(system_prompt: str, user_message: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = get_client()

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.8,
    )

    return response.choices[0].message.content or ""
