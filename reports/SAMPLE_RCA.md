# Incident Investigation Report

**Generated:** 2026-07-27 01:15:07 UTC  
**Tool:** incident-pilot v0.1.0  
**Escalation:** Escalate to Engineering

---

## Original Ticket

> Worker app crashes when clocking in at facility 4821

---

## Triage

| Field     | Value |
|-----------|-------|
| Severity  | P2 |
| Component | `worker-app` |
| Category  | clock-in |
| Summary   | Worker app crashes when attempting to clock in at facility 4821 |

---

## SQL Investigation

**Keywords searched:** `worker-app, clock-in, clock in, worker, crashes, attempting, clock, facility`  
**Incidents matched:** 5

| ID | Title | Component | Severity | Status |
|----|-------|-----------|----------|--------|
| 13 | Facility API latency spike — p99 > 8 s for 40 minutes | `facility-api` | P1 | resolved |
| 5 | Worker app showing incorrect pay rate on shift confirmation screen | `worker-app` | P3 | resolved |
| 16 | NFC reader offline for 3 hours — workers unable to clock in | `nfc-service` | P1 | resolved |
| 8 | Workers outside geofence allowed to clock in — enforcement disabled | `geofence-service` | P1 | resolved |
| 4 | Clock-out not registering — shift remains open for 6+ hours | `worker-app` | P2 | resolved |

---

## Log Analysis

**Log file analysed:** `clock_in_crash.log`

**Error Signatures**

1. **NullPointerException in ShiftSessionManager.startSession()**
   - Timestamp: 2024-11-03T08:13:47Z
   - Service: worker-app
   - Error Message: NullPointerException in ShiftSessionManager.startSession()
   - Stack Trace Fragment:
     ```
     java.lang.NullPointerException
       at ShiftSessionManager.startSession(ShiftSessionManager.java:142)
       at ClockInController.handleClockIn(ClockInController.java:88)
     ```
   - Timestamp: 2024-11-03T08:14:10Z
   - Service: worker-app
   - Error Message: NullPointerException in ShiftSessionManager.startSession()
   - Stack Trace Fragment:
     ```
     java.lang.NullPointerException
       at ShiftSessionManager.startSession(ShiftSessionManager.java:142)
       at ClockInController.handleClockIn(ClockInController.java:88)
     ```

2. **Clock-in FAILED — session not created for shift SH-88221**
   - Timestamp: 2024-11-03T08:13:47Z
   - Service: worker-app
   - Error Message: Clock-in FAILED — session not created for shift SH-88221
   - No stack trace fragment available

**Affected Services**

1. worker-app
2. geofence-service
3. support-events

**Timeline**

1. 2024-11-03T08:13:40Z: Worker opened shift search screen
2. 2024-11-03T08:13:42Z: Worker tapped clock-in button for shift SH-88221
3. 2024-11-03T08:13:43Z: Initiating clock-in flow — fetching facility config
4. 2024-11-03T08:13:45Z: Geofence radius is 0 for facility 4821 — enforcement skipped, proceeding in permissive mode
5. 2024-11-03T08:13:47Z: NullPointerException in ShiftSessionManager.startSession()
6. 2024-11-03T08:13:47Z: Clock-in FAILED — session not created for shift SH-88221
7. 2024-11-03T08:13:48Z: Displaying generic error dialog to user — 'Something went wrong, please try again'
8. 2024-11-03T08:14:10Z: User retried clock-in — same failure reproduced

**Key Findings**

1. **NullPointerException in ShiftSessionManager.startSession()**: The application crashes with a NullPointerException in the ShiftSessionManager.startSession() method, which suggests a null value is being passed to the method. This error is reproducible.
2. **Geofence radius is 0 for facility 4821**: The geofence radius for facility 4821 is 0, which may indicate a misconfiguration or an issue with the geofencing service.
3. **Clock-in failure with generic error message**: The application displays a generic error message to the user after the clock-in failure, which may not provide sufficient information for the user to diagnose the issue.
4. **Support ticket auto-created**: A support ticket (TSE-3301) is auto-created due to the clock-in failure, which will help track the issue further.

---

## Root Cause Analysis

## Ticket
Worker app crashes when clocking in at facility 4821

## Triage Summary
The worker app crashes with a P2 severity, affecting the clock-in component, and categorized under clock-in issues. The problem description is: Worker app crashes when attempting to clock in at facility 4821.

## Similar Past Incidents
* ID 5: Worker app showing incorrect pay rate on shift confirmation screen
  - Resolution pattern: stale rate cache not invalidated after facility updates
  - Applies to this incident: yes
* ID 4: Clock-out not registering – shift remains open for 6+ hours
  - Resolution pattern: WebSocket disconnect on poor connectivity causing clock-out events to drop
  - Applies to this incident: no

## Log Analysis Summary
* A NullPointerException in ShiftSessionManager.startSession() is consistently reproduced, indicating a null value is being passed to the method.
* The geofence radius for facility 4821 is 0, suggesting a misconfiguration or an issue with the geofencing service.
* Clock-in failure with a generic error message is displayed to the user, which may not provide sufficient information for diagnosis.
* A support ticket (TSE-3301) is auto-created due to the clock-in failure.

## Root Cause Hypothesis
Based on the log analysis and similar past incidents, I hypothesize that the root cause of the worker app crash is related to data synchronization and connectivity issues. Specifically, I believe that the ShiftSessionManager.startSession() method is failing due to a null value being passed to it, which may be caused by a stale rate cache or a WebSocket disconnect on poor connectivity. I suspect that the geofence radius being 0 for facility 4821 may be a contributing factor to the issue.

## Impacted Scope
The issue affects workers attempting to clock in at facility 4821. The estimated blast radius is limited to this specific facility, and the issue is ongoing. However, it may have historical implications if the stale rate cache or WebSocket disconnect issues are not addressed.

## Recommended Fix
1. Investigate and update the facility configuration for facility 4821 to ensure the geofence radius is set correctly.
2. Review and update the ShiftSessionManager.startSession() method to handle null values and ensure data synchronization.
3. Implement a retry mechanism for clock-in failures to provide a better user experience.
4. Validate the WebSocket connection and implement a fallback mechanism for poor connectivity.
5. Schedule a follow-up review to ensure the stale rate cache is invalidated after facility updates.

## Escalation Decision
Escalate to Engineering. The root cause hypothesis requires further investigation and code changes to resolve the issue.

## Monitoring Signals to Watch
* Geofence radius for facility 4821 should be set correctly and updated in real-time.
* NullPointerException in ShiftSessionManager.startSession() should be resolved, and the method should handle null values correctly.
* Clock-in failures should be reduced, and the retry mechanism should be effective.
* WebSocket connection should be stable, and the fallback mechanism should be triggered correctly.
* Support ticket auto-creation should be disabled or modified to provide more informative error messages.

---

*Report generated by [incident-pilot](https://github.com/amosalloyce/incident-pilot) — a multi-agent TSE investigation assistant.*