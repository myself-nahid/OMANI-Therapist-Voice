import sqlite3
import datetime

DATABASE_NAME = "backend/conversation.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Create table to store conversation turns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_text TEXT,
            detected_emotion TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_conversation(session_id: str, user_text: str, emotion: str, ai_response: str):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversation_history (session_id, user_text, detected_emotion, ai_response)
        VALUES (?, ?, ?, ?)
    """, (session_id, user_text, emotion, ai_response))
    conn.commit()
    conn.close()

def get_conversation_history(session_id: str, limit: int = 10):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_text, ai_response FROM conversation_history
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (session_id, limit))
    history = cursor.fetchall()
    conn.close()
    # Format for LLM: return a list of {"role": "user/assistant", "content": "..."}
    formatted_history = []
    for user_msg, ai_msg in reversed(history): # reverse to get chronological order
        if user_msg:
            formatted_history.append({"role": "user", "content": user_msg})
        if ai_msg:
            formatted_history.append({"role": "assistant", "content": ai_msg})
    return formatted_history