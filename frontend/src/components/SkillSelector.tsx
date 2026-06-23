import type { Skill } from "../types/chat";

type SkillSelectorProps = {
  skills: Skill[];
  selectedSkillId: string;
  disabled?: boolean;
  onChange: (skillId: string) => void;
};

export function SkillSelector({ skills, selectedSkillId, disabled = false, onChange }: SkillSelectorProps) {
  const selectedSkill = skills.find((skill) => skill.id === selectedSkillId);

  return (
    <label className="selector-card">
      <span className="selector-label">Character Skill</span>
      <select
        value={selectedSkillId}
        disabled={disabled || skills.length === 0}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="" disabled>
          Select a skill
        </option>
        {skills.map((skill) => (
          <option key={skill.id} value={skill.id}>
            {skill.name}
          </option>
        ))}
      </select>
      {selectedSkill ? <small>{selectedSkill.description}</small> : null}
    </label>
  );
}
