# incident-pilot — Autonomous SRE War Room

[![Live Production Cockpit](https://img.shields.io/badge/Live_Cockpit-alloyce.duckdns.org%2Fincident--pilot-f59e0b?style=for-the-badge&logo=google-chrome&logoColor=white)](https://alloyce.duckdns.org/incident-pilot)
![CI](../../actions/workflows/ci.yml/badge.svg)

**A multi-agent Technical Support Engineer (TSE) and SRE investigation platform.**

## 🌐 Live Web System & AI Agent Swarm

The platform is deployed live on **Oracle Cloud Always Free (ARM64)** under the unified ecosystem endpoint:
- **Interactive Cockpit**: [https://alloyce.duckdns.org/incident-pilot](https://alloyce.duckdns.org/incident-pilot)
- **Flagship Ecosystem Hub**: [https://alloyce.duckdns.org](https://alloyce.duckdns.org)
- **Guided Voice Walkthrough**: Built-in human-sounding narrated tour walking viewers through log ingestion, chaos injection (connection pool leaks), automated root-cause isolation, and runbook approval gates.

### Autonomous AI Agent Swarm (Groq LLaMA 3.3)
- **Incident Pilot Prime** — Incident Commander AI coordinating triage and response.
- **SRE Triage Agent** — Classifies anomaly severity (P1/P2/P3) and filters noise in high-velocity log streams.
- **Root Cause Investigator** — Cross-references error stack traces against recent git commits to pinpoint failure origins.
- **Runbook Synthesizer** — Synthesizes immediate tactical mitigation runbooks (e.g. pool expansion, cache purge).
- **Human-in-the-Loop Safety Gate** — Operator authorization gate before executing automated remediation actions.

### n8n Workflow Automation
Includes exportable production n8n workflow definition in [`workflows/incident-remediation-flow.json`](workflows/incident-remediation-flow.json):
```
Sentry Error Webhook -> Groq Root Cause Agent -> Slack War Room Alert -> Execute Runbook Mitigation
```

Feed it a support ticket or stream logs. Watch specialised AI agents collaborate to triage,
query a historical incidents database, analyse application logs, and produce a
structured Root Cause Analysis (RCA) report — all in seconds.

---

## What This Demonstrates

This project was built to demonstrate the exact skills required of a Technical Support
Engineer working at a production platform serving hundreds of thousands of users:

| Agent | Clipboard JD Skill |
|---|---|
| **TriageAgent** | Rapidly classify incoming issues by severity, component, and category — turning noisy reports into high-signal work items |
| **SQLAgent** | Interrogate a historical incidents database to surface similar past tickets, resolution patterns, and recurrence signals |
| **LogAnalystAgent** | Parse structured application logs to identify error signatures, affected services, and event timelines — like reading Datadog without the GUI |
| **RCAAgent** | Synthesise all findings into a production-ready RCA: root cause hypothesis, impacted scope, recommended fix, escalation decision, and monitoring signals |

Every agent produces **evidence-backed, reproducible output** — clean enough for an
engineer to pick up without rework.

---

## Architecture

```
 Support Ticket (--ticket "...")
           │
           ▼
  ┌─────────────────┐
  │  TriageAgent    │  Classifies severity (P1–P4), component, category
  └────────┬────────┘
           │ triage context
           ▼
  ┌─────────────────┐
  │   SQLAgent      │  Queries SQLite incidents DB · summarises matches via LLM
  └────────┬────────┘
           │ + sql_summary, sql_raw_results
           ▼
  ┌─────────────────┐
  │ LogAnalystAgent │  Selects relevant log file · extracts errors, timeline, findings
  └────────┬────────┘
           │ + log_analysis
           ▼
  ┌─────────────────┐
  │   RCAAgent      │  Synthesises all context → structured RCA markdown report
  └────────┬────────┘
           │
           ▼
  reports/RCA_<timestamp>.md
```

**LLM backend:** [Groq](https://console.groq.com) — free tier, `llama-3.1-8b-instant`  
**Database:** SQLite (stdlib) — seeded with 16 realistic Clipboard-style incidents  
**Log files:** 3 structured JSON-Lines files simulating Datadog-style service logs

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/amosalloyce/incident-pilot.git
cd incident-pilot
make install

# 2. Add your Groq API key (free at https://console.groq.com/keys)
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here

# 3. Seed the incidents database
make seed

# 4. Run an investigation
make run TICKET="Worker app crashes when clocking in at facility 4821"
```

A timestamped markdown report is written to `./reports/`.

---

## Example Output

```
──────────── incident-pilot — Multi-Agent TSE Investigation ─────────────

Ticket: Worker app crashes when clocking in at facility 4821

▶ Running TriageAgent...
╭─────────────────── TriageAgent ───────────────────╮
│ Severity : P2                                     │
│ Component: worker-app                             │
│ Category : clock-in                               │
│ Summary  : Worker app crashes on clock-in at 4821 │
╰───────────────────────────────────────────────────╯

▶ Running SQLAgent...
▶ Running LogAnalystAgent...
▶ Running RCAAgent...

────────────────── Investigation Complete ──────────────────

✓ Report written: reports/RCA_20241103_081347.md
```

**→ [View a sample RCA report](reports/SAMPLE_RCA.md)**

---

## Project Structure

```
incident-pilot/
├── src/incident_pilot/
│   ├── main.py                 # CLI entry point
│   ├── pipeline.py             # orchestrates the 4-agent sequence
│   ├── agents/
│   │   ├── triage.py           # TriageAgent
│   │   ├── sql_agent.py        # SQLAgent
│   │   ├── log_analyst.py      # LogAnalystAgent
│   │   └── rca.py              # RCAAgent
│   ├── db/
│   │   ├── schema.sql          # incidents + log_events DDL
│   │   ├── seed.py             # seeds 16 realistic incidents
│   │   └── queries.py          # SQL helper functions
│   └── utils/
│       ├── groq_client.py      # thin Groq SDK wrapper
│       └── report.py           # markdown report writer
├── tests/
│   ├── test_db_queries.py      # 10 unit tests — SQL helpers
│   └── test_triage_agent.py    # 5 unit tests — TriageAgent (Groq mocked)
├── sample_logs/
│   ├── clock_in_crash.log      # JSON-Lines: worker-app NPE on clock-in
│   ├── geofence_timeout.log    # JSON-Lines: geofence rate-limit + retry exhaustion
│   └── facility_quiz_500.log   # JSON-Lines: facility API 500 on quiz submit
└── reports/
    └── SAMPLE_RCA.md           # pre-generated sample report
```

---

## Running Tests

```bash
make test
```

All 15 tests pass with no network calls — Groq is mocked in unit tests so CI runs
without an API key.

---

## Supported Ticket Types

The DB and log files cover the four core Clipboard platform components:

| Component | Example Tickets |
|---|---|
| `worker-app` | Clock-in crashes, pay rate errors, double clock-ins |
| `geofence-service` | Timeout failures, boundary misconfiguration, enforcement disabled |
| `facility-api` | Quiz 500 errors, latency spikes, admin permission failures |
| `nfc-service` | Tag format mismatches, offline readers, out-of-order events |

---

## Tech Stack

- **Python 3.11+**
- **[Groq](https://groq.com)** — free LLM API (`llama-3.1-8b-instant`)
- **SQLite** — stdlib, no ORM
- **[Rich](https://github.com/Textualize/rich)** — terminal output
- **pytest** + **pytest-mock** — testing
- **python-dotenv** — env config

---

*Built as a portfolio demonstration of TSE-relevant engineering skills.*  
*See also: [Clipboard Health](https://www.clipboardhealth.com)*
