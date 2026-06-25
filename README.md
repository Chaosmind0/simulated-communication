# Simulated Communication

A web-based testing-stage demo for simulated character communication. The current MVP lets a user select a character Skill, select a voice profile, type into a QQ-style chat interface, and receive a mock assistant reply from the FastAPI backend.

## Current testing-stage behavior

- The frontend loads Skills from `GET http://127.0.0.1:8000/api/skills`.
- The frontend loads Voices from `GET http://127.0.0.1:8000/api/voices`.
- The frontend sends chat text to `POST http://127.0.0.1:8000/api/chat`.
- The backend validates the selected `skill_id` and `voice_id`, groups chat by `session_id`, and returns a mock assistant reply by default.
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

- `mock` (default): returns the fixed testing-stage assistant reply and does not require `OPENAI_API_KEY` or a local LLM server.
- `openai`: opt-in real text mode; calls `llm_client.generate_reply()` with the loaded Skill prompt as the system prompt and requires `OPENAI_API_KEY`.
- `local`: opt-in local text mode; calls an OpenAI-compatible local server, such as LM Studio or llama.cpp server, with the loaded Skill prompt as the system prompt and does not require OpenAI quota.

`VOICE_MODE` values:

- `mock` (default): calls `generate_mock_speech()` and returns `audio_url: null`. Voicebox is not required.
- `voicebox`: reserved for a future TTS release; in the current MVP it returns a clear deferred-feature error and does not call Voicebox.

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

Conversation history is stored in memory per `session_id`. It is limited to the most recent 10 user/assistant messages and is cleared when the backend restarts. To clear one session manually, call `POST http://127.0.0.1:8000/api/chat/reset` with `{ "session_id": "..." }`; the response includes `status: "ok"` and `cleared: true`. To inspect one session without exposing message text, call `GET http://127.0.0.1:8000/api/chat/session/{session_id}` for `session_id`, `message_count`, and `max_history_messages`.



## Conversation diagnostics

Conversation history is in-memory only and is intended for development testing. It is keyed by `session_id`, capped at the latest 10 user/assistant messages, and is not persisted across backend restarts.

Reset one session:

```bash
curl -X POST http://127.0.0.1:8000/api/chat/reset \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"your-session-id"}'
```

Inspect one session without returning full message content:

```bash
curl http://127.0.0.1:8000/api/chat/session/your-session-id
```

The diagnostics response includes `session_id`, `message_count`, and `max_history_messages` only.

## Long-term memory

Long-term memory is also in-memory only during the testing stage. It is separate from short-term conversation history:

- Short-term history stores recent user/assistant turns for a `session_id` and is sent as chat history.
- Long-term memory stores small extracted facts, not raw transcripts, and is retrieved separately under a `Relevant long-term memory` system section for `CHAT_MODE=openai` and `CHAT_MODE=local`.

Memory categories:

- `user_profile`: stable facts such as user name or preferred nickname.
- `user_preference`: stable preferences or repeatedly stated interests.
- `relationship`: relationship state between a user/session and a character; scoped to the current `skill_id`.
- `world_or_project_context`: stable project, story, world, or repo context.
- `temporary_note`: explicitly remembered low-scope notes.

Memory confidence:

- `high`: explicitly stated stable facts, such as “remember that ...” or “my name is ...”.
- `medium`: likely useful inferred facts, such as preferences or project context.
- `low`: reserved for uncertain notes; low-confidence memories are not retrieved for normal chat.

The extractor should store stable names, nicknames, preferences, important project facts, and relationship-relevant facts. It should not store one-time random numbers unless explicitly important, temporary test content, secrets, passwords, API keys, tokens, private keys, sensitive personal data by default, or large raw transcripts.

Memory retrieval is scoped and limited. Normal chat retrieves only high/medium confidence memories for the current `session_id`, includes relationship memories only for the matching `skill_id`, and limits prompt injection to the top 5 relevant memories.

Development memory endpoints:

```bash
# List memories for a session, optionally filtered by skill_id
curl 'http://127.0.0.1:8000/api/memory?session_id=your-session-id'

# Disable a memory without deleting it
curl -X POST http://127.0.0.1:8000/api/memory/<memory-id>/disable

# Delete a memory by id
curl -X DELETE http://127.0.0.1:8000/api/memory/<memory-id>

# Clear memories for a session, optionally with a skill_id
curl -X POST http://127.0.0.1:8000/api/memory/clear \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"your-session-id"}'
```

