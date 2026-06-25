import { ChangeEvent, useEffect, useRef, useState } from "react";
import { resolveBackendUrl } from "../api/client";
import type { AvatarType, ChatMessage } from "../types/chat";

type MessageBubbleProps = {
  aiAvatarUrl?: string | null;
  userAvatarUrl?: string | null;
  message: ChatMessage;
  onAvatarUpload: (avatarType: AvatarType, file: File) => Promise<void>;
};

export function MessageBubble({ aiAvatarUrl, userAvatarUrl, message, onAvatarUpload }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const avatarType: AvatarType = isUser ? "user" : "ai";
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [avatarFailed, setAvatarFailed] = useState(false);
  const avatarUrl = isUser ? userAvatarUrl : aiAvatarUrl;
  const resolvedAvatarUrl = avatarUrl && !avatarFailed ? resolveBackendUrl(avatarUrl) : null;

  useEffect(() => {
    setAvatarFailed(false);
  }, [avatarUrl]);

  async function handleAvatarSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    try {
      setIsUploading(true);
      await onAvatarUpload(avatarType, file);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <article className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}>
      <button
        className="avatar avatar-button"
        type="button"
        disabled={isUploading}
        aria-label={`Upload ${isUser ? "user" : "AI"} avatar`}
        title={`Upload ${isUser ? "user" : "AI"} avatar`}
        onClick={() => inputRef.current?.click()}
      >
        {resolvedAvatarUrl ? <img src={resolvedAvatarUrl} alt="" onError={() => setAvatarFailed(true)} /> : isUser ? "我" : "AI"}
      </button>
      <input
        ref={inputRef}
        className="visually-hidden"
        type="file"
        accept="image/png,image/jpeg,image/webp,image/gif"
        onChange={handleAvatarSelected}
      />
      <div className={`message-bubble ${isUser ? "message-bubble-user" : "message-bubble-assistant"}`}>
        <p>{message.text}</p>
      </div>
    </article>
  );
}
