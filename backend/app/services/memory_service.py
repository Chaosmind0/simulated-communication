import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import List, Optional

from app.services.database import get_connection


MEMORY_CATEGORIES = {
    "user_profile",
    "user_preference",
    "relationship",
    "world_or_project_context",
    "temporary_note",
}
RETRIEVABLE_CONFIDENCE = {"high", "medium"}
MAX_RETRIEVED_MEMORIES = 5

_SECRET_PATTERN = re.compile(
    r"(api[_ -]?key|token|password|passwd|private[_ -]?key|secret|bearer\s+|sk-[A-Za-z0-9])",
    re.IGNORECASE,
)
_TEMPORARY_PATTERN = re.compile(r"\b(random number|temporary|temp|test content|just testing)\b", re.IGNORECASE)
_IMPORTANT_PATTERN = re.compile(r"\b(important|remember|please remember)\b", re.IGNORECASE)
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


@dataclass
class MemoryRecord:
    id: str
    session_id: str
    skill_id: Optional[str]
    category: str
    confidence: str
    content: str
    disabled: bool
    created_at: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_sensitive(text: str) -> bool:
    return bool(_SECRET_PATTERN.search(text))


def _is_temporary_without_importance(text: str) -> bool:
    return bool(_TEMPORARY_PATTERN.search(text)) and not bool(_IMPORTANT_PATTERN.search(text))


def _guess_category(text: str) -> str:
    lowered = text.lower()
    if any(keyword in lowered for keyword in ["prefer", "like", "favorite", "favourite", "love"]):
        return "user_preference"
    if any(keyword in lowered for keyword in ["relationship", "trust", "friend", "partner"]):
        return "relationship"
    if any(keyword in lowered for keyword in ["project", "story", "world", "setting", "repo"]):
        return "world_or_project_context"
    if any(keyword in lowered for keyword in ["name", "nickname", "call me"]):
        return "user_profile"
    return "temporary_note"


def _classify_memory(text: str) -> Optional[tuple[str, str, str, Optional[str]]]:
    cleaned = text.strip()
    lowered = cleaned.lower()

    remember_match = re.search(r"\b(?:please\s+)?remember(?: that)?\s+(.+)", cleaned, re.IGNORECASE)
    if remember_match:
        fact = remember_match.group(1).strip().rstrip(".")
        category = _guess_category(fact)
        scope = "skill" if category == "relationship" else None
        return category, "high", fact, scope

    name_match = re.search(r"\bmy name is\s+([^,.!?]+)", cleaned, re.IGNORECASE)
    if name_match:
        return "user_profile", "high", f"User name: {name_match.group(1).strip()}", None

    nickname_match = re.search(r"\bcall me\s+([^,.!?]+)", cleaned, re.IGNORECASE)
    if nickname_match:
        return "user_profile", "high", f"Preferred nickname: {nickname_match.group(1).strip()}", None

    preference_match = re.search(
        r"\b(?:i prefer|i like|i love|my favorite|my favourite)\s+(.+)", cleaned, re.IGNORECASE
    )
    if preference_match:
        return "user_preference", "medium", preference_match.group(0).strip().rstrip("."), None

    if any(keyword in lowered for keyword in ["project", "story", "world", "setting", "repo"]):
        return "world_or_project_context", "medium", cleaned, None

    if any(keyword in lowered for keyword in ["relationship", "trust", "friend", "partner"]):
        return "relationship", "medium", cleaned, "skill"

    return None


def _record_from_row(row) -> MemoryRecord:
    return MemoryRecord(
        id=row["id"],
        session_id=row["session_id"],
        skill_id=row["skill_id"],
        category=row["category"],
        confidence=row["confidence"],
        content=row["content"],
        disabled=bool(row["disabled"]),
        created_at=row["created_at"],
    )


def maybe_store_memory(session_id: str, skill_id: str, user_message: str) -> Optional[MemoryRecord]:
    if _is_sensitive(user_message) or _is_temporary_without_importance(user_message):
        return None

    classified = _classify_memory(user_message)
    if not classified:
        return None

    category, confidence, content, scope = classified
    record = MemoryRecord(
        id=str(uuid.uuid4()),
        session_id=session_id,
        skill_id=skill_id if scope == "skill" else None,
        category=category,
        confidence=confidence,
        content=content[:500],
        disabled=False,
        created_at=_now(),
    )
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO memories (id, session_id, skill_id, category, confidence, content, disabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.session_id,
                record.skill_id,
                record.category,
                record.confidence,
                record.content,
                int(record.disabled),
                record.created_at,
            ),
        )
    return record


def list_memories(
    session_id: Optional[str] = None, skill_id: Optional[str] = None, include_disabled: bool = False
) -> List[dict]:
    query = "SELECT * FROM memories WHERE 1 = 1"
    params: list[str | int] = []
    if session_id is not None:
        query += " AND session_id = ?"
        params.append(session_id)
    if skill_id is not None:
        query += " AND (skill_id IS NULL OR skill_id = ?)"
        params.append(skill_id)
    if not include_disabled:
        query += " AND disabled = 0"
    query += " ORDER BY created_at DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [asdict(_record_from_row(row)) for row in rows]


def delete_memory(memory_id: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        return cursor.rowcount > 0


def disable_memory(memory_id: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute("UPDATE memories SET disabled = 1 WHERE id = ?", (memory_id,))
        return cursor.rowcount > 0


def clear_memories(session_id: Optional[str] = None, skill_id: Optional[str] = None) -> int:
    query = "DELETE FROM memories WHERE 1 = 1"
    params: list[str] = []
    if session_id is not None:
        query += " AND session_id = ?"
        params.append(session_id)
    if skill_id is not None:
        query += " AND (skill_id IS NULL OR skill_id = ?)"
        params.append(skill_id)

    with get_connection() as connection:
        cursor = connection.execute(query, params)
        return cursor.rowcount


def get_relevant_memories(session_id: str, skill_id: str, query: str, limit: int = MAX_RETRIEVED_MEMORIES) -> List[dict]:
    query_tokens = set(_TOKEN_PATTERN.findall(query.lower()))
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM memories
            WHERE disabled = 0
              AND session_id = ?
              AND confidence IN ('high', 'medium')
              AND (skill_id IS NULL OR skill_id = ?)
            """,
            (session_id, skill_id),
        ).fetchall()

    candidates = []
    for row in rows:
        record = _record_from_row(row)
        if record.category == "relationship" and record.skill_id != skill_id:
            continue
        content_tokens = set(_TOKEN_PATTERN.findall(record.content.lower()))
        score = len(query_tokens & content_tokens)
        candidates.append((score, record.created_at, record))

    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [asdict(record) for _, _, record in candidates[:limit]]


def format_memories_for_prompt(memories: List[dict]) -> str:
    if not memories:
        return ""

    lines = ["# Relevant long-term memory"]
    for memory in memories:
        lines.append(f"- ({memory['category']}, {memory['confidence']}) {memory['content']}")
    return "\n".join(lines)
