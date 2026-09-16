import sqlite3
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from .config import DB_PATH

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_name TEXT NOT NULL,
                pet_name TEXT NOT NULL,
                pet_species TEXT NOT NULL DEFAULT 'Autre',
                years_known TEXT DEFAULT '',
                message TEXT NOT NULL,
                media_path TEXT,
                media_type TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                moderated_at TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
        """)
    conn.close()

def create_message(
    author_name: str,
    pet_name: str,
    pet_species: str,
    years_known: str,
    message: str,
    media_path: Optional[str] = None,
    media_type: Optional[str] = None,
    status: str = "pending"
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    with conn:
        cursor = conn.execute("""
            INSERT INTO messages (
                author_name, pet_name, pet_species, years_known,
                message, media_path, media_type, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            author_name.strip(),
            pet_name.strip(),
            pet_species.strip(),
            years_known.strip(),
            message.strip(),
            media_path,
            media_type,
            status,
            now
        ))
        msg_id = cursor.lastrowid
    conn.close()
    return msg_id

def get_approved_messages(species_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db()
    query = "SELECT * FROM messages WHERE status = 'approved'"
    params = []
    if species_filter and species_filter.lower() != "tous":
        query += " AND LOWER(pet_species) = LOWER(?)"
        params.append(species_filter)
    query += " ORDER BY created_at DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_messages_for_admin(status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db()
    query = "SELECT * FROM messages"
    params = []
    if status and status.lower() != "tous":
        query += " WHERE status = ?"
        params.append(status.lower())
    query += " ORDER BY created_at DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    row = conn.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_message_status(message_id: int, new_status: str) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    with conn:
        cursor = conn.execute("""
            UPDATE messages 
            SET status = ?, moderated_at = ?
            WHERE id = ?
        """, (new_status, now, message_id))
        updated = cursor.rowcount > 0
    conn.close()
    return updated

def update_message_content(
    message_id: int,
    author_name: str,
    pet_name: str,
    pet_species: str,
    years_known: str,
    message: str
) -> bool:
    conn = get_db()
    with conn:
        cursor = conn.execute("""
            UPDATE messages
            SET author_name = ?, pet_name = ?, pet_species = ?, years_known = ?, message = ?
            WHERE id = ?
        """, (author_name.strip(), pet_name.strip(), pet_species.strip(), years_known.strip(), message.strip(), message_id))
        updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_message(message_id: int) -> Optional[str]:
    """Deletes a message from the DB and returns the media_path if any (for file cleanup)."""
    conn = get_db()
    row = conn.execute("SELECT media_path FROM messages WHERE id = ?", (message_id,)).fetchone()
    if not row:
        conn.close()
        return None
    media_path = row["media_path"]
    with conn:
        conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    conn.close()
    return media_path

def get_stats() -> Dict[str, int]:
    conn = get_db()
    rows = conn.execute("""
        SELECT status, COUNT(*) as count 
        FROM messages 
        GROUP BY status
    """).fetchall()
    conn.close()
    stats = {"pending": 0, "approved": 0, "rejected": 0, "total": 0}
    for r in rows:
        st = r["status"]
        if st in stats:
            stats[st] = r["count"]
        stats["total"] += r["count"]
    return stats
