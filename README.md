# Simulated Communication

A web-based testing-stage demo for simulated character communication. The current MVP lets a user select a character Skill, select a voice profile, type into a QQ-style chat interface, and receive a mock assistant reply from the FastAPI backend.

## Current testing-stage behavior

- The frontend loads Skills from `GET http://127.0.0.1:8000/api/skills`.
- The frontend loads Voices from `GET http://127.0.0.1:8000/api/voices`.
- The frontend sends chat text to `POST http://127.0.0.1:8000/api/chat`.
- The backend validates the selected `skill_id` and `voice_id`, then returns a mock assistant reply.
- Default runtime mode is fully mock-based: `CHAT_MODE=mock` and `VOICE_MODE=mock`.
- Voice generation is mock-only by default; the backend intentionally returns `audio_url: null`, so the frontend does not show audio controls.
- OpenAI and Voicebox are intentionally **not required** in this stage.
- No database, authentication, Unity, or Live2D integration is included yet.

## Project structure

```text
frontend/      Vite + React + TypeScript chat UI
backend/       FastAPI backend with mock chat endpoint
skills/        Example character Skill data
config/        Skill and voice configuration files and examples
```


## Runtime modes

Runtime behavior is controlled by environment variables. Defaults are safe for local testing:

```bash
CHAT_MODE=mock
VOICE_MODE=mock
```

`CHAT_MODE` values:

- `mock` (default): returns the fixed testing-stage assistant reply and does not require `OPENAI_API_KEY`.
- `openai`: reserved for intentional real LLM testing; calls `llm_client.generate_reply()` with the loaded Skill prompt and requires `OPENAI_API_KEY`.

`VOICE_MODE` values:

- `mock` (default): calls `generate_mock_speech()` and returns `audio_url: null`. Voicebox is not required.
- `voicebox`: reserved for future Voicebox integration and currently returns a clear not-implemented error instead of calling a real service.

Copy `.env.example` if you want a local environment file, but do not commit real secrets:

```bash
cp .env.example .env
```

The project does not load `.env` automatically yet; export variables in your shell or use your process manager when testing non-default modes.

## Backend setup and run

From the repository root:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The backend runs at:

- API base URL: `http://127.0.0.1:8000/api`
- Health check: `http://127.0.0.1:8000/api/health`
- Skills: `http://127.0.0.1:8000/api/skills`
- Voices: `http://127.0.0.1:8000/api/voices`

If `config/skills.json` or `config/voices.json` is missing, the backend falls back to `config/skills.example.json` and `config/voices.example.json`.

## Frontend setup and run

In a second terminal, from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend in a browser:

- `http://127.0.0.1:5173/`

Expected behavior:

1. The page shows a Skill selector and a Voice selector.
2. The first available Skill and Voice are selected by default.
3. Type a message in the chat input and press **Send**.
4. The user message appears on the right.
5. The backend mock assistant reply appears on the left.
6. No OpenAI API key or Voicebox service is needed.

## Frontend build check

From the repository root:

```bash
cd frontend
npm run build
```

## Mock mode and error handling

- `/api/chat` stays in mock mode by default for the testing stage.
- `CHAT_MODE=mock` does not call `llm_client.generate_reply()` and does not require `OPENAI_API_KEY`.
- `CHAT_MODE=openai` is opt-in and calls `llm_client.generate_reply()` with the loaded Skill prompt.
- `VOICE_MODE=mock` calls only `generate_mock_speech()`, which is a local placeholder and does not call a real Voicebox service.
- `VOICE_MODE=voicebox` is a guarded future integration path and currently returns a clear not-implemented error instead of making network calls.
- `audio_url` may be `null` during testing; this is expected and the frontend handles it by hiding audio controls.
- Invalid `skill_id` values return a clear `404` HTTP error.
- Invalid `voice_id` values return a clear `404` HTTP error.
- `backend/app/services/llm_client.py` remains in the repository for future real LLM integration, but it is not used by the current mock chat path.

## Useful commands

```bash
# Start backend
cd backend && uvicorn app.main:app --reload --port 8000

# Start frontend dev server
cd frontend && npm run dev

# Build frontend
cd frontend && npm run build
```

## Known limitations and next steps

Current limitations:

- Assistant replies are fixed mock text.
- Speech generation is not implemented.
- `audio_url` is always `null` in mock mode.
- Chat history is held only in frontend memory and disappears on refresh.
- There is no authentication or database persistence.

Recommended next steps after the testing stage:

1. Implement the guarded `VOICE_MODE=voicebox` path only when Voicebox is available.
2. Use `CHAT_MODE=openai` only for intentional real model testing with `OPENAI_API_KEY` configured.
3. Add a real speech generation path only when Voicebox is available and explicitly enabled.
4. Add automated backend and frontend tests for the mock and mode-switching flows.
