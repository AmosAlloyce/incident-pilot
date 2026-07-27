"""
Unit tests for db/queries.py.
Uses a temporary in-memory SQLite DB so no file I/O and no dependency on a real seed.
"""

import os
import sqlite3
import pytest
from pathlib import Path

# Point queries module at a temp in-memory DB before importing
os.environ["DB_PATH"] = ":memory:"

from incident_pilot.db import queries  # noqa: E402  (import after env set)
from incident_pilot.db.seed import INCIDENTS, LOG_EVENTS, SCHEMA_PATH


@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch, tmp_path):
    """
    Create a fresh SQLite DB in a temp file for each test, monkeypatch DB_PATH,
    and seed it with the real seed data so queries have something to work with.
    """
    db_file = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_file)
    # Patch the module-level variable used by _connect()
    monkeypatch.setattr(queries, "DB_PATH", db_file)

    conn = sqlite3.connect(db_file)
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)
    conn.executemany(
        "INSERT INTO incidents (id, title, component, severity, status, created_at, resolution_notes) "
        "VALUES (?,?,?,?,?,?,?)",
        INCIDENTS,
    )
    conn.executemany(
        "INSERT INTO log_events (incident_id, timestamp, level, service, message, trace) "
        "VALUES (?,?,?,?,?,?)",
        LOG_EVENTS,
    )
    conn.commit()
    conn.close()
    yield


class TestFindSimilarIncidents:
    def test_returns_results_for_known_keyword(self):
        results = queries.find_similar_incidents(["clock-in"])
        assert len(results) > 0, "Expected at least one incident matching 'clock-in'"

    def test_returns_results_for_multiple_keywords(self):
        results = queries.find_similar_incidents(["geofence", "timeout"])
        assert len(results) > 0, "Expected incidents matching geofence/timeout keywords"

    def test_returns_empty_list_for_unknown_keyword(self):
        results = queries.find_similar_incidents(["xyzzy_nonexistent_term_42"])
        assert results == [], "Expected empty list for a keyword that matches nothing"

    def test_returns_empty_list_for_empty_keywords(self):
        results = queries.find_similar_incidents([])
        assert results == [], "Expected empty list when no keywords provided"

    def test_result_has_expected_fields(self):
        results = queries.find_similar_incidents(["worker-app"])
        assert results, "Expected at least one result"
        row = results[0]
        for field in ("id", "title", "component", "severity", "status", "created_at"):
            assert field in row, f"Missing field: {field}"

    def test_limit_is_respected(self):
        results = queries.find_similar_incidents(["facility"], limit=2)
        assert len(results) <= 2, "Result count exceeded the requested limit"


class TestGetLogEventsForIncident:
    def test_returns_log_events_for_seeded_incident(self):
        events = queries.get_log_events_for_incident(1)
        assert len(events) > 0, "Expected log events for incident 1"

    def test_returns_empty_list_for_nonexistent_incident(self):
        events = queries.get_log_events_for_incident(9999)
        assert events == [], "Expected empty list for an incident that does not exist"

    def test_events_ordered_by_timestamp(self):
        events = queries.get_log_events_for_incident(6)
        timestamps = [e["timestamp"] for e in events]
        assert timestamps == sorted(timestamps), "Log events should be ordered by timestamp ASC"

    def test_event_has_expected_fields(self):
        events = queries.get_log_events_for_incident(1)
        assert events, "Expected at least one event"
        for field in ("id", "incident_id", "timestamp", "level", "service", "message"):
            assert field in events[0], f"Missing field: {field}"
