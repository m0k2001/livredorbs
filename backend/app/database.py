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
                moderated_at TEXT,
                include_in_print INTEGER NOT NULL DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
        """)
        # Safe migration for existing DB
        try:
            conn.execute("ALTER TABLE messages ADD COLUMN include_in_print INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass
    conn.close()

def create_message(
    author_name: str,
    pet_name: str,
    pet_species: str,
    years_known: str,
    message: str,
    media_path: Optional[str] = None,
    media_type: Optional[str] = None,
    status: str = "pending",
    include_in_print: int = 1
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    with conn:
        cursor = conn.execute("""
            INSERT INTO messages (
                author_name, pet_name, pet_species, years_known,
                message, media_path, media_type, status, created_at, include_in_print
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            author_name.strip(),
            pet_name.strip(),
            pet_species.strip(),
            years_known.strip(),
            message.strip(),
            media_path,
            media_type,
            status,
            now,
            1 if include_in_print else 0
        ))
        msg_id = cursor.lastrowid
    conn.close()
    return msg_id

def get_approved_messages(species_filter: Optional[str] = None, for_print: bool = False) -> List[Dict[str, Any]]:
    conn = get_db()
    query = "SELECT * FROM messages WHERE status = 'approved'"
    params = []
    if for_print:
        query += " AND (include_in_print = 1 OR include_in_print IS NULL)"
    if species_filter and species_filter.lower() != "tous":
        query += " AND LOWER(pet_species) = LOWER(?)"
        params.append(species_filter)
    query += " ORDER BY created_at DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_messages_for_admin(status: Optional[str] = None, print_only: bool = False) -> List[Dict[str, Any]]:
    conn = get_db()
    query = "SELECT * FROM messages"
    params = []
    conditions = []
    if status and status.lower() != "tous":
        conditions.append("status = ?")
        params.append(status.lower())
    if print_only:
        conditions.append("(include_in_print = 1 OR include_in_print IS NULL)")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
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

def update_message_print_selection(message_id: int, include_in_print: bool) -> bool:
    conn = get_db()
    with conn:
        cursor = conn.execute("""
            UPDATE messages 
            SET include_in_print = ?
            WHERE id = ?
        """, (1 if include_in_print else 0, message_id))
        updated = cursor.rowcount > 0
    conn.close()
    return updated

def bulk_update_print_selection(include_in_print: bool, status: Optional[str] = None) -> int:
    conn = get_db()
    val = 1 if include_in_print else 0
    with conn:
        if status and status.lower() != "tous":
            cursor = conn.execute("UPDATE messages SET include_in_print = ? WHERE status = ?", (val, status.lower()))
        else:
            cursor = conn.execute("UPDATE messages SET include_in_print = ?", (val,))
        count = cursor.rowcount
    conn.close()
    return count

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
    print_row = conn.execute("""
        SELECT COUNT(*) as count 
        FROM messages 
        WHERE status = 'approved' AND (include_in_print = 1 OR include_in_print IS NULL)
    """).fetchone()
    conn.close()
    stats = {"pending": 0, "approved": 0, "rejected": 0, "total": 0, "print_selected": 0}
    for r in rows:
        st = r["status"]
        if st in stats:
            stats[st] = r["count"]
        stats["total"] += r["count"]
    if print_row:
        stats["print_selected"] = print_row["count"]
    return stats
