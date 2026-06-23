import os
from dataclasses import dataclass


CHAT_MODE_MOCK = "mock"
CHAT_MODE_OPENAI = "openai"
VOICE_MODE_MOCK = "mock"
VOICE_MODE_VOICEBOX = "voicebox"

SUPPORTED_CHAT_MODES = {CHAT_MODE_MOCK, CHAT_MODE_OPENAI}
SUPPORTED_VOICE_MODES = {VOICE_MODE_MOCK, VOICE_MODE_VOICEBOX}


@dataclass(frozen=True)
class RuntimeSettings:
    chat_mode: str = CHAT_MODE_MOCK
    voice_mode: str = VOICE_MODE_MOCK
    openai_model: str = "gpt-4o-mini"
    voicebox_base_url: str = "http://127.0.0.1:17493"


def _read_mode(name: str, default: str) -> str:
    return os.getenv(name, default).strip().lower()


def get_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        chat_mode=_read_mode("CHAT_MODE", CHAT_MODE_MOCK),
        voice_mode=_read_mode("VOICE_MODE", VOICE_MODE_MOCK),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        voicebox_base_url=os.getenv("VOICEBOX_BASE_URL", "http://127.0.0.1:17493"),
    )
