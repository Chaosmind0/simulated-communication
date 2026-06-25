import type { AvatarType, ChatMessage } from "../types/chat";
import { MessageBubble } from "./MessageBubble";

type ChatWindowProps = {
  aiAvatarUrl?: string | null;
  userAvatarUrl?: string | null;
  messages: ChatMessage[];
  isSending: boolean;
  onAvatarUpload: (avatarType: AvatarType, file: File) => Promise<void>;
};

export function ChatWindow({ aiAvatarUrl, userAvatarUrl, messages, isSending, onAvatarUpload }: ChatWindowProps) {
  return (
    <section className="chat-window" aria-live="polite">
      {messages.length === 0 ? (
        <div className="empty-state">
          <strong>Start a character chat</strong>
          <span>Select a Character Skill, then send a message.</span>
        </div>
      ) : (
        messages.map((message) => (
          <MessageBubble
            key={message.id}
            aiAvatarUrl={aiAvatarUrl}
            userAvatarUrl={userAvatarUrl}
            message={message}
            onAvatarUpload={onAvatarUpload}
          />
        ))
      )}
      {isSending ? <div className="typing-indicator">Assistant is preparing a mock reply…</div> : null}
    </section>
  );
}
