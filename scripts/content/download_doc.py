#!/usr/bin/env python3
"""Download a Google Doc and convert it to markdown.

Extracts text content from a Google Doc via the Docs API, preserving
heading levels, and saves as markdown.

Usage:
    python download_doc.py <url_or_id> [output_path]

Environment:
    Token and credentials are loaded from the scripts directory
    (same auth as upload_to_docs.py).
"""

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = SCRIPT_DIR / "token_docs.json"
CREDENTIALS_PATH = SCRIPT_DIR / "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
]


def get_credentials():
    """Load or refresh Google OAuth2 credentials."""
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


def extract_doc_id(url_or_id):
    """Extract the Google Doc ID from a URL or return the ID as-is.

    Supports formats:
        - https://docs.google.com/document/d/DOC_ID/edit
        - https://docs.google.com/document/d/DOC_ID
        - Plain DOC_ID string

    Args:
        url_or_id: URL or document ID string.

    Returns:
        str: The extracted document ID.
    """
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url_or_id)
    if match:
        return match.group(1)
    # Assume it is a bare ID if no URL pattern matched
    if re.match(r"^[a-zA-Z0-9_-]+$", url_or_id):
        return url_or_id
    print(f"ERROR: Could not parse document ID from: {url_or_id}")
    sys.exit(1)


_HEADING_PREFIX = {
    "HEADING_1": "# ",
    "HEADING_2": "## ",
    "HEADING_3": "### ",
    "HEADING_4": "#### ",
    "HEADING_5": "##### ",
    "HEADING_6": "###### ",
}


def download_doc(creds, doc_id):
    """Download a Google Doc and return its content as markdown.

    Uses the Docs API to retrieve structured content, converting
    paragraph styles (headings) and text runs to markdown.

    Args:
        creds: Google OAuth2 credentials.
        doc_id: Google document ID.

    Returns:
        tuple: (title, markdown_text)
    """
    from googleapiclient.discovery import build

    service = build("docs", "v1", credentials=creds)
    doc = service.documents().get(documentId=doc_id).execute()
    title = doc.get("title", "Untitled")

    md_lines = []
    body = doc.get("body", {})
    content = body.get("content", [])

    for element in content:
        paragraph = element.get("paragraph")
        if not paragraph:
            continue

        style = paragraph.get("paragraphStyle", {})
        named_style = style.get("namedStyleType", "NORMAL_TEXT")
        prefix = _HEADING_PREFIX.get(named_style, "")

        line_parts = []
        for run in paragraph.get("elements", []):
            text_run = run.get("textRun")
            if not text_run:
                continue

            text = text_run.get("content", "")
            ts = text_run.get("textStyle", {})

            # Apply inline formatting
            stripped = text.rstrip("\n")
            if stripped:
                if ts.get("bold") and ts.get("italic"):
                    stripped = f"***{stripped}***"
                elif ts.get("bold"):
                    stripped = f"**{stripped}**"
                elif ts.get("italic"):
                    stripped = f"*{stripped}*"

                link = ts.get("link", {}).get("url")
                if link:
                    stripped = f"[{stripped}]({link})"

            line_parts.append(stripped)

        line_text = "".join(line_parts)
        if line_text or not prefix:
            md_lines.append(f"{prefix}{line_text}")

    markdown = "\n".join(md_lines)
    return title, markdown


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download a Google Doc as markdown"
    )
    parser.add_argument("url_or_id", help="Google Doc URL or document ID")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output file path (default: <title>.md in current directory)",
    )
    args = parser.parse_args()

    doc_id = extract_doc_id(args.url_or_id)
    creds = get_credentials()
    title, markdown = download_doc(creds, doc_id)

    if args.output:
        out_path = Path(args.output)
    else:
        safe_name = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
        out_path = Path(f"{safe_name}.md")

    out_path.write_text(markdown, encoding="utf-8")
    print(f"Saved: {out_path} ({len(markdown)} bytes)")


if __name__ == "__main__":
    main()
