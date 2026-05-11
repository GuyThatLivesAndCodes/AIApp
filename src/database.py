import re
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from config import DATA_DIR, DB_PATH, SETTINGS_PATH, DEFAULT_SETTINGS


# ------------------------------------------------------------------ date parsing

_DATE_FORMATS = [
    "%m/%d/%Y %I:%M %p",   # 05/09/2026 05:19 PM
    "%m/%d/%Y %I:%M%p",    # 05/09/2026 05:19PM  (no space)
    "%m/%d/%Y %H:%M:%S",   # 05/09/2026 17:19:00
    "%m/%d/%Y %H:%M",      # 05/09/2026 17:19
    "%m/%d/%Y",            # 05/09/2026
    "%Y-%m-%dT%H:%M:%S",   # ISO
    "%Y-%m-%d %H:%M:%S",   # ISO with space
    "%Y-%m-%d",            # ISO date only
]


def parse_date_to_iso(date_str: str) -> Optional[str]:
    """Parse various human date formats into ISO 8601 for reliable SQLite sorting."""
    if not date_str:
        return None
    # Insert a space between digits and AM/PM if missing: "5:19PM" → "5:19 PM"
    s = re.sub(r"(\d)(AM|PM)", r"\1 \2", date_str.strip(), flags=re.IGNORECASE).upper()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).isoformat()
        except ValueError:
            continue
    return None


def _iso_start_of_day(date_str: str) -> Optional[str]:
    """Return ISO start-of-day (00:00:00) for a given date string."""
    iso = parse_date_to_iso(date_str)
    if iso:
        return iso[:10] + "T00:00:00"
    return None


def _iso_end_of_day(date_str: str) -> Optional[str]:
    """Return ISO end-of-day (23:59:59) for a given date string."""
    iso = parse_date_to_iso(date_str)
    if iso:
        return iso[:10] + "T23:59:59"
    return None


# ------------------------------------------------------------------ database

