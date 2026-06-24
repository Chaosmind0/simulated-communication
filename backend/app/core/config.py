import os
from dataclasses import dataclass


CHAT_MODE_MOCK = "mock"
CHAT_MODE_OPENAI = "openai"
CHAT_MODE_LOCAL = "local"
VOICE_MODE_MOCK = "mock"
VOICE_MODE_VOICEBOX = "voicebox"

SUPPORTED_CHAT_MODES = {CHAT_MODE_MOCK, CHAT_MODE_OPENAI, CHAT_MODE_LOCAL}
SUPPORTED_VOICE_MODES = {VOICE_MODE_MOCK, VOICE_MODE_VOICEBOX}


@dataclass(frozen=True)
class RuntimeSettings:
    chat_mode: str = CHAT_MODE_MOCK
    voice_mode: str = VOICE_MODE_MOCK
    openai_model: str = "gpt-4o-mini"
    local_llm_base_url: str = "http://127.0.0.1:1234/v1"
    local_llm_model: str = "local-model"
    local_llm_api_key: str = "not-needed"
    voicebox_base_url: str = "http://127.0.0.1:17493"


def _read_mode(name: str, default: str) -> str:
    return os.getenv(name, default).strip().lower()


def get_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        chat_mode=_read_mode("CHAT_MODE", CHAT_MODE_MOCK),
        voice_mode=_read_mode("VOICE_MODE", VOICE_MODE_MOCK),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        local_llm_base_url=os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:1234/v1"),
        local_llm_model=os.getenv("LOCAL_LLM_MODEL", "local-model"),
        local_llm_api_key=os.getenv("LOCAL_LLM_API_KEY", "not-needed"),
        voicebox_base_url=os.getenv("VOICEBOX_BASE_URL", "http://127.0.0.1:17493"),
    )
