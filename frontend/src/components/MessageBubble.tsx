import type { ChatMessage } from "../types/chat";

type MessageBubbleProps = {
  message: ChatMessage;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <article className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}>
      <div className="avatar" aria-hidden="true">
        {isUser ? "我" : "AI"}
      </div>
      <div className={`message-bubble ${isUser ? "message-bubble-user" : "message-bubble-assistant"}`}>
        <p>{message.text}</p>
        {message.audio_url ? <audio controls src={message.audio_url} /> : null}
      </div>
    </article>
  );
}
