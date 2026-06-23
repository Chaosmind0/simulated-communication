import type { Voice } from "../types/chat";

type VoiceSelectorProps = {
  voices: Voice[];
  selectedVoiceId: string;
  disabled?: boolean;
  onChange: (voiceId: string) => void;
};

export function VoiceSelector({ voices, selectedVoiceId, disabled = false, onChange }: VoiceSelectorProps) {
  const selectedVoice = voices.find((voice) => voice.id === selectedVoiceId);

  return (
    <label className="selector-card">
      <span className="selector-label">Voice Profile</span>
      <select
        value={selectedVoiceId}
        disabled={disabled || voices.length === 0}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="" disabled>
          Select a voice
        </option>
        {voices.map((voice) => (
          <option key={voice.id} value={voice.id}>
            {voice.display_name}
          </option>
        ))}
      </select>
      {selectedVoice ? (
        <small>
          {selectedVoice.language}
          {selectedVoice.engine ? ` · ${selectedVoice.engine}` : ""}
        </small>
      ) : null}
    </label>
  );
}
