"""Chat history persistence — stores user conversations as JSON files.

Each user gets a directory under data/chat_history/<username>/.
Each conversation is a JSON file named by session timestamp.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

HISTORY_DIR = Path(__file__).parent.parent / "data" / "chat_history"


def _user_dir(username: str) -> Path:
    """Get or create the history directory for a user."""
    d = HISTORY_DIR / username
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_exchange(
    username: str,
    session_id: str,
    user_query: str,
    assistant_response: str,
    agent: str = "",
    confidence: float = 0.0,
    sources: list = None,
    used_web_search: bool = False,
):
    """Append a Q&A exchange to the user's current session file."""
    if not username:
        return

    session_file = _user_dir(username) / f"{session_id}.json"

    # Load existing session or create new
    if session_file.exists():
        with open(session_file, "r") as f:
            session_data = json.load(f)
    else:
        session_data = {
            "session_id": session_id,
            "username": username,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "exchanges": [],
        }

    session_data["exchanges"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": user_query,
        "response": assistant_response,
        "agent": agent,
        "confidence": float(confidence),
        "sources": [s.get("name", "") if isinstance(s, dict) else str(s) for s in (sources or [])],
        "used_web_search": bool(used_web_search),
    })
    session_data["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Use first query as session title
    if len(session_data["exchanges"]) == 1:
        title = user_query[:80]
        session_data["title"] = title + ("…" if len(user_query) > 80 else "")

    with open(session_file, "w") as f:
        json.dump(session_data, f, indent=2, default=str)

    logger.info(f"[History] Saved exchange for {username} in session {session_id}")


def get_sessions(username: str) -> list[dict]:
    """Get all sessions for a user, sorted by most recent first.

    Returns a list of dicts with session metadata (no full exchanges
    to keep it lightweight for the sidebar).
    """
    if not username:
        return []

    user_path = _user_dir(username)
    sessions = []

    for f in sorted(user_path.glob("*.json"), reverse=True):
        try:
            with open(f, "r") as fh:
                data = json.load(fh)
            sessions.append({
                "session_id": data.get("session_id", f.stem),
                "title": data.get("title", "Untitled"),
                "created_at": data.get("created_at", ""),
                "last_updated": data.get("last_updated", ""),
                "exchange_count": len(data.get("exchanges", [])),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    return sessions


def get_session_detail(username: str, session_id: str) -> Optional[dict]:
    """Load a full session with all exchanges."""
    if not username:
        return None

    session_file = _user_dir(username) / f"{session_id}.json"
    if not session_file.exists():
        return None

    with open(session_file, "r") as f:
        return json.load(f)


def delete_session(username: str, session_id: str) -> bool:
    """Delete a session file."""
    if not username:
        return False

    session_file = _user_dir(username) / f"{session_id}.json"
    if session_file.exists():
        session_file.unlink()
        logger.info(f"[History] Deleted session {session_id} for {username}")
        return True
    return False
