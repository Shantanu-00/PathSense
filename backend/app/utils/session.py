# app/utils/session.py

import uuid
from typing import Any, Dict

_sessions: Dict[str, Dict[str, Any]] = {}

def get_session(session_id: str | None) -> tuple[str, Dict[str, Any]]:
    if session_id is None or session_id not in _sessions:
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            'intent': {},
            'route': {
                'places': [],      # Regular places to visit
                'start': None,     # Fixed start point (separate)
                'end': None,       # Fixed end point (separate)
                'last_query': {}
            },
            'history': []
        }
    return session_id, _sessions[session_id]

def store_in_session(session_id: str, data: Dict[str, Any]) -> None:
    if session_id not in _sessions:
        get_session(session_id)
    _sessions[session_id].update(data)

def get_from_session(session_id: str) -> Dict[str, Any]:
    return _sessions.get(session_id, {})