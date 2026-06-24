from typing import Dict, List, TypedDict


MAX_HISTORY_MESSAGES = 10


class ConversationMessage(TypedDict):
    role: str
    content: str


_conversations: Dict[str, List[ConversationMessage]] = {}


def get_recent_messages(session_id: str) -> List[ConversationMessage]:
    messages = _conversations.get(session_id, [])
    return list(messages[-MAX_HISTORY_MESSAGES:])


def append_exchange(session_id: str, user_message: str, assistant_reply: str) -> None:
    messages = _conversations.setdefault(session_id, [])
    messages.extend(
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_reply},
        ]
    )
    del messages[:-MAX_HISTORY_MESSAGES]


def clear_session(session_id: str) -> None:
    _conversations.pop(session_id, None)