class Database:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS messages (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender       TEXT NOT NULL,
                    content      TEXT NOT NULL,
                    date         TEXT NOT NULL,
                    date_ts      TEXT,
                    conversation TEXT NOT NULL DEFAULT '',
                    received_at  TEXT NOT NULL DEFAULT (datetime('now'))
                );
                CREATE INDEX IF NOT EXISTS idx_msg_sender ON messages(sender);

                CREATE TABLE IF NOT EXISTS reports (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    content      TEXT NOT NULL,
                    generated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS chats (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    title      TEXT NOT NULL,
                    transcript TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)
            # Migrations: run each ALTER TABLE; ignore if column already present
            for migration in [
                "ALTER TABLE messages ADD COLUMN date_ts TEXT",
                "ALTER TABLE messages ADD COLUMN conversation TEXT NOT NULL DEFAULT ''",
                "ALTER TABLE reports ADD COLUMN content_b TEXT NOT NULL DEFAULT ''",
            ]:
                try:
                    conn.execute(migration)
                except sqlite3.OperationalError:
                    pass
            conn.execute("CREATE INDEX IF NOT EXISTS idx_msg_date_ts ON messages(date_ts)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_msg_conversation ON messages(conversation)")

        self._backfill_date_ts()

    def _backfill_date_ts(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, date FROM messages WHERE date_ts IS NULL"
            ).fetchall()
            for row in rows:
                iso = parse_date_to_iso(row["date"])
                if iso:
                    conn.execute(
                        "UPDATE messages SET date_ts = ? WHERE id = ?",
                        (iso, row["id"]),
                    )

    # ------------------------------------------------------------------ messages

    def message_exists(self, sender: str, content: str, date: str, conversation: str) -> bool:
        """Return True if an identical (sender, content, date, conversation) row already exists."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM messages WHERE sender=? AND content=? AND date=? AND conversation=? LIMIT 1",
                (sender, content, date, conversation),
            ).fetchone()
        return row is not None

    def add_message(self, sender: str, content: str, date: str, conversation: str = "") -> int:
        date_ts = parse_date_to_iso(date)
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO messages (sender, content, date, date_ts, conversation) VALUES (?, ?, ?, ?, ?)",
                (sender, content, date, date_ts, conversation),
            )
            return cur.lastrowid

    def _date_clauses(self, start_date: Optional[str], end_date: Optional[str]) -> tuple[str, list]:
        """Build ISO-safe date range SQL clauses. Falls back to LIKE if parsing fails."""
        clauses = ""
        params: list = []

        if start_date:
            iso = _iso_start_of_day(start_date)
            if iso:
                clauses += " AND (date_ts >= ? OR (date_ts IS NULL AND date LIKE ?))"
                params.extend([iso, f"{start_date.split()[0]}%"])
            else:
                clauses += " AND date LIKE ?"
                params.append(f"{start_date}%")

        if end_date:
            iso = _iso_end_of_day(end_date)
            if iso:
                clauses += " AND (date_ts <= ? OR (date_ts IS NULL AND date LIKE ?))"
                params.extend([iso, f"{end_date.split()[0]}%"])
            else:
                clauses += " AND date LIKE ?"
                params.append(f"{end_date}%")

        return clauses, params

    def search_messages(
        self,
        sender: Optional[str] = None,
        conversation: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        keywords: Optional[str] = None,
    ) -> list[dict]:
        query = "SELECT * FROM messages WHERE 1=1"
        params: list = []
        if sender:
            query += " AND LOWER(sender) LIKE LOWER(?)"
            params.append(f"%{sender}%")
        if conversation:
            query += " AND LOWER(conversation) LIKE LOWER(?)"
            params.append(f"%{conversation}%")
        date_clause, date_params = self._date_clauses(start_date, end_date)
        query += date_clause
        params.extend(date_params)
        if keywords:
            query += " AND LOWER(content) LIKE LOWER(?)"
            params.append(f"%{keywords}%")
        query += " ORDER BY COALESCE(date_ts, date)"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_conversations(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT conversation FROM messages WHERE conversation != '' ORDER BY conversation"
            ).fetchall()
        return [r["conversation"] for r in rows]

    def get_raw_messages(
        self,
        message_ids: Optional[list[int]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        if message_ids:
            placeholders = ",".join("?" * len(message_ids))
            query = f"SELECT * FROM messages WHERE id IN ({placeholders}) ORDER BY COALESCE(date_ts, date)"
            params = list(message_ids)
        else:
            query = "SELECT * FROM messages WHERE 1=1"
            params = []
            date_clause, date_params = self._date_clauses(start_date, end_date)
            query += date_clause
            params.extend(date_params)
            query += " ORDER BY COALESCE(date_ts, date)"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_recent_messages(self, n: int = 15) -> list[dict]:
        """Return the n most recent messages by date_ts, oldest-first for readability."""
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT * FROM (
                       SELECT * FROM messages ORDER BY COALESCE(date_ts, received_at) DESC LIMIT ?
                   ) ORDER BY COALESCE(date_ts, received_at) ASC""",
                (n,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_senders(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT sender FROM messages ORDER BY sender").fetchall()
        return [r["sender"] for r in rows]

    def get_message_count(
        self,
        sender: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> int:
        query = "SELECT COUNT(*) FROM messages WHERE 1=1"
        params: list = []
        if sender:
            query += " AND LOWER(sender) LIKE LOWER(?)"
            params.append(f"%{sender}%")
        date_clause, date_params = self._date_clauses(start_date, end_date)
        query += date_clause
        params.extend(date_params)
        with self._connect() as conn:
            return conn.execute(query, params).fetchone()[0]

    def delete_messages(self, ids: list[int]) -> int:
        if not ids:
            return 0
        placeholders = ",".join("?" * len(ids))
        with self._connect() as conn:
            cur = conn.execute(f"DELETE FROM messages WHERE id IN ({placeholders})", ids)
            return cur.rowcount

    def get_all_messages(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM messages ORDER BY COALESCE(date_ts, received_at) DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ reports

    def add_report(self, content_a: str, content_b: str = "") -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO reports (content, content_b) VALUES (?, ?)",
                (content_a, content_b),
            )
            return cur.lastrowid

    def get_latest_report(self) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def get_all_reports(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ chats

    def save_chat(self, title: str, transcript: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO chats (title, transcript) VALUES (?, ?)",
                (title, transcript),
            )
            return cur.lastrowid

    def get_all_chats(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM chats ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    def get_chat(self, chat_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
        return dict(row) if row else None

    def delete_chat(self, chat_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))


# ------------------------------------------------------------------ settings

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH) as f:
                stored = json.load(f)
            return _deep_merge(DEFAULT_SETTINGS, stored)
        except Exception:
            pass
    return _deep_merge({}, DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result
