# Incident Pilot — Autonomous SRE War Room & Runbook Executor

[![Production Live](https://img.shields.io/badge/Production-Live%20at%20alloyce.duckdns.org%2Fincident-f59e0b?style=for-the-badge&logo=caddy)](https://alloyce.duckdns.org/incident)
[![Python 3.12](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![OpenTelemetry](https://img.shields.io/badge/Telemetry-OpenTelemetry-F5A800?style=for-the-badge&logo=opentelemetry)](https://opentelemetry.io)
[![Groq AI Commander](https://img.shields.io/badge/Incident%20Commander-Groq%20LLaMA%203.3-f55036?style=for-the-badge)](https://groq.com)
[![n8n PagerDuty](https://img.shields.io/badge/Alerting-n8n%20War%20Room-ea4b71?style=for-the-badge&logo=n8n)](https://n8n.io)

> Production-grade autonomous SRE platform that ingests high-throughput OpenTelemetry spans, isolates production anomalies, correlates error traces with git commit history via Groq AI, and executes vetted mitigation runbooks with human-in-the-loop signoff.

---

## 1. System Architecture

```mermaid
flowchart TD
    Ingress["Streaming Ingestion Pipeline (Kafka / OTel)"] --> Engine["Incident Pilot Ingestion Worker (:8000)"]
    Engine --> AnomalyEngine["Statistical Anomaly Detector (3.5σ Threshold)"]
    
    subgraph SRECommander["Autonomous SRE Commander Swarm (Groq LLaMA 3.3)"]
        AnomalyEngine -->|P1 Alarm| Commander["Incident Pilot Prime"]
        Commander --> Triage["SRE Triage Agent"]
        Commander --> Investigator["Root Cause Investigator (Git Diff & Stacktrace Correlation)"]
        Commander --> Runbook["Runbook Synthesizer"]
        Commander --> PostMortem["Post-Mortem Author (Markdown Generator)"]
    end

    subgraph Remediation["Human-in-the-Loop & n8n PagerDuty Engine"]
        Runbook --> Modal["Human Approval Gate (Modal Verification)"]
        Modal -->|Operator Approves| Execute["Automated Cluster Mitigation"]
        Execute --> Slack["PagerDuty & Slack Broadcast"]
        Execute --> Report["Export Post-Mortem Retrospective"]
    end
```

---

## 2. P1 Incident Triage Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor System as Ingestion Stream
    participant SRE as Incident Pilot Engine
    participant AI as Groq Root-Cause Investigator
    actor Operator as Human SRE Lead
    participant N8N as n8n Pipeline

    System->>SRE: FATAL: [DB-CONN-01] Connection pool exhausted (100/100)!
    SRE->>SRE: Declare P1 Critical Incident (Alarm Engaged)
    SRE->>AI: Correlate stacktrace with trailing 24h Git commits
    AI-->>SRE: Root Cause: Commit e7f8b9 ("unclosed transaction handle in billing loop")
    SRE->>AI: Synthesize tactical mitigation runbook
    AI-->>SRE: Runbook: Terminate idle sessions, expand ceiling to 250, shift traffic
    SRE->>Operator: Present Human Approval Gate Modal
    Operator->>SRE: Authorize Mitigation Runbook Execution
    SRE->>N8N: Trigger /api/incident-pilot/mitigate
    N8N->>System: Expand connection pool & kill idle sessions
    SRE->>Operator: Mark Outage Resolved (MTTR: 14.8s) & Download Post-Mortem
```

---

## 3. Interactive SRE Capabilities

- **Real-Time Ingestion Console**: Processes OpenTelemetry spans, Kubernetes container logs, and database metrics with zero parsing lag.
- **Chaos Engineering Sandbox**: Allows operators to inject artificial production failures:
  1. *PostgreSQL Connection Pool Exhaustion* (100/100 active connections consumed).
  2. *JVM/Worker Heap Exhaustion* (94% heap memory leak with GC stop-the-world).
  3. *Ingress DDoS Wave* (45,000 req/sec edge surge breaching Envoy limits).
- **Correlated Git Commit Diff Inspector**: Automatically highlights the exact commit and code line responsible for the outage.
- **1-Click Post-Mortem Export**: Generates industry-standard incident retrospectives complete with timeline, root cause, and follow-up action items.

---

## 4. Live Production Walkthrough

Experience the live SRE war room, inject chaos faults, and test autonomous runbook execution at:
👉 **[https://alloyce.duckdns.org/incident](https://alloyce.duckdns.org/incident)**

---

## 5. Repository Structure

```
.
├── app/
│   ├── main.py          # FastAPI telemetry ingestion engine
│   ├── agents/          # Groq AI SRE commander swarm
│   ├── analyzer/        # Trace correlation & git diff parser
│   └── chaos/           # Synthetic chaos injection scenarios
├── workflows/           # n8n PagerDuty & Slack automation JSONs
├── tests/               # Chaos & triage automated test suite
├── Dockerfile           # Production container build
└── compose.yaml         # Standalone war room setup
```
