import json
import uuid
from pathlib import Path
from typing import Optional

import httpx

from app.core.config import get_runtime_settings


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VOICES_CONFIG_PATH = PROJECT_ROOT / "config" / "voices.json"
AUDIO_CACHE_DIR = PROJECT_ROOT / "audio_cache"


class VoiceboxConfigurationError(RuntimeError):
    """Raised when Voicebox mode is enabled without required voice settings."""


class VoiceboxProviderError(RuntimeError):
    """Raised when the Voicebox request fails or returns an invalid response."""


class VoiceboxEmptyAudioError(RuntimeError):
    """Raised when Voicebox returns no playable audio bytes."""


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
    # Testing-stage voice pipeline placeholder. This intentionally does not call
    # Voicebox or any speech generation service. Returning None keeps the current
    # frontend behavior stable because it already hides audio controls when
    # audio_url is null. The text and voice_id parameters are accepted so the
    # future real Voicebox integration can keep the same call shape.
    _ = (text, voice_id)
    return None


async def generate_voicebox_speech(text: str, voice_id: Optional[str]) -> Optional[str]:
    if not voice_id:
        raise VoiceboxConfigurationError("VOICE_MODE=voicebox requires a voice_id.")

    voice = find_voice(voice_id)
    if not voice:
        raise VoiceboxConfigurationError(f"Voice not found: {voice_id}")

    profile_id = voice.get("voicebox_profile_id")
    if not profile_id or profile_id == "replace_with_voicebox_profile_id":
        raise VoiceboxConfigurationError(f"Voice {voice_id} is missing voicebox_profile_id.")

    settings = get_runtime_settings()
    payload = {
        "profile_id": profile_id,
        "text": text,
        "language": voice.get("language") or "zh",
    }
    if voice.get("engine"):
        payload["engine"] = voice["engine"]

    url = f"{settings.voicebox_base_url.rstrip('/')}/generate/stream"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
    except httpx.RequestError as exc:
        raise VoiceboxProviderError(
            f"Voicebox request failed. Is Voicebox running at {settings.voicebox_base_url}? {exc}"
        ) from exc

    if response.status_code != 200:
        detail = response.text[:300]
        raise VoiceboxProviderError(
            f"Voicebox returned status {response.status_code} from /generate/stream: {detail}"
        )

    content_type = response.headers.get("content-type", "")
    if content_type and not content_type.startswith("audio/"):
        raise VoiceboxProviderError(f"Voicebox returned unexpected content-type: {content_type}")

    audio_bytes = response.content
    if not audio_bytes:
        raise VoiceboxEmptyAudioError("Voicebox returned empty audio bytes.")

    AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.wav"
    (AUDIO_CACHE_DIR / filename).write_bytes(audio_bytes)
    return f"/audio/{filename}"
