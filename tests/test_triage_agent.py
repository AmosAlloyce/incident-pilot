"""
Unit tests for TriageAgent.
All Groq API calls are mocked — no network required.
"""

import json
import pytest


class TestTriageAgent:
    """Tests for TriageAgent.run() — Groq is always mocked."""

    def _make_groq_response(self, severity, component, category, summary):
        return json.dumps({
            "severity": severity,
            "component": component,
            "category": category,
            "summary": summary,
        })

    def test_clock_in_crash_maps_to_worker_app(self, mocker):
        mocker.patch(
            "incident_pilot.utils.groq_client.chat",
            return_value=self._make_groq_response(
                "P2", "worker-app", "clock-in",
                "Worker app crashes when clocking in due to NullPointerException."
            ),
        )
        from incident_pilot.agents.triage import TriageAgent
        agent = TriageAgent()
        context = agent.run({"ticket": "Worker app crashes when clocking in at facility 4821"})

        triage = context["triage"]
        assert triage["component"] == "worker-app"
        assert triage["severity"] in ("P1", "P2", "P3", "P4")
        assert triage["category"] == "clock-in"

    def test_geofence_ticket_severity_is_p2_or_lower(self, mocker):
        mocker.patch(
            "incident_pilot.utils.groq_client.chat",
            return_value=self._make_groq_response(
                "P2", "geofence-service", "geofence",
                "Geofence service timing out causing clock-in failures."
            ),
        )
        from incident_pilot.agents.triage import TriageAgent
        agent = TriageAgent()
        context = agent.run({"ticket": "Geofence check timing out for workers at hospital campus"})

        triage = context["triage"]
        severity = triage["severity"]
        # P2, P3, or P4 — not P1 for a single-facility timeout described as intermittent
        assert severity in ("P1", "P2", "P3", "P4"), f"Unexpected severity: {severity}"
        # Specifically test that this parses to P2 as mocked
        assert severity == "P2"

    def test_triage_result_stored_in_context(self, mocker):
        mocker.patch(
            "incident_pilot.utils.groq_client.chat",
            return_value=self._make_groq_response(
                "P3", "facility-api", "quiz",
                "Facility quiz returning 500 on submission."
            ),
        )
        from incident_pilot.agents.triage import TriageAgent
        agent = TriageAgent()
        context = {"ticket": "Quiz submission fails with 500 error", "other_key": "preserved"}
        result = agent.run(context)

        # Original keys preserved
        assert result["other_key"] == "preserved"
        assert "triage" in result

    def test_malformed_groq_response_uses_fallback(self, mocker):
        """If Groq returns prose instead of JSON, agent should not crash."""
        mocker.patch(
            "incident_pilot.utils.groq_client.chat",
            return_value="Sorry, I cannot classify this ticket right now.",
        )
        from incident_pilot.agents.triage import TriageAgent
        agent = TriageAgent()
        context = agent.run({"ticket": "Some unknown issue"})

        triage = context["triage"]
        assert "severity" in triage
        assert "component" in triage
        # Fallback values
        assert triage["severity"] == "P3"
        assert triage["component"] == "unknown"

    def test_json_embedded_in_prose_is_extracted(self, mocker):
        """If Groq wraps JSON in text, the agent should still parse it."""
        embedded = (
            'Here is the classification:\n'
            '{"severity": "P1", "component": "nfc-service", '
            '"category": "nfc", "summary": "NFC readers offline at 8 facilities."}\n'
            'Let me know if you need more detail.'
        )
        mocker.patch("incident_pilot.utils.groq_client.chat", return_value=embedded)

        from incident_pilot.agents.triage import TriageAgent
        agent = TriageAgent()
        context = agent.run({"ticket": "NFC reader not scanning"})

        triage = context["triage"]
        assert triage["component"] == "nfc-service"
        assert triage["severity"] == "P1"
