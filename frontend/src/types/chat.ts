export type Skill = {
  id: string;
  name: string;
  description: string;
  skill_path: string;
  avatar?: string | null;
  ai_avatar_url?: string | null;
  user_avatar_url?: string | null;
};

export type Voice = {
  id: string;
  display_name: string;
  voicebox_profile_id: string;
  language: string;
  engine?: string | null;
  linked_skill_id?: string | null;
};

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
  audio_url?: string | null;
  emotion?: string;
  motion?: string;
};

export type ChatRequest = {
  session_id: string;
  skill_id: string;
  voice_id?: string;
  message: string;
};

export type ChatResponse = {
  reply_text: string;
  audio_url: string | null;
  emotion: string;
  motion: string;
};

export type AvatarType = "ai" | "user";

export type SkillAvatarResponse = {
  status: "ok";
  skill_id: string;
  avatar_type: AvatarType;
  avatar_url: string;
};
