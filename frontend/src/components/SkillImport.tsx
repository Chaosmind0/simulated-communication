import { ChangeEvent, useRef, useState } from "react";

type SkillImportProps = {
  disabled?: boolean;
  onImport: (files: File[]) => Promise<void>;
};

const directoryInputProps = {
  webkitdirectory: "",
  directory: "",
} as Record<string, string>;

export function SkillImport({ disabled = false, onImport }: SkillImportProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFilesSelected(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";

    if (files.length === 0) {
      return;
    }

    try {
      setIsImporting(true);
      setError(null);
      await onImport(files);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to import Skill folder.");
    } finally {
      setIsImporting(false);
    }
  }

  return (
    <section className="selector-card skill-import-card" aria-label="Import Character Skill">
      <div>
        <span className="selector-label">Import Character Skill</span>
        <p className="import-helper">Select a local Skill folder containing SKILL.md, persona.md, and knowledge.md.</p>
      </div>
      <input
        ref={inputRef}
        className="visually-hidden"
        type="file"
        multiple
        disabled={disabled || isImporting}
        onChange={handleFilesSelected}
        {...directoryInputProps}
      />
      <button type="button" disabled={disabled || isImporting} onClick={() => inputRef.current?.click()}>
        {isImporting ? "Importing…" : "Import Character Skill"}
      </button>
      {error ? <small className="inline-error">{error}</small> : null}
    </section>
  );
}
