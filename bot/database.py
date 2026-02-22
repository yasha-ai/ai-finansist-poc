"""SQLite база данных для хранения расписания новостей."""

import sqlite3
from datetime import datetime
from pathlib import Path

from bot.models import NewsEvent

DB_PATH = Path("data/events.db")


def _connect() -> sqlite3.Connection:
    """Получить соединение с БД."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            description TEXT DEFAULT '',
            active INTEGER DEFAULT 1
        )
        """
    )
    conn.commit()
    return conn


def add_event(event_date: datetime, symbol: str, description: str = "") -> int:
    """Добавить новость в расписание. Возвращает id."""
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO events (event_date, symbol, description) VALUES (?, ?, ?)",
        (event_date.isoformat(), symbol.upper(), description),
    )
    conn.commit()
    event_id: int = cur.lastrowid  # type: ignore[assignment]
    conn.close()
    return event_id


def list_events(only_active: bool = True) -> list[NewsEvent]:
    """Получить список новостей."""
    conn = _connect()
    query = "SELECT * FROM events"
    if only_active:
        query += " WHERE active = 1"
    query += " ORDER BY event_date ASC"
    rows = conn.execute(query).fetchall()
    conn.close()
    return [
        NewsEvent(
            id=r["id"],
            event_date=datetime.fromisoformat(r["event_date"]),
            symbol=r["symbol"],
            description=r["description"],
            active=bool(r["active"]),
        )
        for r in rows
    ]


def delete_event(event_id: int) -> bool:
    """Удалить новость по id. Возвращает True если удалена."""
    conn = _connect()
    cur = conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def deactivate_event(event_id: int) -> None:
    """Деактивировать новость (после отработки)."""
    conn = _connect()
    conn.execute("UPDATE events SET active = 0 WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
