import { useEffect, useState } from "react";
import { getChatHistory, getSkills, importSkillFolder, sendChatMessage, uploadSkillAvatar } from "./api/client";
import { ChatInput } from "./components/ChatInput";
import { ChatWindow } from "./components/ChatWindow";
import { SkillImport } from "./components/SkillImport";
import { SkillSelector } from "./components/SkillSelector";
import type { AvatarType, ChatHistoryMessage, ChatMessage, Skill } from "./types/chat";

function createMessageId() {
  return `${Date.now()}-${crypto.randomUUID()}`;
}

function App() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selectedSkillId, setSelectedSkillId] = useState("");
  const [messagesBySkillId, setMessagesBySkillId] = useState<Record<string, ChatMessage[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedMessages = selectedSkillId ? messagesBySkillId[selectedSkillId] ?? [] : [];
  const selectedSkill = skills.find((skill) => skill.id === selectedSkillId) ?? null;

  function getSkillSessionId(skillId: string) {
    return `web-session:${skillId}`;
  }

  function appendSkillMessage(skillId: string, message: ChatMessage) {
    setMessagesBySkillId((currentMessagesBySkillId) => ({
      ...currentMessagesBySkillId,
      [skillId]: [...(currentMessagesBySkillId[skillId] ?? []), message],
    }));
  }

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

  useEffect(() => {
    let ignore = false;

    async function loadSkillHistory() {
      if (!selectedSkillId) {
        return;
      }

      try {
        setError(null);
        const history = await getChatHistory(selectedSkillId, getSkillSessionId(selectedSkillId));
        if (ignore) {
          return;
        }

        setMessagesBySkillId((currentMessagesBySkillId) => ({
          ...currentMessagesBySkillId,
          [selectedSkillId]: history.map(historyMessageToChatMessage),
        }));
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Failed to load chat history.");
        }
      }
    }

    loadSkillHistory();

    return () => {
      ignore = true;
    };
  }, [selectedSkillId]);

  async function handleImportSkill(files: File[]) {
    setError(null);
    const importedSkill = await importSkillFolder(files);
    await refreshSkills(importedSkill.id);
  }

  async function handleAvatarUpload(avatarType: AvatarType, file: File) {
    if (!selectedSkillId) {
      setError("Please select a character Skill before uploading an avatar.");
      return;
    }

    try {
      setError(null);
      const response = await uploadSkillAvatar(selectedSkillId, avatarType, file);
      const cacheBustedAvatarUrl = `${response.avatar_url}?v=${Date.now()}`;

      setSkills((currentSkills) =>
        currentSkills.map((skill) => {
          if (skill.id !== selectedSkillId) {
            return skill;
          }

          return {
            ...skill,
            ai_avatar_url: avatarType === "ai" ? cacheBustedAvatarUrl : skill.ai_avatar_url,
            user_avatar_url: avatarType === "user" ? cacheBustedAvatarUrl : skill.user_avatar_url,
          };
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to upload avatar.");
    }
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

    appendSkillMessage(selectedSkillId, userMessage);
    setIsSending(true);
    setError(null);

    try {
      const response = await sendChatMessage({
        session_id: getSkillSessionId(selectedSkillId),
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

      appendSkillMessage(selectedSkillId, assistantMessage);
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
        <ChatWindow
          aiAvatarUrl={selectedSkill?.ai_avatar_url ?? null}
          userAvatarUrl={selectedSkill?.user_avatar_url ?? null}
          messages={selectedMessages}
          isSending={isSending}
          onAvatarUpload={handleAvatarUpload}
        />
        <ChatInput disabled={chatDisabled} onSend={handleSend} />
      </section>
    </main>
  );
}

export default App;

function historyMessageToChatMessage(message: ChatHistoryMessage): ChatMessage {
  return {
    id: `history-${message.id}`,
    role: message.role,
    text: message.text,
  };
}
