"""
SQL query helpers used by SQLAgent.
All functions return plain dicts so they are easy to serialise and pass between agents.
"""

import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = os.getenv("DB_PATH", "incident_pilot.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def find_similar_incidents(keywords: list[str], limit: int = 5) -> list[dict[str, Any]]:
    """
    Full-text keyword search across incident title, component, and resolution_notes.
    Returns up to `limit` resolved incidents ordered by most recent first.

    Example
    -------
    >>> find_similar_incidents(["clock-in", "crash"])
    [{"id": 1, "title": "Worker app crashes on clock-in ...", ...}, ...]
    """
    if not keywords:
        return []

    conditions = " OR ".join(
        ["title LIKE ? OR component LIKE ? OR resolution_notes LIKE ?"] * len(keywords)
    )
    params: list[str] = []
    for kw in keywords:
        pattern = f"%{kw}%"
        params.extend([pattern, pattern, pattern])

    sql = f"""
        SELECT id, title, component, severity, status, created_at, resolution_notes
        FROM   incidents
        WHERE  ({conditions})
        ORDER  BY created_at DESC
        LIMIT  {limit}
    """
    conn = _connect()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_log_events_for_incident(incident_id: int) -> list[dict[str, Any]]:
    """
    Fetch all log events associated with a specific incident, ordered by timestamp.

    Example
    -------
    >>> get_log_events_for_incident(1)
    [{"id": 1, "incident_id": 1, "timestamp": "...", "level": "INFO", ...}, ...]
    """
    sql = """
        SELECT id, incident_id, timestamp, level, service, message, trace
        FROM   log_events
        WHERE  incident_id = ?
        ORDER  BY timestamp ASC
    """
    conn = _connect()
    try:
        rows = conn.execute(sql, [incident_id]).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
