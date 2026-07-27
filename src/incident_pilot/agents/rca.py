"""
RCAAgent — synthesises all prior agent outputs into a structured
Root Cause Analysis (RCA) report in markdown format.

Inputs consumed from context:
  - ticket          : original ticket text
  - triage          : TriageAgent output
  - sql_summary     : SQLAgent prose summary
  - sql_raw_results : raw DB rows
  - log_analysis    : LogAnalystAgent structured analysis

Output added to context:
  - rca_report      : full markdown RCA string
  - escalation      : "TSE" | "Engineering" with one-sentence rationale
"""

import json

from incident_pilot.utils import groq_client

SYSTEM_PROMPT = """\
You are a Senior Technical Support Engineer writing a formal Root Cause Analysis (RCA)
for a production incident. Your audience is the Engineering team who will receive the
escalation and the Head of Worker Experience who needs an executive summary.

You will be given the full investigation context:
- Original ticket
- Triage classification (severity, component, category)
- SQL investigation summary (similar past incidents from the DB)
- Log analysis (error signatures, timeline, key findings)

Write a structured RCA report in markdown using EXACTLY these sections:

## Ticket
Restate the original ticket verbatim.

## Triage Summary
One paragraph: severity, component, category, and your one-sentence problem description.

## Similar Past Incidents
Bullet list of relevant historical incidents with IDs, titles, and whether their
resolution pattern applies here.

## Log Analysis Summary
Condensed version of the key log findings (3-6 bullets).

## Root Cause Hypothesis
1-2 paragraphs. State your primary root cause hypothesis. Be specific:
name the function, service, config value, or data condition you believe is responsible.
Use "hypothesis" language — you are not claiming certainty without a code fix confirmed.

## Impacted Scope
Who is affected (workers / facilities / operations), estimated blast radius, and
whether the issue is ongoing or historical.

## Recommended Fix
Numbered list of concrete remediation steps. Each step should be actionable by an engineer.
Include both the immediate fix and any follow-up hardening.

## Escalation Decision
State clearly: "Escalate to Engineering" or "Resolvable at TSE level".
Give a one-sentence rationale.

## Monitoring Signals to Watch
2-4 bullet points: what metrics, log patterns, or alerts should be monitored
to confirm the fix worked or to detect recurrence.

Write in professional, direct TSE language. No markdown code fences. Use ## headers only.
"""


class RCAAgent:
    """
    Synthesises all investigation context into a final structured RCA markdown report.
    """

    name = "RCAAgent"

    def run(self, context: dict) -> dict:
        """
        Parameters
        ----------
        context : dict
            Must contain: 'ticket', 'triage', 'sql_summary', 'log_analysis'.

        Returns
        -------
        dict
            Updated context with 'rca_report' (str markdown) and 'escalation' (str).
        """
        user_message = (
            f"Original ticket:\n{context['ticket']}\n\n"
            f"Triage:\n{json.dumps(context.get('triage', {}), indent=2)}\n\n"
            f"SQL Investigation Summary:\n{context.get('sql_summary', 'N/A')}\n\n"
            f"Log Analysis:\n{context.get('log_analysis', 'N/A')}"
        )

        rca_report = groq_client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            max_tokens=2048,
        )

        context["rca_report"] = rca_report

        # Extract escalation decision from report text
        escalation = "Escalate to Engineering"  # safe default
        lower = rca_report.lower()
        if "resolvable at tse" in lower or "no escalation" in lower:
            escalation = "Resolvable at TSE level"
        context["escalation"] = escalation

        return context
