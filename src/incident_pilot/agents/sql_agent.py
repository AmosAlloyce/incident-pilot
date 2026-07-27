"""
SQLAgent — queries the incidents database for similar past tickets and
summarises the findings in plain English using Groq.

Steps:
  1. Extract search keywords from triage context (component + category + key terms).
  2. Call find_similar_incidents() to fetch matching past incidents from SQLite.
  3. Ask Groq to summarise the SQL results in TSE language.
"""

import json

from incident_pilot.db.queries import find_similar_incidents
from incident_pilot.utils import groq_client

SYSTEM_PROMPT = """\
You are a Technical Support Engineer reviewing historical incident data to determine
whether a new ticket matches any known past issues.

You will be given:
- The current ticket's triage summary (component, severity, category, summary).
- A JSON list of similar past incidents retrieved from the incidents database.

Respond with a structured plain-English paragraph (3-6 sentences) that:
1. States whether any strong matches were found in the database.
2. Names the most relevant past incident(s) by title and ID.
3. Highlights key resolution steps from those incidents that may apply now.
4. Notes the pattern (e.g. recurring component, data migration side-effects, config issue).

If no matches were found, say so clearly and note that this may be a new issue pattern.
Do NOT output JSON. Output readable prose only.
"""


def _extract_keywords(triage: dict) -> list[str]:
    """
    Build a keyword list from triage fields to drive the SQL search.
    """
    keywords: list[str] = []

    component = triage.get("component", "")
    category = triage.get("category", "")
    summary = triage.get("summary", "")

    if component and component != "unknown":
        keywords.append(component)

    # Map category to common search terms
    category_map = {
        "clock-in":    ["clock-in", "clock in"],
        "geofence":    ["geofence", "boundary", "location"],
        "quiz":        ["quiz", "submission"],
        "nfc":         ["nfc", "tag", "scan"],
        "auth":        ["auth", "login", "permission"],
        "performance": ["latency", "timeout", "slow"],
        "data":        ["data", "migration", "sync"],
    }
    keywords.extend(category_map.get(category, [category]))

    # Pull significant words from the summary (>4 chars, not stop-words)
    stop = {"the", "and", "for", "with", "that", "this", "from", "when", "after", "into"}
    for word in summary.lower().split():
        clean = word.strip(".,;:\"'()—")
        if len(clean) > 4 and clean not in stop and clean not in keywords:
            keywords.append(clean)

    return list(dict.fromkeys(keywords))[:8]  # deduplicate, cap at 8


class SQLAgent:
    """
    Searches the historical incidents DB and summarises matches via Groq.
    """

    name = "SQLAgent"

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
              'sql_keywords'       — list[str] used for the query
              'sql_raw_results'    — list[dict] rows from DB
              'sql_summary'        — str Groq-generated prose summary
        """
        triage = context["triage"]
        keywords = _extract_keywords(triage)
        context["sql_keywords"] = keywords

        rows = find_similar_incidents(keywords, limit=5)
        context["sql_raw_results"] = rows

        user_message = (
            f"Current ticket triage:\n{json.dumps(triage, indent=2)}\n\n"
            f"Keywords used for DB search: {keywords}\n\n"
            f"Similar past incidents found ({len(rows)}):\n{json.dumps(rows, indent=2)}"
        )

        summary = groq_client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
        )
        context["sql_summary"] = summary
        return context