Long-term memory is not persisted to a database and is cleared by backend restart. These endpoints are development tools only and should be revisited before adding authentication or production persistence.

## OpenAI text mode (optional)

Default local development should stay in mock mode. To intentionally test real model-generated text replies, keep voice output mocked and start the backend with OpenAI mode enabled:

```bash
export CHAT_MODE=openai
export VOICE_MODE=mock
export OPENAI_API_KEY=replace_with_your_key
export OPENAI_MODEL=gpt-4o-mini
cd backend
uvicorn app.main:app --reload --port 8000
```

In this mode, `/api/chat` loads the selected Skill prompt with `load_skill_prompt()` and passes it as the system prompt to the OpenAI-compatible chat client. If `OPENAI_API_KEY` is missing, the endpoint returns a clear error instead of crashing. Voicebox should remain disabled with `VOICE_MODE=mock`; real Voicebox integration is reserved for a later stage.


## Local LLM mode (optional)

Use `CHAT_MODE=local` to call an OpenAI-compatible local server without using OpenAI billing or quota. Keep voice output mocked for now:

```bash
export CHAT_MODE=local
export VOICE_MODE=mock
export LOCAL_LLM_BASE_URL=http://127.0.0.1:1234/v1
export LOCAL_LLM_MODEL=<the loaded model identifier>
export LOCAL_LLM_API_KEY=not-needed
cd backend
uvicorn app.main:app --reload --port 8000
```

For LM Studio, start the local server in LM Studio, load a model, and set `LOCAL_LLM_MODEL` to the model identifier shown by the server. Ollama or llama.cpp can also be used if they expose an OpenAI-compatible `/v1` endpoint. In local mode, `/api/chat` sends the Skill prompt, recent session history, and the current user message to the local server. If the local server is not running or the model name is missing, `/api/chat` returns a clear error instead of crashing.

## Voice and TTS roadmap

The current MVP is text-only. `VOICE_MODE=mock` remains the only active voice behavior and `/api/chat` returns `audio_url: null`. The active Voice Profile selector has been removed from the UI; voice selection and playback are future TTS work.

If `VOICE_MODE=voicebox` is set now, the backend returns a clear error explaining that Voicebox integration is deferred. It does not call Voicebox, does not use `/generate/stream`, and does not create audio files.

Future roadmap items:

- Voicebox / TTS integration using a supported streaming endpoint.
- Audio playback in the frontend once real `audio_url` values are produced.
- Preset/cloned profile and engine/language compatibility handling.
- Audio cache retention and cleanup policy.
- Live2D voice and motion synchronization.

`VOICEBOX_BASE_URL` may remain in `.env.example` as a future optional setting, but it is ignored while `VOICE_MODE=mock`.


## Importing Character Skills

The frontend includes an **Import Character Skill** button near the Character Skill selector. Choose a local folder containing at least these files:

- `SKILL.md`
- `persona.md`
- `knowledge.md`

The browser uploads the selected folder to `POST /api/skills/import` as multipart form data. The backend validates the folder, rejects unsafe paths or binary/oversized files, saves it under `skills/imported/<safe_skill_id>/`, and updates `config/skills.json` so it appears in `GET /api/skills`. If `config/skills.json` does not exist, it is created from the example Skill config plus the imported Skill.

Imported Skill entries look like:

```json
{
  "id": "safe_skill_id",
  "name": "Display Name",
  "description": "Imported character skill.",
  "skill_path": "skills/imported/safe_skill_id",
  "avatar": null
}
```

Simple `name` and `description` front matter in `SKILL.md` is used when available; otherwise the display name is inferred from the folder name. Uploaded files are treated as text/data only and are never executed.



## Persistent chat history and memory

The backend initializes a local SQLite database at `data/app.db` on startup. This file is local-only and is ignored by git through the existing `*.db` rule.

SQLite stores:

- `conversations`: Skill-scoped browser/backend conversation sessions.
- `messages`: every persisted user and assistant chat message.
- `memories`: long-term memory records, including category, confidence, disabled state, and optional Skill scope.

The frontend uses stable Skill-scoped session IDs such as `web-session:<skill_id>`, so closing and reopening the browser can reload the same selected Skill history through `GET /api/chat/history?skill_id=<skill_id>&session_id=web-session:<skill_id>`. Switching Skills loads only that Skill's stored messages.

