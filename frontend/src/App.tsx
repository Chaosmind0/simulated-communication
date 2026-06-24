import { useEffect, useMemo, useState } from "react";
import { getSkills, getVoices, sendChatMessage } from "./api/client";
import { ChatInput } from "./components/ChatInput";
import { ChatWindow } from "./components/ChatWindow";
import { SkillSelector } from "./components/SkillSelector";
import { VoiceSelector } from "./components/VoiceSelector";
import type { ChatMessage, Skill, Voice } from "./types/chat";

function createMessageId() {
  return `${Date.now()}-${crypto.randomUUID()}`;
}

function App() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [voices, setVoices] = useState<Voice[]>([]);
  const [selectedSkillId, setSelectedSkillId] = useState("");
  const [selectedVoiceId, setSelectedVoiceId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sessionId = useMemo(() => crypto.randomUUID(), []);

  useEffect(() => {
    let ignore = false;

    async function loadOptions() {
      try {
        setIsLoading(true);
        setError(null);
        const [skillsData, voicesData] = await Promise.all([getSkills(), getVoices()]);

        if (ignore) {
          return;
        }

        setSkills(skillsData);
        setVoices(voicesData);
        setSelectedSkillId(skillsData[0]?.id ?? "");
        setSelectedVoiceId(voicesData[0]?.id ?? "");
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Failed to load chat options.");
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    loadOptions();

    return () => {
      ignore = true;
    };
  }, []);

  async function handleSend(messageText: string) {
    if (!selectedSkillId) {
      setError("Please select a character Skill before sending a message.");
      return;
    }

    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      text: messageText,
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setIsSending(true);
    setError(null);

    try {
      const response = await sendChatMessage({
        session_id: sessionId,
        skill_id: selectedSkillId,
        voice_id: selectedVoiceId || undefined,
        message: messageText,
      });

      const assistantMessage: ChatMessage = {
        id: createMessageId(),
        role: "assistant",
        text: response.reply_text,
        audio_url: response.audio_url,
        emotion: response.emotion,
        motion: response.motion,
      };

      setMessages((currentMessages) => [...currentMessages, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message.");
    } finally {
      setIsSending(false);
    }
  }

  const chatDisabled = isLoading || isSending || !selectedSkillId || !selectedVoiceId;

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Testing MVP</p>
          <h1>Simulated Character Communication</h1>
          <p className="subtitle">QQ-style mock chat powered by the local FastAPI test endpoints.</p>
        </div>
      </header>

      <section className="control-panel" aria-label="Chat setup">
        <SkillSelector
          skills={skills}
          selectedSkillId={selectedSkillId}
          disabled={isLoading || isSending}
          onChange={setSelectedSkillId}
        />
        <VoiceSelector
          voices={voices}
          selectedVoiceId={selectedVoiceId}
          disabled={isLoading || isSending}
          onChange={setSelectedVoiceId}
        />
      </section>

      {isLoading ? <div className="status-banner">Loading Skills and Voices…</div> : null}
      {error ? <div className="status-banner status-banner-error">{error}</div> : null}

      <section className="chat-card">
        <ChatWindow messages={messages} isSending={isSending} />
        <ChatInput disabled={chatDisabled} onSend={handleSend} />
      </section>
    </main>
  );
}

export default App;
