import json
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VOICES_CONFIG_PATH = PROJECT_ROOT / "config" / "voices.json"


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

