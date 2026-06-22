import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
VOICES_CONFIG_PATH = PROJECT_ROOT / "config" / "voices.json"


def load_voices_config():
    if not VOICES_CONFIG_PATH.exists():
        fallback_path = PROJECT_ROOT / "config" / "voices.example.json"
        with fallback_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    with VOICES_CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)