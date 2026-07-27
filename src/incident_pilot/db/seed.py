"""
Seed the SQLite incidents database with realistic Clipboard-style fake data.
Run via: make seed   (or PYTHONPATH=src python -m incident_pilot.db.seed)
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "incident_pilot.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


INCIDENTS = [
    # worker-app / clock-in issues
    (1,  "Worker app crashes on clock-in at facility 4821", "worker-app", "P2", "resolved",
     "2024-11-03T08:14:00Z",
     "NullPointerException in ShiftSessionManager when facility geofence radius was 0. "
     "Fixed by adding null-guard and re-seeding facility config."),
    (2,  "Clock-in button unresponsive for workers on Android 14", "worker-app", "P3", "resolved",
     "2024-11-10T11:30:00Z",
     "Android 14 changed background location permission flow. App was silently denied. "
     "Updated manifest and released patch 3.4.2."),
    (3,  "Workers double-clocked-in after app backgrounded during shift start", "worker-app", "P2", "resolved",
     "2024-12-01T07:55:00Z",
     "Race condition between optimistic UI update and server acknowledgement. "
     "Added idempotency key to clock-in POST request."),
    (4,  "Clock-out not registering — shift remains open for 6+ hours", "worker-app", "P2", "resolved",
     "2024-12-15T14:20:00Z",
     "WebSocket disconnect on poor connectivity caused clock-out event to drop. "
     "Implemented retry queue with exponential back-off."),
    (5,  "Worker app showing incorrect pay rate on shift confirmation screen", "worker-app", "P3", "resolved",
     "2025-01-08T09:05:00Z",
     "Stale rate cache not invalidated after facility updated contract. "
     "Cache TTL reduced to 5 min and manual invalidation endpoint added."),

    # geofence-service
    (6,  "Geofence check timing out for 23% of clock-in attempts at hospital campus", "geofence-service", "P1", "resolved",
     "2024-10-22T06:00:00Z",
     "Google Maps Geocoding API rate limit hit during morning rush. "
     "Switched to cached polygon lookup; external API now only called on cache miss."),
    (7,  "Geofence boundary incorrect after facility address update", "geofence-service", "P3", "resolved",
     "2024-11-18T13:45:00Z",
     "Address update in admin portal did not trigger geofence recalculation job. "
     "Added webhook listener on facility address change event."),
    (8,  "Workers outside geofence allowed to clock in — enforcement disabled", "geofence-service", "P1", "resolved",
     "2024-12-20T05:30:00Z",
     "Feature flag geofence_enforcement was flipped to false during unrelated deploy. "
     "Restored flag, added change-guard to prevent flag toggling without approval."),
    (9,  "Geofence radius set to 0 meters for 14 facilities after data migration", "geofence-service", "P2", "resolved",
     "2025-01-14T10:10:00Z",
     "Migration script cast NULL radius to 0 instead of default 200m. "
     "Backfill script run; migration fixed."),

    # facility-api
    (10, "Facility quiz returning 500 error on final submission", "facility-api", "P2", "resolved",
     "2024-11-05T16:00:00Z",
     "Unhandled exception when quiz answer payload contained null for optional field. "
     "Added input validation and default fallback."),
    (11, "Facility quiz scores not persisted — workers forced to retake", "facility-api", "P3", "resolved",
     "2024-11-25T12:30:00Z",
     "DB write transaction was rolled back silently due to deadlock on quiz_results table. "
     "Added retry logic with row-level locking."),
    (12, "Facility admin unable to update quiz questions — 403 returned", "facility-api", "P3", "resolved",
     "2024-12-10T09:15:00Z",
     "Role-permission mapping for FACILITY_ADMIN missing quiz_write scope after auth refactor. "
     "Scope re-added and regression test added."),
    (13, "Facility API latency spike — p99 > 8 s for 40 minutes", "facility-api", "P1", "resolved",
     "2025-01-20T02:00:00Z",
     "Missing index on facility_id in bookings table caused full-table scan under load. "
     "Index added; query time returned to <200 ms."),

    # nfc-service
    (14, "NFC tag scan not registering at 8 facilities after firmware update", "nfc-service", "P2", "resolved",
     "2024-10-30T07:00:00Z",
     "Firmware v2.1 changed NFC tag UID format from hex to decimal. "
     "Parser updated to handle both formats."),
    (15, "NFC clock-in events arriving out of order — negative shift durations recorded", "nfc-service", "P3", "resolved",
     "2024-12-05T11:00:00Z",
     "Event timestamps were device-local; devices had clock drift up to 90 s. "
     "Switched to server-side timestamping on event ingestion."),
    (16, "NFC reader offline for 3 hours — workers unable to clock in", "nfc-service", "P1", "resolved",
     "2025-01-02T06:45:00Z",
     "NFC reader lost network connectivity; no fallback to app-based clock-in was presented. "
     "Added offline fallback prompt in worker app and alerting for reader heartbeat loss."),
]

LOG_EVENTS = [
    # Incident 1 — worker-app crash on clock-in
    (1, "2024-11-03T08:13:45Z", "INFO",  "worker-app",      "User 9912 initiated clock-in at facility 4821", None),
    (1, "2024-11-03T08:13:46Z", "INFO",  "worker-app",      "Fetching geofence config for facility 4821", None),
    (1, "2024-11-03T08:13:47Z", "WARN",  "geofence-service","Facility 4821 geofence radius is 0 — defaulting to permissive mode", None),
    (1, "2024-11-03T08:13:47Z", "ERROR", "worker-app",
     "NullPointerException in ShiftSessionManager.startSession()",
     "java.lang.NullPointerException\n  at ShiftSessionManager.startSession(ShiftSessionManager.java:142)\n  at ClockInController.handleClockIn(ClockInController.java:88)"),
    (1, "2024-11-03T08:13:47Z", "ERROR", "worker-app",      "Clock-in failed for user 9912 — session not created", None),

    # Incident 6 — geofence timeout
    (6, "2024-10-22T05:58:00Z", "INFO",  "geofence-service","Clock-in request received for facility 1103, user 7741", None),
    (6, "2024-10-22T05:58:01Z", "INFO",  "geofence-service","Calling Google Maps Geocoding API for lat/lng resolution", None),
    (6, "2024-10-22T05:58:06Z", "WARN",  "geofence-service","Geocoding API response time 5001 ms — threshold 3000 ms", None),
    (6, "2024-10-22T05:58:06Z", "ERROR", "geofence-service","Geocoding API rate limit exceeded: 429 Too Many Requests", None),
    (6, "2024-10-22T05:58:06Z", "ERROR", "geofence-service",
     "GeofenceCheckException: upstream timeout after 3 retries",
     "com.clipboard.geofence.GeofenceCheckException: upstream timeout\n  at GeofenceService.checkBoundary(GeofenceService.java:204)"),
    (6, "2024-10-22T05:58:06Z", "ERROR", "worker-app",      "Clock-in rejected — geofence validation failed for user 7741", None),

    # Incident 10 — facility quiz 500
    (10, "2024-11-05T15:59:30Z", "INFO",  "facility-api",   "Quiz submission received from worker 3344 for facility 902", None),
    (10, "2024-11-05T15:59:30Z", "INFO",  "facility-api",   "Validating quiz payload — 12 answers provided", None),
    (10, "2024-11-05T15:59:30Z", "WARN",  "facility-api",   "Optional field 'comments' is null in submission body", None),
    (10, "2024-11-05T15:59:30Z", "ERROR", "facility-api",
     "Unhandled NullPointerException in QuizSubmissionHandler.persist()",
     "java.lang.NullPointerException\n  at QuizSubmissionHandler.persist(QuizSubmissionHandler.java:77)\n  at FacilityApiController.submitQuiz(FacilityApiController.java:201)"),
    (10, "2024-11-05T15:59:30Z", "ERROR", "facility-api",   "HTTP 500 returned to client for quiz submission — worker 3344", None),

    # Incident 14 — NFC tag format
    (14, "2024-10-30T06:58:00Z", "INFO",  "nfc-service",    "NFC scan event received from reader R-009 at facility 2210", None),
    (14, "2024-10-30T06:58:00Z", "WARN",  "nfc-service",    "Tag UID format unrecognised — expected hex, got decimal '0481726533640280'", None),
    (14, "2024-10-30T06:58:00Z", "ERROR", "nfc-service",
     "TagParseException: UID format mismatch after firmware v2.1 upgrade",
     "com.clipboard.nfc.TagParseException: UID format mismatch\n  at NfcTagParser.parseUid(NfcTagParser.java:55)"),
    (14, "2024-10-30T06:58:01Z", "ERROR", "nfc-service",    "Clock-in event dropped — could not resolve worker from tag UID", None),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def seed() -> None:
    print(f"Seeding database at: {DB_PATH}")
    conn = get_connection()
    cur = conn.cursor()

    # Drop and recreate tables
    schema = SCHEMA_PATH.read_text()
    cur.executescript("DROP TABLE IF EXISTS log_events; DROP TABLE IF EXISTS incidents;")
    cur.executescript(schema)

    cur.executemany(
        "INSERT INTO incidents (id, title, component, severity, status, created_at, resolution_notes) "
        "VALUES (?,?,?,?,?,?,?)",
        INCIDENTS,
    )

    cur.executemany(
        "INSERT INTO log_events (incident_id, timestamp, level, service, message, trace) "
        "VALUES (?,?,?,?,?,?)",
        LOG_EVENTS,
    )

    conn.commit()
    conn.close()
    print(f"  {len(INCIDENTS)} incidents inserted.")
    print(f"  {len(LOG_EVENTS)} log events inserted.")
    print("Done.")


if __name__ == "__main__":
    seed()
