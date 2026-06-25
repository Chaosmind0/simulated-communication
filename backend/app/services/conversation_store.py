from typing import List, Optional, TypedDict

from app.services.database import get_connection

MAX_HISTORY_MESSAGES = 10


class ConversationMessage(TypedDict):
    role: str
    content: str


def _get_or_create_conversation_id(connection, session_id: str, skill_id: str) -> int:
    row = connection.execute(
        "SELECT id FROM conversations WHERE session_id = ? AND skill_id = ?",
        (session_id, skill_id),
    ).fetchone()
    if row:
        return int(row["id"])

    cursor = connection.execute(
        "INSERT INTO conversations (session_id, skill_id) VALUES (?, ?)",
        (session_id, skill_id),
    )
    return int(cursor.lastrowid)


def get_recent_messages(session_id: str, skill_id: str) -> List[ConversationMessage]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM conversations WHERE session_id = ? AND skill_id = ?",
            (session_id, skill_id),
        ).fetchone()
        if not row:
            return []
        messages = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (row["id"], MAX_HISTORY_MESSAGES),
        ).fetchall()
    return [{"role": message["role"], "content": message["content"]} for message in reversed(messages)]


def get_message_count(session_id: str, skill_id: Optional[str] = None) -> int:
    query = """
        SELECT COUNT(*) AS count
        FROM messages
        JOIN conversations ON conversations.id = messages.conversation_id
        WHERE conversations.session_id = ?
    """
    params: list[str] = [session_id]
    if skill_id is not None:
        query += " AND conversations.skill_id = ?"
        params.append(skill_id)

    with get_connection() as connection:
        row = connection.execute(query, params).fetchone()
    return int(row["count"] if row else 0)


def append_exchange(session_id: str, skill_id: str, user_message: str, assistant_reply: str) -> None:
    with get_connection() as connection:
        conversation_id = _get_or_create_conversation_id(connection, session_id, skill_id)
        connection.executemany(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            [
                (conversation_id, "user", user_message),
                (conversation_id, "assistant", assistant_reply),
            ],
        )
        connection.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,),
        )


def clear_session(session_id: str, skill_id: Optional[str] = None) -> None:
    with get_connection() as connection:
        if skill_id is None:
            connection.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
        else:
            connection.execute(
                "DELETE FROM conversations WHERE session_id = ? AND skill_id = ?",
                (session_id, skill_id),
            )


def get_history_for_skill(skill_id: str, session_id: Optional[str] = None) -> list[dict]:
    query = """
        SELECT messages.id, messages.role, messages.content, messages.created_at, conversations.session_id, conversations.skill_id
        FROM messages
        JOIN conversations ON conversations.id = messages.conversation_id
        WHERE conversations.skill_id = ?
    """
    params: list[str] = [skill_id]
    if session_id is not None:
        query += " AND conversations.session_id = ?"
        params.append(session_id)
    query += " ORDER BY messages.id ASC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        {
            "id": str(row["id"]),
            "role": row["role"],
            "text": row["content"],
            "created_at": row["created_at"],
            "session_id": row["session_id"],
            "skill_id": row["skill_id"],
        }
        for row in rows
    ]
