"""In-memory session store for conversation history and user preferences."""
from typing import Dict, List
from langchain_core.messages import BaseMessage

_sessions: Dict[str, List[BaseMessage]] = {}
_preferences: Dict[str, List[dict]] = {}


def get_history(session_id: str) -> List[BaseMessage]:
    return _sessions.get(session_id, [])


def append_message(session_id: str, message: BaseMessage) -> None:
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append(message)


def get_preferences(session_id: str) -> List[dict]:
    return _preferences.get(session_id, [])


def set_preferences(session_id: str, preferences: List[dict]) -> None:
    _preferences[session_id] = preferences


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
    _preferences.pop(session_id, None)


def new_session() -> str:
    import uuid
    sid = str(uuid.uuid4())
    _sessions[sid] = []
    _preferences[sid] = []
    return sid
