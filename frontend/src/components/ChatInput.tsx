import { FormEvent, useState } from "react";

type ChatInputProps = {
  disabled?: boolean;
  onSend: (message: string) => Promise<void> | void;
};

export function ChatInput({ disabled = false, onSend }: ChatInputProps) {
  const [draft, setDraft] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draft.trim();

    if (!message || disabled) {
      return;
    }

    setDraft("");
    await onSend(message);
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <textarea
        value={draft}
        disabled={disabled}
        placeholder="Type a message…"
        rows={3}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            event.currentTarget.form?.requestSubmit();
          }
        }}
      />
      <button type="submit" disabled={disabled || draft.trim().length === 0}>
        Send
      </button>
    </form>
  );
}
