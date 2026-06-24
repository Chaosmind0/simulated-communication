import type { ChatRequest, ChatResponse, Skill, Voice } from "../types/chat";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export function resolveBackendUrl(url: string): string {
  if (/^https?:\/\//i.test(url)) {
    return url;
  }

  const apiBase = new URL(API_BASE_URL);
  return `${apiBase.origin}${url.startsWith("/") ? url : `/${url}`}`;
}

async function readJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const details = await res.text();
    throw new Error(details || `Request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function getSkills(): Promise<Skill[]> {
  const res = await fetch(`${API_BASE_URL}/skills`);
  return readJson<Skill[]>(res);
}

export async function getVoices(): Promise<Voice[]> {
  const res = await fetch(`${API_BASE_URL}/voices`);
  return readJson<Voice[]>(res);
}

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return readJson<ChatResponse>(res);
}
