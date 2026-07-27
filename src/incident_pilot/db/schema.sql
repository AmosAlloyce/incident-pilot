CREATE TABLE IF NOT EXISTS incidents (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT    NOT NULL,
    component        TEXT    NOT NULL,   -- e.g. worker-app, geofence-service, facility-api, nfc-service
    severity         TEXT    NOT NULL,   -- P1, P2, P3, P4
    status           TEXT    NOT NULL,   -- open, resolved, monitoring
    created_at       TEXT    NOT NULL,   -- ISO-8601
    resolution_notes TEXT
);

CREATE TABLE IF NOT EXISTS log_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL REFERENCES incidents(id),
    timestamp   TEXT    NOT NULL,
    level       TEXT    NOT NULL,   -- INFO, WARN, ERROR
    service     TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    trace       TEXT                -- stack trace fragment, nullable
);
