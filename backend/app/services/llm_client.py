import os

from openai import AsyncOpenAI

from app.core.config import get_runtime_settings


class LLMConfigurationError(RuntimeError):
    """Raised when an LLM mode is enabled without required settings."""


class LLMProviderError(RuntimeError):
    """Raised when an OpenAI-compatible provider request fails."""


class LLMEmptyResponseError(RuntimeError):
    """Raised when the provider returns no usable assistant text."""


def get_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMConfigurationError("CHAT_MODE=openai requires OPENAI_API_KEY to be set.")

    return AsyncOpenAI(api_key=api_key, timeout=30.0)


def get_local_client() -> AsyncOpenAI:
    settings = get_runtime_settings()
    if not settings.local_llm_base_url:
        raise LLMConfigurationError("CHAT_MODE=local requires LOCAL_LLM_BASE_URL to be set.")
    if not settings.local_llm_model:
        raise LLMConfigurationError("CHAT_MODE=local requires LOCAL_LLM_MODEL to be set.")

    return AsyncOpenAI(
        base_url=settings.local_llm_base_url,
        api_key=settings.local_llm_api_key or "not-needed",
        timeout=30.0,
    )


def _extract_reply_text(response, provider_name: str) -> str:
    if not response.choices:
        raise LLMEmptyResponseError(f"{provider_name} response did not include any choices.")

    reply_text = response.choices[0].message.content
    if not reply_text or not reply_text.strip():
        raise LLMEmptyResponseError(f"{provider_name} response did not include assistant text.")

    return reply_text.strip()


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

    return _extract_reply_text(response, "OpenAI")


async def generate_local_reply(system_prompt: str, user_message: str) -> str:
    settings = get_runtime_settings()
    client = get_local_client()

    try:
        response = await client.chat.completions.create(
            model=settings.local_llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.8,
        )
    except Exception as exc:
        raise LLMProviderError(
            "Local LLM request failed. "
            f"Is an OpenAI-compatible server running at {settings.local_llm_base_url}? {exc}"
        ) from exc

    return _extract_reply_text(response, "Local LLM")
