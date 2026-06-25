import { useEffect, useMemo, useState } from "react";
import { getSkills, importSkillFolder, sendChatMessage } from "./api/client";
import { ChatInput } from "./components/ChatInput";
import { ChatWindow } from "./components/ChatWindow";
import { SkillImport } from "./components/SkillImport";
import { SkillSelector } from "./components/SkillSelector";
import type { ChatMessage, Skill } from "./types/chat";

function createMessageId() {
  return `${Date.now()}-${crypto.randomUUID()}`;
}

function App() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selectedSkillId, setSelectedSkillId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sessionId = useMemo(() => crypto.randomUUID(), []);

  async function refreshSkills(preferredSkillId?: string) {
    const skillsData = await getSkills();
    setSkills(skillsData);
    setSelectedSkillId((currentSkillId) => {
      if (preferredSkillId && skillsData.some((skill) => skill.id === preferredSkillId)) {
        return preferredSkillId;
      }
      if (currentSkillId && skillsData.some((skill) => skill.id === currentSkillId)) {
        return currentSkillId;
      }
      return skillsData[0]?.id ?? "";
    });
  }

  useEffect(() => {
    let ignore = false;

    async function loadOptions() {
      try {
        setIsLoading(true);
        setError(null);
        const skillsData = await getSkills();

        if (ignore) {
          return;
        }

        setSkills(skillsData);
        setSelectedSkillId(skillsData[0]?.id ?? "");
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Failed to load character Skills.");
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

  async function handleImportSkill(files: File[]) {
    setError(null);
    const importedSkill = await importSkillFolder(files);
    await refreshSkills(importedSkill.id);
  }

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

  const chatDisabled = isLoading || isSending || !selectedSkillId;

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Testing MVP</p>
          <h1>Simulated Character Communication</h1>
          <p className="subtitle">QQ-style text chat powered by the local FastAPI endpoints.</p>
        </div>
      </header>

      <section className="control-panel" aria-label="Chat setup">
        <SkillSelector
          skills={skills}
          selectedSkillId={selectedSkillId}
          disabled={isLoading || isSending}
          onChange={setSelectedSkillId}
        />
        <SkillImport disabled={isLoading || isSending} onImport={handleImportSkill} />
      </section>

      {isLoading ? <div className="status-banner">Loading character Skills…</div> : null}
      {error ? <div className="status-banner status-banner-error">{error}</div> : null}

      <section className="chat-card">
        <ChatWindow messages={messages} isSending={isSending} />
        <ChatInput disabled={chatDisabled} onSend={handleSend} />
      </section>
    </main>
  );
}

export default App;
