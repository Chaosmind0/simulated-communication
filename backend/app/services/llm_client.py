import os

from openai import AsyncOpenAI

from app.core.config import get_runtime_settings


class LLMConfigurationError(RuntimeError):
    """Raised when real OpenAI mode is enabled without required settings."""


class LLMProviderError(RuntimeError):
    """Raised when the OpenAI-compatible provider request fails."""


class LLMEmptyResponseError(RuntimeError):
    """Raised when the provider returns no usable assistant text."""


def get_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMConfigurationError("CHAT_MODE=openai requires OPENAI_API_KEY to be set.")

    return AsyncOpenAI(api_key=api_key, timeout=30.0)


async def generate_reply(system_prompt: str, user_message: str) -> str:
    settings = get_runtime_settings()
    client = get_client()

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.8,
        )
    except Exception as exc:
        raise LLMProviderError(f"OpenAI request failed: {exc}") from exc

    if not response.choices:
        raise LLMEmptyResponseError("OpenAI response did not include any choices.")

    reply_text = response.choices[0].message.content
    if not reply_text or not reply_text.strip():
        raise LLMEmptyResponseError("OpenAI response did not include assistant text.")

    return reply_text.strip()
