#!/usr/bin/env python3
"""Draft Jira tickets from a structured JSON input file.

Reads candidate ticket data and generates both a formatted JSON
payload file and a markdown preview for review before submission.

Usage:
    python draft_jira_tickets.py [input_file]

Environment:
    JIRA_PROJECT_KEY — Jira project key (e.g., "PROJ")

Input file format (JSON):
    [
        {
            "summary": "Ticket title",
            "description": "Detailed description",
            "issue_type": "Task",
            "priority": "Medium",
            "labels": ["automation"],
            "components": ["backend"]
        }
    ]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_json(filepath):
    """Read and parse a JSON file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        list: Parsed JSON data (expected to be a list of candidate dicts).
    """
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    return json.loads(path.read_text(encoding="utf-8"))


def build_drafts(candidates, project_key):
    """Build Jira-ready ticket drafts from candidate data.

    Args:
        candidates: List of candidate dicts with summary, description, etc.
        project_key: Jira project key.

    Returns:
        list[dict]: Jira API-compatible ticket payloads.
    """
    drafts = []
    for idx, candidate in enumerate(candidates, 1):
        draft = {
            "fields": {
                "project": {"key": project_key},
                "summary": candidate.get("summary", f"Draft ticket {idx}"),
                "description": candidate.get("description", ""),
                "issuetype": {"name": candidate.get("issue_type", "Task")},
            }
        }

        if candidate.get("priority"):
            draft["fields"]["priority"] = {"name": candidate["priority"]}

        if candidate.get("labels"):
            draft["fields"]["labels"] = candidate["labels"]

        if candidate.get("components"):
            draft["fields"]["components"] = [
                {"name": c} for c in candidate["components"]
            ]

        drafts.append(draft)

    return drafts


def write_markdown(drafts, output_path):
    """Write a markdown preview of the drafted tickets.

    Args:
        drafts: List of Jira ticket draft dicts.
        output_path: Path for the markdown output file.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Draft Jira Tickets",
        "",
        f"Generated: {now}",
        f"Total tickets: {len(drafts)}",
        "",
    ]

    for idx, draft in enumerate(drafts, 1):
        fields = draft["fields"]
        lines.append(f"## {idx}. {fields['summary']}")
        lines.append("")
        lines.append(f"- **Project**: {fields['project']['key']}")
        lines.append(f"- **Type**: {fields['issuetype']['name']}")

        if "priority" in fields:
            lines.append(f"- **Priority**: {fields['priority']['name']}")
        if "labels" in fields:
            lines.append(f"- **Labels**: {', '.join(fields['labels'])}")
        if "components" in fields:
            comp_names = [c["name"] for c in fields["components"]]
            lines.append(f"- **Components**: {', '.join(comp_names)}")

        lines.append("")
        if fields.get("description"):
            lines.append(fields["description"])
            lines.append("")

        lines.append("---")
        lines.append("")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"Markdown preview: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Draft Jira tickets from a JSON input file"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="ticket_candidates.json",
        help="Path to JSON input file (default: ticket_candidates.json)",
    )
    args = parser.parse_args()

    project_key = os.environ.get("JIRA_PROJECT_KEY")
    if not project_key:
        print("ERROR: JIRA_PROJECT_KEY environment variable is not set.")
        sys.exit(1)

    candidates = read_json(args.input_file)
    drafts = build_drafts(candidates, project_key)

    # Write JSON payloads
    json_output = Path("drafted_tickets.json")
    json_output.write_text(
        json.dumps(drafts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"JSON payloads: {json_output} ({len(drafts)} tickets)")

    # Write markdown preview
    write_markdown(drafts, "drafted_tickets.md")


if __name__ == "__main__":
    main()
