import type { ChatMessage } from "../types/chat";
import { MessageBubble } from "./MessageBubble";

type ChatWindowProps = {
  messages: ChatMessage[];
  isSending: boolean;
};

export function ChatWindow({ messages, isSending }: ChatWindowProps) {
  return (
    <section className="chat-window" aria-live="polite">
      {messages.length === 0 ? (
        <div className="empty-state">
          <strong>Start a mock chat</strong>
          <span>Select a Skill and Voice, then send a message.</span>
        </div>
      ) : (
        messages.map((message) => <MessageBubble key={message.id} message={message} />)
      )}
      {isSending ? <div className="typing-indicator">Assistant is preparing a mock reply…</div> : null}
    </section>
  );
}
