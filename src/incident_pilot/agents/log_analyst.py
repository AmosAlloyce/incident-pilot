"""
LogAnalystAgent — selects the most relevant sample log file based on the
component identified by TriageAgent, parses it for error signatures,
and produces a structured log analysis via Groq.
"""

import json
from pathlib import Path

from incident_pilot.utils import groq_client

SYSTEM_PROMPT = """\
You are a Technical Support Engineer performing log analysis during an active incident investigation.

You will be given:
- The triage context for the current ticket (component, severity, category, summary).
- The raw contents of a structured application log file (JSON-Lines format).

Your job is to produce a log analysis report with the following sections:

**Error Signatures**
List each unique ERROR-level event found in the logs. Include the timestamp, service,
error message, and any stack trace fragment.

**Affected Services**
List all distinct services that appear in the logs with ERRORs or WARNs.

**Timeline**
Reconstruct the sequence of events leading up to the failure in 4-8 bullet points
(timestamp — event description).

**Key Findings**
2-4 bullet points identifying the most diagnostically significant observations
(e.g. rate limit hit, null config value, specific exception class, retry exhaustion).

Be concise. Use plain English. No JSON output.
"""

# Maps component names to log file stems
COMPONENT_LOG_MAP = {
    "worker-app":       "clock_in_crash",
    "geofence-service": "geofence_timeout",
    "facility-api":     "facility_quiz_500",
    "nfc-service":      "clock_in_crash",   # NFC failures surface in worker-app logs too
}

# __file__ = src/incident_pilot/agents/log_analyst.py
# .parent * 4 = project root
SAMPLE_LOGS_DIR = Path(__file__).parent.parent.parent.parent / "sample_logs"


def _find_log_file(component: str) -> Path | None:
    """
    Return the Path to the most relevant sample log file for the given component.
    Falls back to clock_in_crash if no mapping exists.
    """
    stem = COMPONENT_LOG_MAP.get(component, "clock_in_crash")
    candidate = SAMPLE_LOGS_DIR / f"{stem}.log"
    if candidate.exists():
        return candidate
    # Try any log file as last resort
    logs = list(SAMPLE_LOGS_DIR.glob("*.log"))
    return logs[0] if logs else None


def _summarise_log(log_path: Path) -> str:
    """
    Read log file and return a condensed version (ERROR + WARN lines + first/last INFO).
    Keeps total chars under 4000 to stay within Groq context limits.
    """
    lines = log_path.read_text(encoding="utf-8").splitlines()
    important: list[str] = []
    info_lines: list[str] = []

    for line in lines:
        try:
            entry = json.loads(line)
            if entry.get("level") in ("ERROR", "WARN"):
                important.append(line)
            else:
                info_lines.append(line)
        except json.JSONDecodeError:
            important.append(line)

    # Include first 3 and last 2 INFO lines for timeline context
    selected = info_lines[:3] + important + info_lines[-2:]
    content = "\n".join(selected)
    return content[:4000]


class LogAnalystAgent:
    """
    Reads the most relevant sample log file and produces a structured log analysis.
    """

    name = "LogAnalystAgent"

    def run(self, context: dict) -> dict:
        """
        Parameters
        ----------
        context : dict
            Must contain 'triage' (dict) from TriageAgent.

        Returns
        -------
        dict
            Updated context with:
              'log_file_used'  — str path of the log file analysed
              'log_analysis'   — str structured analysis produced by Groq
        """
        triage = context["triage"]
        component = triage.get("component", "unknown")

        log_path = _find_log_file(component)
        if log_path is None:
            context["log_file_used"] = None
            context["log_analysis"] = "No sample log file available for this component."
            return context

        context["log_file_used"] = str(log_path.name)
        log_content = _summarise_log(log_path)

        user_message = (
            f"Triage context:\n{json.dumps(triage, indent=2)}\n\n"
            f"Log file: {log_path.name}\n\n"
            f"Log contents:\n{log_content}"
        )

        analysis = groq_client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=1500,
        )
        context["log_analysis"] = analysis
        return context