Useful persistence endpoints:

- `GET /api/chat/history?skill_id=<skill_id>` loads stored messages for a Skill.
- `POST /api/chat/reset` clears a session, or one Skill session when `skill_id` is included in the payload.
- `GET /api/memory?skill_id=<skill_id>` lists stored memories for development inspection.
- `DELETE /api/memory/{memory_id}` deletes one memory record.
- `POST /api/memory/clear` clears memories for a session and/or Skill scope.

To fully reset local persistence during development, stop the backend and delete `data/app.db`; it will be recreated on the next backend startup. Do not store API keys, tokens, or secrets in chat messages or memory.

## Per-Skill chat avatars

Each Character Skill can have separate chat avatars for assistant and user messages:

- AI / assistant avatar: `avatar_ai.png` (or another supported image extension such as `.jpg`, `.webp`, or `.gif`)
- User avatar: `avatar_user.png` (or another supported image extension such as `.jpg`, `.webp`, or `.gif`)

Click the AI icon on an assistant message or the user icon on a user message to upload or replace that Skill's avatar. Uploaded avatars are validated as image files, limited to 5 MB, saved inside the selected Skill folder, and served through safe API URLs such as `GET /api/skills/{skill_id}/avatar/ai` and `GET /api/skills/{skill_id}/avatar/user`. If no avatar exists, the chat keeps the fallback labels `AI` and `我`.

Imported Skill folders may include `avatar_ai.png` and/or `avatar_user.png`; those files are preserved during import and shown automatically when the imported Skill is selected. Uploaded files are never executed.

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

1. The page shows a Character Skill selector and an Import Character Skill button.
2. The first available Skill is selected by default.
3. Type a message in the chat input and press **Send**.
4. The user message appears on the right.
5. The backend mock assistant reply appears on the left.
6. Switching Character Skills shows that Skill's own frontend chat messages and uses a Skill-scoped backend session ID.
7. No OpenAI API key or Voicebox service is needed.

## Frontend build check

From the repository root:

```bash
cd frontend
npm run build
```

## Mock mode and error handling

- `/api/chat` stays in mock mode by default for the testing stage.
- `CHAT_MODE=mock` does not call `llm_client.generate_reply()` and does not require `OPENAI_API_KEY`.
- `CHAT_MODE=openai` is opt-in and calls `llm_client.generate_reply()` with the loaded Skill prompt as the system prompt. Missing API keys, provider failures, and empty model responses are returned as clear HTTP errors.
- `CHAT_MODE=local` is opt-in and calls an OpenAI-compatible local server using `LOCAL_LLM_BASE_URL`, `LOCAL_LLM_MODEL`, and `LOCAL_LLM_API_KEY`. Local server failures and empty responses are returned as clear HTTP errors.
- `CHAT_MODE=openai` and `CHAT_MODE=local` include recent in-memory session history after the system Skill prompt. The frontend scopes browser session IDs by selected Skill so short-term context does not mix between characters.
- `VOICE_MODE=mock` calls only `generate_mock_speech()`, which is a local placeholder and does not call a real Voicebox service. The active frontend Voice Profile selector is removed for the text-only MVP.
- `VOICE_MODE=voicebox` is currently deferred and returns a clear error without making network calls.
- `audio_url` is expected to be `null` in the current text-only MVP, and the frontend does not render audio controls.
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

- Assistant replies are fixed mock text unless `CHAT_MODE=openai` or `CHAT_MODE=local` is explicitly enabled.
- Speech generation is deferred; mock mode returns no audio.
- `audio_url` is always `null` in mock mode.
- Backend conversation history and long-term memory are in-memory only, grouped by `session_id`, and disappear on backend restart or the relevant reset/clear endpoint.
- There is no authentication or database persistence.

Recommended next steps after the testing stage:

1. Future: Voicebox / TTS integration.
2. Use `CHAT_MODE=openai` only for intentional real text testing with `OPENAI_API_KEY` configured, or `CHAT_MODE=local` with an OpenAI-compatible local server.
3. Future: audio playback in the frontend, profile engine compatibility handling, and Live2D voice/motion synchronization.
4. Add automated backend and frontend tests for the mock and mode-switching flows.
