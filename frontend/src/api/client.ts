import type {
  AvatarType,
  ChatHistoryMessage,
  ChatRequest,
  ChatResponse,
  Skill,
  SkillAvatarResponse,
  Voice,
} from "../types/chat";

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

export async function getChatHistory(skillId: string, sessionId?: string): Promise<ChatHistoryMessage[]> {
  const params = new URLSearchParams({ skill_id: skillId });
  if (sessionId) {
    params.set("session_id", sessionId);
  }
  const res = await fetch(`${API_BASE_URL}/chat/history?${params.toString()}`);
  return readJson<ChatHistoryMessage[]>(res);
}

export async function importSkillFolder(files: File[], displayName?: string): Promise<Skill> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file, file.webkitRelativePath || file.name);
  }
  if (displayName?.trim()) {
    formData.append("display_name", displayName.trim());
  }

  const res = await fetch(`${API_BASE_URL}/skills/import`, {
    method: "POST",
    body: formData,
  });

  return readJson<Skill>(res);
}

export async function uploadSkillAvatar(skillId: string, avatarType: AvatarType, file: File): Promise<SkillAvatarResponse> {
  const formData = new FormData();
  formData.append("avatar_type", avatarType);
  formData.append("file", file, file.name);

  const res = await fetch(`${API_BASE_URL}/skills/${encodeURIComponent(skillId)}/avatar`, {
    method: "POST",
    body: formData,
  });

  return readJson<SkillAvatarResponse>(res);
}
