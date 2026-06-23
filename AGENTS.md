# AGENTS.md

## Project goal

This project is a web-based demo for simulated character communication.

Current MVP goal:

* User can select a character Skill.
* User can select a voice profile.
* User can type text in a QQ-style chat box.
* The frontend sends the message to the FastAPI backend.
* The backend returns a mock assistant reply.
* The frontend displays both user and assistant messages.

Do not implement real OpenAI API calls or real Voicebox integration in the current testing stage.

## Tech stack

Backend:

* Python
* FastAPI
* Pydantic
* Uvicorn

Frontend:

* Vite
* React
* TypeScript

## Backend run command

From the repository root:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Frontend run command

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

## Current testing constraints

* Do not require a real OPENAI_API_KEY.
* Do not call the real Voicebox service.
* Do not add authentication.
* Do not add database persistence.
* Do not add Unity or Live2D features yet.
* Keep the implementation simple and readable.
* The backend `/api/chat` endpoint can return a mock assistant reply during the testing stage.

## Required frontend MVP

Implement or complete:

* `frontend/index.html`
* `frontend/src/main.tsx`
* `frontend/src/App.tsx`
* `frontend/src/types/chat.ts`
* `frontend/src/components/SkillSelector.tsx`
* `frontend/src/components/VoiceSelector.tsx`
* `frontend/src/components/ChatWindow.tsx`
* `frontend/src/components/MessageBubble.tsx`
* `frontend/src/components/ChatInput.tsx`

Expected behavior:

* Load skills from `GET /api/skills`.
* Load voices from `GET /api/voices`.
* Let the user select one Skill and one Voice.
* Let the user type and send a message.
* Send the message to `POST /api/chat`.
* Display user messages on the right.
* Display assistant mock replies on the left.
* If `audio_url` is `null`, do not render audio controls.
* Use a simple QQ-style chat layout.

## Code style

* Use TypeScript types.
* Keep components small.
* Use English comments in code.
* Avoid unnecessary libraries.
* Prefer plain CSS for now.
* Do not introduce Tailwind, UI frameworks, routing, state libraries, or database code for the testing MVP.

## Acceptance criteria

Codex should consider the task complete only when:

* `cd frontend && npm install && npm run dev` works.
* `cd frontend && npm run build` works.
* The frontend page loads successfully in the browser.
* The page shows Skill and Voice selectors.
* The user can send a text message.
* The user message appears in the chat window.
* The backend mock assistant reply appears in the chat window.
* No real OpenAI API call is required.
* No real Voicebox service is required.
