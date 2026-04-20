"""In-memory session store for conversation history."""
from typing import Dict, List
from langchain_core.messages import BaseMessage, HumanMessage

_sessions: Dict[str, List[BaseMessage]] = {}


def get_history(session_id: str) -> List[BaseMessage]:
    return _sessions.get(session_id, [])


def append_message(session_id: str, message: BaseMessage) -> None:
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append(message)


def new_session() -> str:
    import uuid
    sid = str(uuid.uuid4())
    _sessions[sid] = []
    return sid
