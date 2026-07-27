"""
CLI entry point for incident-pilot.

Usage
-----
python -m incident_pilot.main --ticket "Worker app crashes when clocking in at facility 4821"

Or via Makefile:
make run TICKET="Worker app crashes when clocking in at facility 4821"
"""

import argparse
import sys

from rich.console import Console
from rich.text import Text

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="incident-pilot",
        description=(
            "Multi-agent TSE investigation assistant. "
            "Accepts a support ticket and produces a structured RCA report."
        ),
    )
    parser.add_argument(
        "--ticket",
        type=str,
        required=True,
        help='The support ticket text to investigate. E.g. --ticket "Worker app crashes on clock-in"',
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to write the RCA report into (default: ./reports/)",
    )

    args = parser.parse_args()

    ticket = args.ticket.strip()
    if not ticket:
        console.print("[red]Error:[/red] --ticket cannot be empty.")
        sys.exit(1)

    # Run pipeline (imports here to defer heavy imports until we actually need them)
    from incident_pilot.pipeline import run_pipeline
    from incident_pilot.utils.report import write_report

    try:
        context = run_pipeline(ticket)
        report_path = write_report(context, output_dir=args.output_dir)
        console.print(f"[bold green]✓ Report written:[/bold green] {report_path}")
    except EnvironmentError as exc:
        console.print(f"[red]Configuration error:[/red] {exc}")
        sys.exit(1)
    except Exception as exc:
        console.print(f"[red]Unexpected error:[/red] {exc}")
        raise


if __name__ == "__main__":
    main()
