from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers import skills, voices, chat, memory

app = FastAPI(title="Simulated Communication API")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIO_CACHE_DIR = PROJECT_ROOT / "audio_cache"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


app.include_router(skills.router, prefix="/api")
app.include_router(voices.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
