"""
Pipeline orchestrator — runs the four agents in sequence and streams each
agent's output to the terminal using Rich panels.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from incident_pilot.agents.triage import TriageAgent
from incident_pilot.agents.sql_agent import SQLAgent
from incident_pilot.agents.log_analyst import LogAnalystAgent
from incident_pilot.agents.rca import RCAAgent

console = Console()

# (agent_instance, panel_colour, output_context_key)
_AGENTS = [
    (TriageAgent(),      "bold cyan",    "triage"),
    (SQLAgent(),         "bold yellow",  "sql_summary"),
    (LogAnalystAgent(),  "bold magenta", "log_analysis"),
    (RCAAgent(),         "bold green",   "rca_report"),
]


def _format_agent_output(agent_name: str, context: dict) -> str:
    """
    Extract the relevant output field for this agent and format it for display.
    """
    import json

    if agent_name == "TriageAgent":
        triage = context.get("triage", {})
        return (
            f"Severity : {triage.get('severity', '?')}\n"
            f"Component: {triage.get('component', '?')}\n"
            f"Category : {triage.get('category', '?')}\n"
            f"Summary  : {triage.get('summary', '?')}"
        )
    if agent_name == "SQLAgent":
        n = len(context.get("sql_raw_results", []))
        keywords = context.get("sql_keywords", [])
        summary = context.get("sql_summary", "")
        return f"Keywords searched: {keywords}\nMatches found: {n}\n\n{summary}"
    if agent_name == "LogAnalystAgent":
        log_file = context.get("log_file_used", "none")
        analysis = context.get("log_analysis", "")
        return f"Log file: {log_file}\n\n{analysis}"
    if agent_name == "RCAAgent":
        escalation = context.get("escalation", "?")
        report_preview = context.get("rca_report", "")[:600]
        return f"Escalation: {escalation}\n\n{report_preview}..."
    return ""


def run_pipeline(ticket: str) -> dict:
    """
    Execute the full 4-agent investigation pipeline.

    Parameters
    ----------
    ticket : str
        The raw support ticket text supplied by the user.

    Returns
    -------
    dict
        The accumulated investigation context containing all agent outputs.
    """
    context: dict = {"ticket": ticket}

    console.print()
    console.rule("[bold white]incident-pilot — Multi-Agent TSE Investigation[/bold white]")
    console.print(f"\n[dim]Ticket:[/dim] {ticket}\n")

    for agent, colour, _ in _AGENTS:
        console.print(f"[{colour}]▶ Running {agent.name}...[/{colour}]")
        context = agent.run(context)

        output_text = _format_agent_output(agent.name, context)
        panel = Panel(
            Text(output_text),
            title=f"[{colour}]{agent.name}[/{colour}]",
            border_style=colour.replace("bold ", ""),
            expand=True,
        )
        console.print(panel)
        console.print()

    console.rule("[bold green]Investigation Complete[/bold green]")
    console.print()
    return context
