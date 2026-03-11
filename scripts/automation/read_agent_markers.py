#!/usr/bin/env python3
"""Read agent markers from Google Drive files or Confluence pages.

Agent markers are metadata properties set by PAC automation scripts
(pac_agent, pac_source, pac_timestamp, pac_version) that track which
tool created or last modified a document.

Usage:
    python read_agent_markers.py <url_or_id>

Supports:
    - Google Drive file URLs and IDs
    - Confluence page URLs and IDs
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = SCRIPT_DIR / "token_docs.json"
CREDENTIALS_PATH = SCRIPT_DIR / "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


# ---------------------------------------------------------------------------
# ID parsers
# ---------------------------------------------------------------------------

def parse_drive_id(value):
    """Extract a Google Drive file ID from a URL or bare ID.

    Args:
        value: URL or file ID string.

    Returns:
        str or None: Extracted file ID.
    """
    # URL patterns: /d/ID, /folders/ID, id=ID
    for pattern in [
        r"/d/([a-zA-Z0-9_-]+)",
        r"/folders/([a-zA-Z0-9_-]+)",
        r"[?&]id=([a-zA-Z0-9_-]+)",
    ]:
        match = re.search(pattern, value)
        if match:
            return match.group(1)

    # Bare ID
    if re.match(r"^[a-zA-Z0-9_-]{10,}$", value):
        return value

    return None


def parse_confluence_id(value):
    """Extract a Confluence page ID from a URL or bare ID.

    Args:
        value: URL or page ID string.

    Returns:
        str or None: Extracted page ID.
    """
    # URL pattern: /pages/ID or pageId=ID
    for pattern in [
        r"/pages/(\d+)",
        r"pageId=(\d+)",
    ]:
        match = re.search(pattern, value)
        if match:
            return match.group(1)

    # Bare numeric ID
    if re.match(r"^\d+$", value):
        return value

    return None


def detect_type(value):
    """Detect whether a value refers to a Drive file or Confluence page.

    Args:
        value: URL or ID string.

    Returns:
        str: 'drive' or 'confluence'.
    """
    if "atlassian.net" in value or "confluence" in value.lower():
        return "confluence"
    if "google.com" in value or "drive.google" in value or "docs.google" in value:
        return "drive"

    # Numeric IDs are likely Confluence
    if re.match(r"^\d+$", value):
        return "confluence"

    # Alphanumeric IDs are likely Drive
    return "drive"


# ---------------------------------------------------------------------------
# Marker readers
# ---------------------------------------------------------------------------

def read_drive_marker(file_id):
    """Read PAC agent marker properties from a Google Drive file.

    Args:
        file_id: Google Drive file ID.

    Returns:
        dict: Properties prefixed with 'pac_', or empty dict.
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("ERROR: No valid credentials. Run upload_to_docs.py first to authenticate.")
            sys.exit(1)

    service = build("drive", "v3", credentials=creds)
    result = service.files().get(
        fileId=file_id,
        fields="id,name,properties",
    ).execute()

    properties = result.get("properties", {})
    pac_props = {k: v for k, v in properties.items() if k.startswith("pac_")}

    return {
        "file_id": file_id,
        "file_name": result.get("name", ""),
        "markers": pac_props,
    }


def read_confluence_marker(page_id):
    """Read PAC agent marker from a Confluence page's properties.

    Looks for a page property named 'pac.agent_marker' that contains
    JSON metadata about the last automation run.

    Args:
        page_id: Confluence page ID.

    Returns:
        dict: Marker data, or empty dict.
    """
    import requests

    domain = os.environ.get("ATLASSIAN_DOMAIN")
    email = os.environ.get("ATLASSIAN_EMAIL")
    token = os.environ.get("ATLASSIAN_API_TOKEN")

    if not all([domain, email, token]):
        print("ERROR: Confluence credentials not set (ATLASSIAN_DOMAIN, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN).")
        sys.exit(1)

    # Get page info
    page_url = f"https://{domain}/wiki/rest/api/content/{page_id}"
    resp = requests.get(
        page_url,
        auth=(email, token),
        params={"expand": "metadata.properties"},
        timeout=30,
    )
    resp.raise_for_status()
    page_data = resp.json()

    # Check for pac.agent_marker property
    props_url = f"https://{domain}/wiki/rest/api/content/{page_id}/property/pac.agent_marker"
    try:
        prop_resp = requests.get(props_url, auth=(email, token), timeout=30)
        if prop_resp.status_code == 200:
            marker_data = prop_resp.json().get("value", {})
        else:
            marker_data = {}
    except Exception:
        marker_data = {}

    return {
        "page_id": page_id,
        "page_title": page_data.get("title", ""),
        "markers": marker_data,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Read PAC agent markers from a document"
    )
    parser.add_argument(
        "url_or_id",
        help="Google Drive URL/ID or Confluence URL/page ID",
    )
    args = parser.parse_args()

    value = args.url_or_id
    doc_type = detect_type(value)

    if doc_type == "drive":
        file_id = parse_drive_id(value)
        if not file_id:
            print(f"ERROR: Could not parse Drive file ID from: {value}")
            sys.exit(1)
        result = read_drive_marker(file_id)
    else:
        page_id = parse_confluence_id(value)
        if not page_id:
            print(f"ERROR: Could not parse Confluence page ID from: {value}")
            sys.exit(1)
        result = read_confluence_marker(page_id)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
