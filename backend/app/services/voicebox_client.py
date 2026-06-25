import json
import uuid
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VOICES_CONFIG_PATH = PROJECT_ROOT / "config" / "voices.json"
AUDIO_CACHE_DIR = PROJECT_ROOT / "audio_cache"


class VoiceboxConfigurationError(RuntimeError):
    """Raised when Voicebox mode is enabled without required voice settings."""


class VoiceboxProviderError(RuntimeError):
    """Raised when the Voicebox request fails or returns an invalid response."""


class VoiceboxEmptyAudioError(RuntimeError):
    """Raised when Voicebox returns no playable audio bytes."""


class VoiceboxDeferredError(RuntimeError):
    """Raised when a caller enables future Voicebox mode in the current text-only MVP."""


class VoiceboxConfigurationError(RuntimeError):
    """Reserved for future Voicebox configuration validation errors."""


class VoiceboxProviderError(RuntimeError):
    """Reserved for future Voicebox provider request errors."""


class VoiceboxEmptyAudioError(RuntimeError):
    """Reserved for future Voicebox empty-audio responses."""


class VoiceboxDeferredError(RuntimeError):
    """Raised when a caller enables future Voicebox mode in the current text-only MVP."""


class VoiceboxConfigurationError(RuntimeError):
    """Reserved for future Voicebox configuration validation errors."""


class VoiceboxProviderError(RuntimeError):
    """Reserved for future Voicebox provider request errors."""


class VoiceboxEmptyAudioError(RuntimeError):
    """Reserved for future Voicebox empty-audio responses."""


class VoiceboxDeferredError(RuntimeError):
    """Raised when a caller enables future Voicebox mode in the current text-only MVP."""


class VoiceboxConfigurationError(RuntimeError):
    """Reserved for future Voicebox configuration validation errors."""


class VoiceboxProviderError(RuntimeError):
    """Reserved for future Voicebox provider request errors."""


class VoiceboxEmptyAudioError(RuntimeError):
    """Reserved for future Voicebox empty-audio responses."""


class VoiceboxDeferredError(RuntimeError):
    """Raised when a caller enables future Voicebox mode in the current text-only MVP."""


class VoiceboxConfigurationError(RuntimeError):
    """Reserved for future Voicebox configuration validation errors."""


class VoiceboxProviderError(RuntimeError):
    """Reserved for future Voicebox provider request errors."""


class VoiceboxEmptyAudioError(RuntimeError):
    """Reserved for future Voicebox empty-audio responses."""


def load_voices_config():
    if not VOICES_CONFIG_PATH.exists():
        fallback_path = PROJECT_ROOT / "config" / "voices.example.json"
        with fallback_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    with VOICES_CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_voice(voice_id: str) -> Optional[dict]:
    voices = load_voices_config()

    for voice in voices:
        if voice["id"] == voice_id:
            return voice

    return None


async def generate_mock_speech(text: str, voice_id: Optional[str]) -> Optional[str]:
    # Current MVP voice behavior: no speech generation and no audio controls.
    # Keep the call shape so future TTS work can be wired in without changing
    # chat_service or frontend message types.
    _ = (text, voice_id)
    return None


async def generate_voicebox_speech(text: str, voice_id: Optional[str]) -> Optional[str]:
    # Voicebox integration is deliberately deferred. Future work must handle
    # preset vs. cloned profile compatibility, engine/language compatibility,
    # audio cache retention, and /generate/stream error handling before enabling
    # this path. Do not call the real Voicebox service in the current MVP.
    _ = (text, voice_id)
    raise VoiceboxDeferredError(
        "VOICE_MODE=voicebox is deferred to a future version. "
        "Use VOICE_MODE=mock for the current text-only MVP."
    )
