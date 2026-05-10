import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import DATA_DIR, DB_PATH, SETTINGS_PATH, DEFAULT_SETTINGS


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
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender      TEXT NOT NULL,
                    content     TEXT NOT NULL,
                    date        TEXT NOT NULL,
                    received_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
                CREATE INDEX IF NOT EXISTS idx_msg_sender ON messages(sender);
                CREATE INDEX IF NOT EXISTS idx_msg_date   ON messages(date);

                CREATE TABLE IF NOT EXISTS reports (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    content      TEXT NOT NULL,
                    generated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)

    # ------------------------------------------------------------------ messages

    def add_message(self, sender: str, content: str, date: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO messages (sender, content, date) VALUES (?, ?, ?)",
                (sender, content, date),
            )
            return cur.lastrowid

    def search_messages(
        self,
        sender: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        keywords: Optional[str] = None,
    ) -> list[dict]:
        query = "SELECT * FROM messages WHERE 1=1"
        params: list = []
        if sender:
            query += " AND LOWER(sender) LIKE LOWER(?)"
            params.append(f"%{sender}%")
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if keywords:
            query += " AND LOWER(content) LIKE LOWER(?)"
            params.append(f"%{keywords}%")
        query += " ORDER BY id"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_raw_messages(
        self,
        message_ids: Optional[list[int]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        if message_ids:
            placeholders = ",".join("?" * len(message_ids))
            query = f"SELECT * FROM messages WHERE id IN ({placeholders}) ORDER BY id"
            params = message_ids
        else:
            query = "SELECT * FROM messages WHERE 1=1"
            params = []
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            query += " ORDER BY id"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
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
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        with self._connect() as conn:
            return conn.execute(query, params).fetchone()[0]

    def get_all_messages(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ reports

    def add_report(self, content: str) -> int:
        with self._connect() as conn:
            cur = conn.execute("INSERT INTO reports (content) VALUES (?)", (content,))
            return cur.lastrowid

    def get_latest_report(self) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def get_all_reports(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


# ------------------------------------------------------------------ settings

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH) as f:
                stored = json.load(f)
            merged = _deep_merge(DEFAULT_SETTINGS, stored)
            return merged
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
