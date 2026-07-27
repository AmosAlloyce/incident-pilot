"""
TriageAgent — classifies an incoming support ticket into:
  - severity:  P1 / P2 / P3 / P4
  - component: worker-app | geofence-service | facility-api | nfc-service | unknown
  - category:  clock-in | geofence | quiz | nfc | auth | performance | data | other
  - summary:   one-sentence plain-English description of the problem
"""

from incident_pilot.utils import groq_client

SYSTEM_PROMPT = """\
You are a Senior Technical Support Engineer at a healthcare staffing platform.
Your job is to triage incoming support tickets with precision and speed.

Given a ticket description, respond with ONLY a JSON object — no markdown fences, no prose.
Use this exact schema:
{
  "severity": "P1" | "P2" | "P3" | "P4",
  "component": "worker-app" | "geofence-service" | "facility-api" | "nfc-service" | "unknown",
  "category":  "clock-in" | "geofence" | "quiz" | "nfc" | "auth" | "performance" | "data" | "other",
  "summary":   "<one sentence describing the core problem>"
}

Severity guide:
  P1 — production outage or data loss affecting multiple users right now
  P2 — major feature broken for identifiable user(s), no workaround
  P3 — feature degraded, workaround exists or low user count affected
  P4 — minor cosmetic issue or low-impact edge case

Component guide:
  worker-app        — mobile or web app used by healthcare workers
  geofence-service  — location/boundary enforcement at facilities
  facility-api      — quiz, config, or admin functionality for facilities
  nfc-service       — NFC tag scanning for clock-in/out
  unknown           — cannot be determined from the ticket text
"""


class TriageAgent:
    """
    Classifies a raw support ticket into structured triage fields via Groq.
    """

    name = "TriageAgent"

    def run(self, context: dict) -> dict:
        """
        Parameters
        ----------
        context : dict
            Must contain 'ticket' (str) — the raw support ticket text.

        Returns
        -------
        dict
            Original context updated with 'triage' key containing severity,
            component, category, and summary.
        """
        import json

        ticket = context["ticket"]
        raw = groq_client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=f"Ticket: {ticket}",
        )

        try:
            triage = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: extract JSON from within the response if Groq added prose
            import re
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                triage = json.loads(match.group())
            else:
                triage = {
                    "severity": "P3",
                    "component": "unknown",
                    "category": "other",
                    "summary": raw[:200],
                }

        context["triage"] = triage
        return context
