import { resolveBackendUrl } from "../api/client";
import type { ChatMessage } from "../types/chat";

type MessageBubbleProps = {
  message: ChatMessage;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const audioUrl = message.audio_url ? resolveBackendUrl(message.audio_url) : null;

  return (
    <article className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}>
      <div className="avatar" aria-hidden="true">
        {isUser ? "我" : "AI"}
      </div>
      <div className={`message-bubble ${isUser ? "message-bubble-user" : "message-bubble-assistant"}`}>
        <p>{message.text}</p>
        {audioUrl ? <audio controls src={audioUrl} /> : null}
      </div>
    </article>
  );
}
