import os
import json
import uuid
import requests
from datetime import datetime

DB_FILE = "sessions_db.json"


def fetch_video_title(video_id: str) -> str:
    """
    Fetches the video title from YouTube's public oEmbed service.
    """
    try:
        url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            title = data.get("title")
            if title:
                return title
    except Exception as e:
        print(f"[SM] Error fetching video title for {video_id}: {e}")
    return f"Video {video_id}"


def load_all_sessions() -> list:
    """
    Reads and parses the sessions_db.json file.
    """
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"[SM] Error loading sessions database: {e}")
        return []


def save_all_sessions(sessions: list) -> bool:
    """
    Serializes and writes the list of sessions to sessions_db.json.
    """
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[SM] Error saving sessions database: {e}")
        return False


def create_session(video_id: str, title: str, transcript: str, num_chunks: int) -> str:
    """
    Creates a new chat session linked to a video transcript.
    Returns the unique string ID of the session.
    """
    session_id = uuid.uuid4().hex[:12]  # Short 12-char unique hex ID
    session_doc = {
        "session_id": session_id,
        "video_id": video_id,
        "title": title,
        "transcript": transcript,
        "num_chunks": num_chunks,
        "chat_history": [],
        "qa_pairs_raw": "",
        "quiz_questions": [],
        "quiz_answers": {},
        "quiz_result": None,
        "quiz_submitted": False,
        "last_output": "",
        "original_output": "",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    sessions = load_all_sessions()
    sessions.append(session_doc)
    save_all_sessions(sessions)
    print(f"[SM] Created session {session_id} for video {video_id}.")
    return session_id


def get_session(session_id: str) -> dict:
    """
    Retrieves a session dict by ID.
    """
    sessions = load_all_sessions()
    for sess in sessions:
        if sess.get("session_id") == session_id:
            return sess
    return None


def get_cached_video(video_id: str) -> dict:
    """
    Helper to check if any session already has this video's transcript cached,
    to avoid fetching transcripts repeatedly.
    """
    sessions = load_all_sessions()
    for sess in sessions:
        if sess.get("video_id") == video_id and sess.get("transcript"):
            return {
                "video_id": sess["video_id"],
                "title": sess.get("title") or f"Video {video_id}",
                "transcript": sess["transcript"],
                "num_chunks": sess["num_chunks"]
            }
    return None


def update_session(session_id: str, updates: dict) -> bool:
    """
    Updates specific fields in a session.
    """
    if not session_id:
        return False
    sessions = load_all_sessions()
    updated = False
    for sess in sessions:
        if sess.get("session_id") == session_id:
            for k, v in updates.items():
                sess[k] = v
            updated = True
            break
            
    if updated:
        return save_all_sessions(sessions)
    return False


def list_recent_sessions(limit: int = 10) -> list:
    """
    Retrieves the most recent sessions.
    """
    sessions = load_all_sessions()
    # Sort by created_at descending
    try:
        sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    except Exception:
        pass
    return sessions[:limit]
