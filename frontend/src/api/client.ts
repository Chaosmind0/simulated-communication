const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export async function getSkills() {
  const res = await fetch(`${API_BASE_URL}/skills`);
  return res.json();
}

export async function getVoices() {
  const res = await fetch(`${API_BASE_URL}/voices`);
  return res.json();
}

export async function sendChatMessage(payload: {
  session_id: string;
  skill_id: string;
  voice_id?: string;
  message: string;
}) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return res.json();
}