#!/usr/bin/env python3
"""Create and update a Google Sheets member directory.

Builds a team member spreadsheet from a configured member database,
including channel assignments and a master view across all channels.

Usage:
    python create_members_sheet.py --spreadsheet-id SHEET_ID [--config CONFIG]

Config file format (members_config.json):
    {
        "channels": {
            "channel-name": {
                "description": "Channel description",
                "members": ["email1@example.com", "email2@example.com"]
            }
        }
    }

Member database format (define in MEMBER_DB or load from config):
    {
        "email@example.com": {
            "name": "Full Name",
            "slack": "@slack_handle",
            "role": "Job Title",
            "department": "Department",
            "location": "City",
            "team_role": "lead|member|stakeholder"
        }
    }
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = SCRIPT_DIR / "token_sheets.json"
CREDENTIALS_PATH = SCRIPT_DIR / "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

# Member database — populate via config file or extend this dict.
# Format: {email: {name, slack, role, department, location, team_role}}
MEMBER_DB = {}
"""Member database.

Example entry:
    "jane.doe@example.com": {
        "name": "Jane Doe",
        "slack": "@jane.doe",
        "role": "Program Manager",
        "department": "Engineering",
        "location": "Helsinki",
        "team_role": "lead"
    }
"""


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_credentials():
    """Load or refresh Google OAuth2 credentials for Sheets API."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                print(f"ERROR: credentials.json not found at {CREDENTIALS_PATH}")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json())

    return creds


# ---------------------------------------------------------------------------
# Data builders
# ---------------------------------------------------------------------------

def load_config(config_path):
    """Load member and channel configuration from a JSON file.

    Args:
        config_path: Path to the config file.

    Returns:
        dict: Configuration with 'channels' and optional 'members' keys.
    """
    path = Path(config_path)
    if not path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)

    data = json.loads(path.read_text(encoding="utf-8"))

    # Merge members from config into MEMBER_DB
    if "members" in data:
        MEMBER_DB.update(data["members"])

    return data


def build_channel_data(channels_config):
    """Build per-channel member lists with details.

    Args:
        channels_config: Dict mapping channel names to {description, members}.

    Returns:
        dict: Channel name -> list of member row dicts.
    """
    result = {}
    for channel_name, channel_info in channels_config.items():
        rows = []
        member_emails = channel_info.get("members", [])
        description = channel_info.get("description", "")

        for email in member_emails:
            member = MEMBER_DB.get(email, {})
            rows.append({
                "email": email,
                "name": member.get("name", ""),
                "slack": member.get("slack", ""),
                "role": member.get("role", ""),
                "department": member.get("department", ""),
                "location": member.get("location", ""),
                "team_role": member.get("team_role", "member"),
            })

        result[channel_name] = {
            "description": description,
            "rows": sorted(rows, key=lambda r: r.get("name", "")),
        }

    return result


def build_master_view(channel_data):
    """Build a master view with all unique members across channels.

    Args:
        channel_data: Output from build_channel_data().

    Returns:
        list[dict]: Deduplicated member rows with channel assignments.
    """
    members = {}
    for channel_name, info in channel_data.items():
        for row in info["rows"]:
            email = row["email"]
            if email not in members:
                members[email] = dict(row)
                members[email]["channels"] = []
            members[email]["channels"].append(channel_name)

    result = []
    for email, data in sorted(members.items(), key=lambda x: x[1].get("name", "")):
        data["channels_str"] = ", ".join(data["channels"])
        result.append(data)

    return result


# ---------------------------------------------------------------------------
# Sheets operations
# ---------------------------------------------------------------------------

def update_sheet(spreadsheet_id, channel_data, master_view):
    """Update the Google Sheet with member data.

    Creates or updates sheets for each channel and a master view.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID.
        channel_data: Output from build_channel_data().
        master_view: Output from build_master_view().
    """
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)
    sheets = service.spreadsheets()

    # Get existing sheet names
    meta = sheets.get(spreadsheetId=spreadsheet_id).execute()
    existing_sheets = {s["properties"]["title"] for s in meta.get("sheets", [])}

    requests_batch = []

    # Ensure sheets exist
    all_sheet_names = ["Master View"] + list(channel_data.keys())
    for name in all_sheet_names:
        if name not in existing_sheets:
            requests_batch.append({
                "addSheet": {
                    "properties": {"title": name}
                }
            })

    if requests_batch:
        sheets.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests_batch},
        ).execute()

    # Update Master View
    header = ["Name", "Email", "Slack", "Role", "Department", "Location", "Team Role", "Channels"]
    master_rows = [header]
    for m in master_view:
        master_rows.append([
            m.get("name", ""),
            m.get("email", ""),
            m.get("slack", ""),
            m.get("role", ""),
            m.get("department", ""),
            m.get("location", ""),
            m.get("team_role", ""),
            m.get("channels_str", ""),
        ])

    sheets.values().update(
        spreadsheetId=spreadsheet_id,
        range="'Master View'!A1",
        valueInputOption="RAW",
        body={"values": master_rows},
    ).execute()
    print(f"Updated Master View: {len(master_rows) - 1} members")

    # Update channel sheets
    for channel_name, info in channel_data.items():
        header = ["Name", "Email", "Slack", "Role", "Department", "Location", "Team Role"]
        rows = [header]

        # Add description as first row context
        if info["description"]:
            rows.append([f"Description: {info['description']}"] + [""] * 6)

        for row in info["rows"]:
            rows.append([
                row.get("name", ""),
                row.get("email", ""),
                row.get("slack", ""),
                row.get("role", ""),
                row.get("department", ""),
                row.get("location", ""),
                row.get("team_role", ""),
            ])

        # Clear existing data first
        sheets.values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"'{channel_name}'!A:G",
        ).execute()

        sheets.values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{channel_name}'!A1",
            valueInputOption="RAW",
            body={"values": rows},
        ).execute()
        print(f"Updated '{channel_name}': {len(info['rows'])} members")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Create/update a Google Sheets member directory"
    )
    parser.add_argument(
        "--spreadsheet-id",
        required=True,
        help="Google Sheets spreadsheet ID",
    )
    parser.add_argument(
        "--config",
        default="members_config.json",
        help="Path to members config JSON file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    channels_config = config.get("channels", {})

    if not channels_config:
        print("ERROR: No channels defined in config.")
        sys.exit(1)

    channel_data = build_channel_data(channels_config)
    master_view = build_master_view(channel_data)

    update_sheet(args.spreadsheet_id, channel_data, master_view)
    print(f"\nSheet updated: https://docs.google.com/spreadsheets/d/{args.spreadsheet_id}")


if __name__ == "__main__":
    main()
