#!/usr/bin/env python3
"""Build a unified document registry from multiple sources.

Collects document metadata from Google Drive, Confluence, Jira, and local
link indexes, then produces a deduplicated markdown registry.

Usage:
    python build_document_registry.py --config registry_config.json --output registry.md

Config file format (JSON):
    {
        "sources": {
            "drive_folders": ["folder_id_1", "folder_id_2"],
            "drive_keywords": ["project plan", "design doc"],
            "confluence": {
                "space_keys": ["PROJ"],
                "labels": ["architecture"]
            },
            "jira": {
                "projects": ["PROJ"],
                "attachment_types": [".pdf", ".docx"]
            },
            "local_link_index": "path/to/link_index.json"
        },
        "classification": {
            "type_rules": {
                "design": ["design", "architecture", "rfc"],
                "plan": ["plan", "roadmap", "timeline"],
                "report": ["report", "summary", "review"],
                "runbook": ["runbook", "playbook", "how-to"]
            },
            "status_rules": {
                "draft": ["draft", "wip", "work in progress"],
                "review": ["review", "pending"],
                "final": ["final", "approved", "published"]
            },
            "importance_rules": {
                "critical": ["critical", "must-read", "key"],
                "high": ["important", "high-priority"],
                "normal": []
            }
        },
        "output": {
            "group_by": "type",
            "include_metadata": true
        }
    }
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = SCRIPT_DIR / "token_docs.json"
CREDENTIALS_PATH = SCRIPT_DIR / "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]


# ---------------------------------------------------------------------------
# Auth (reusable)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Source collectors
# ---------------------------------------------------------------------------

def collect_drive_folder(creds, folder_id):
    """List documents inside a Google Drive folder.

    Returns:
        list[dict]: Registry entries with title, url, source, modified.
    """
    from googleapiclient.discovery import build

    service = build("drive", "v3", credentials=creds)
    entries = []
    page_token = None

    while True:
        resp = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
            pageSize=100,
            pageToken=page_token,
        ).execute()

        for f in resp.get("files", []):
            entries.append({
                "title": f["name"],
                "url": f.get("webViewLink", f"https://drive.google.com/file/d/{f['id']}"),
                "source": "google_drive",
                "modified": f.get("modifiedTime", ""),
                "mime_type": f.get("mimeType", ""),
            })

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return entries


def collect_drive_keyword(creds, keyword):
    """Search Google Drive by keyword.

    Returns:
        list[dict]: Registry entries matching the keyword.
    """
    from googleapiclient.discovery import build

    service = build("drive", "v3", credentials=creds)
    entries = []

    resp = service.files().list(
        q=f"fullText contains '{keyword}' and trashed = false",
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        pageSize=50,
    ).execute()

    for f in resp.get("files", []):
        entries.append({
            "title": f["name"],
            "url": f.get("webViewLink", f"https://drive.google.com/file/d/{f['id']}"),
            "source": "google_drive",
            "modified": f.get("modifiedTime", ""),
            "mime_type": f.get("mimeType", ""),
            "search_keyword": keyword,
        })

    return entries


def _get_atlassian_credentials():
    """Return (domain, email, token) from environment, or None if missing."""
    domain = os.environ.get("ATLASSIAN_DOMAIN")
    email = os.environ.get("ATLASSIAN_EMAIL")
    token = os.environ.get("ATLASSIAN_API_TOKEN")
    if not all([domain, email, token]):
        return None
    return domain, email, token


def collect_confluence(space_keys, labels=None):
    """Collect pages from Confluence spaces.

    Returns:
        list[dict]: Registry entries from Confluence.
    """
    import requests as req

    creds = _get_atlassian_credentials()
    if creds is None:
        print("WARNING: Confluence credentials not set, skipping Confluence source.")
        return []

    domain, email, token = creds
    entries = []
    for space_key in space_keys:
        cql = f'space = "{space_key}"'
        if labels:
            label_filter = " OR ".join(f'label = "{lb}"' for lb in labels)
            cql += f" AND ({label_filter})"

        url = f"https://{domain}/wiki/rest/api/content/search"
        params = {"cql": cql, "limit": 100}

        try:
            resp = req.get(url, params=params, auth=(email, token), timeout=30)
            resp.raise_for_status()
        except req.RequestException as e:
            print(f"WARNING: Confluence search failed for {space_key}: {e}")
            continue

        for result in resp.json().get("results", []):
            page_url = f"https://{domain}/wiki{result['_links'].get('webui', '')}"
            entries.append({
                "title": result.get("title", ""),
                "url": page_url,
                "source": "confluence",
                "space": space_key,
                "modified": result.get("history", {}).get("lastUpdated", {}).get("when", ""),
            })

    return entries


def _should_include_attachment(filename, attachment_types):
    """Check whether a Jira attachment matches the allowed types."""
    if not attachment_types:
        return True
    ext = Path(filename).suffix.lower()
    return ext in attachment_types


def _build_jira_entry(issue_key, att, project):
    """Build a registry entry dict from a Jira attachment."""
    return {
        "title": f"{issue_key}: {att.get('filename', '')}",
        "url": att.get("content", ""),
        "source": "jira",
        "project": project,
        "issue": issue_key,
        "modified": att.get("created", ""),
    }


def _fetch_jira_project(req, domain, email, token, project):
    """Fetch issues with attachments for a single Jira project."""
    url = f"https://{domain}/rest/api/3/search"
    params = {
        "jql": f"project = {project} AND attachments IS NOT EMPTY",
        "maxResults": 50,
        "fields": "summary,attachment",
    }
    try:
        resp = req.get(url, params=params, auth=(email, token), timeout=30)
        resp.raise_for_status()
    except req.RequestException as e:
        print(f"WARNING: Jira search failed for {project}: {e}")
        return []
    return resp.json().get("issues", [])


def collect_jira(projects, attachment_types=None):
    """Collect documents attached to Jira issues.

    Returns:
        list[dict]: Registry entries from Jira attachments.
    """
    import requests as req

    creds = _get_atlassian_credentials()
    if creds is None:
        print("WARNING: Jira credentials not set, skipping Jira source.")
        return []

    domain, email, token = creds
    entries = []
    attachment_types = attachment_types or []

    for project in projects:
        issues = _fetch_jira_project(req, domain, email, token, project)
        for issue in issues:
            issue_key = issue["key"]
            for att in issue["fields"].get("attachment", []):
                if not _should_include_attachment(att.get("filename", ""), attachment_types):
                    continue
                entries.append(_build_jira_entry(issue_key, att, project))

    return entries


def collect_local_link_index(index_path):
    """Load entries from a local link index JSON file.

    Expected format: list of objects with at least "title" and "url".

    Returns:
        list[dict]: Registry entries from the local index.
    """
    path = Path(index_path)
    if not path.exists():
        print(f"WARNING: Link index not found: {index_path}")
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    entries = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "url" in item:
                item.setdefault("source", "local_index")
                item.setdefault("title", item["url"])
                entries.append(item)
    elif isinstance(data, dict):
        for url, meta in data.items():
            entry = {"url": url, "source": "local_index"}
            if isinstance(meta, str):
                entry["title"] = meta
            elif isinstance(meta, dict):
                entry.update(meta)
                entry.setdefault("title", url)
            entries.append(entry)

    return entries


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_doc_type(entry, rules):
    """Classify document type based on title/keywords.

    Args:
        entry: Document entry dict.
        rules: Dict mapping type name to list of keywords.

    Returns:
        str: Matched type or "other".
    """
    title = entry.get("title", "").lower()
    for doc_type, keywords in rules.items():
        for kw in keywords:
            if kw.lower() in title:
                return doc_type
    return "other"


def classify_status(entry, rules):
    """Classify document status based on title/keywords.

    Args:
        entry: Document entry dict.
        rules: Dict mapping status to list of keywords.

    Returns:
        str: Matched status or "unknown".
    """
    title = entry.get("title", "").lower()
    for status, keywords in rules.items():
        for kw in keywords:
            if kw.lower() in title:
                return status
    return "unknown"


def classify_importance(entry, rules):
    """Classify document importance based on title/keywords.

    Args:
        entry: Document entry dict.
        rules: Dict mapping importance to list of keywords.

    Returns:
        str: Matched importance or "normal".
    """
    title = entry.get("title", "").lower()
    for importance, keywords in rules.items():
        if not keywords:
            continue
        for kw in keywords:
            if kw.lower() in title:
                return importance
    return "normal"


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def canonicalize_url(url):
    """Normalize a URL for deduplication.

    Strips trailing slashes, fragments, and query params like utm_*.

    Args:
        url: Raw URL string.

    Returns:
        str: Canonical URL.
    """
    parsed = urlparse(url)
    # Remove fragment
    path = parsed.path.rstrip("/")
    # Reconstruct without fragment and with cleaned path
    canonical = f"{parsed.scheme}://{parsed.netloc}{path}"
    return canonical.lower()


def dedupe_entries(entries):
    """Remove duplicate entries based on canonical URL.

    Keeps the first occurrence (which should be from the highest-priority source).

    Args:
        entries: List of entry dicts.

    Returns:
        list[dict]: Deduplicated entries.
    """
    seen = set()
    unique = []
    for entry in entries:
        url = entry.get("url", "")
        canon = canonicalize_url(url)
        url_hash = hashlib.md5(canon.encode()).hexdigest()
        if url_hash not in seen:
            seen.add(url_hash)
            unique.append(entry)
    return unique


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _format_entry_table_row(entry):
    """Format a single entry as a markdown table row."""
    title = entry.get("title", "Untitled")
    url = entry.get("url", "")
    source = entry.get("source", "")
    status = entry.get("status", "unknown")
    importance = entry.get("importance", "normal")
    modified = entry.get("modified", "")[:10]
    link = f"[{title}]({url})" if url else title
    return f"| {link} | {source} | {status} | {importance} | {modified} |"


def _format_entry_list_item(entry):
    """Format a single entry as a markdown list item."""
    title = entry.get("title", "Untitled")
    url = entry.get("url", "")
    return f"- [{title}]({url})" if url else f"- {title}"


def _render_group(lines, group_entries, include_metadata):
    """Render a group of entries as either a table or a list."""
    sorted_entries = sorted(group_entries, key=lambda e: e.get("title", ""))
    if include_metadata:
        lines.append("| Title | Source | Status | Importance | Modified |")
        lines.append("|-------|--------|--------|------------|----------|")
        for entry in sorted_entries:
            lines.append(_format_entry_table_row(entry))
    else:
        for entry in sorted_entries:
            lines.append(_format_entry_list_item(entry))


def generate_markdown(entries, config):
    """Generate a markdown document registry from classified entries.

    Args:
        entries: List of classified entry dicts.
        config: Output configuration dict.

    Returns:
        str: Markdown text.
    """
    group_by = config.get("group_by", "type")
    include_metadata = config.get("include_metadata", True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Document Registry",
        "",
        f"Generated: {now}",
        f"Total documents: {len(entries)}",
        "",
    ]

    # Group entries
    groups = {}
    for entry in entries:
        key = entry.get(group_by, "other")
        groups.setdefault(key, []).append(entry)

    for group_name in sorted(groups.keys()):
        lines.append(f"## {group_name.replace('_', ' ').title()}")
        lines.append("")
        _render_group(lines, groups[group_name], include_metadata)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def build_registry(config):
    """Build the full document registry from config.

    Args:
        config: Parsed config dict (see module docstring for format).

    Returns:
        str: Markdown registry content.
    """
    sources = config.get("sources", {})
    classification = config.get("classification", {})
    output_config = config.get("output", {})

    all_entries = []

    # Google Drive folders
    drive_folders = sources.get("drive_folders", [])
    drive_keywords = sources.get("drive_keywords", [])

    if drive_folders or drive_keywords:
        try:
            creds = get_credentials()
            for folder_id in drive_folders:
                print(f"Collecting from Drive folder: {folder_id}")
                all_entries.extend(collect_drive_folder(creds, folder_id))

            for keyword in drive_keywords:
                print(f"Searching Drive for: {keyword}")
                all_entries.extend(collect_drive_keyword(creds, keyword))
        except Exception as e:
            print(f"WARNING: Google Drive collection failed: {e}")

    # Confluence
    conf_config = sources.get("confluence", {})
    if conf_config.get("space_keys"):
        print("Collecting from Confluence...")
        all_entries.extend(
            collect_confluence(
                conf_config["space_keys"],
                conf_config.get("labels"),
            )
        )

    # Jira
    jira_config = sources.get("jira", {})
    if jira_config.get("projects"):
        print("Collecting from Jira...")
        all_entries.extend(
            collect_jira(
                jira_config["projects"],
                jira_config.get("attachment_types"),
            )
        )

    # Local link index
    local_index = sources.get("local_link_index")
    if local_index:
        print(f"Loading local index: {local_index}")
        all_entries.extend(collect_local_link_index(local_index))

    print(f"Collected {len(all_entries)} entries before dedup")

    # Deduplicate
    all_entries = dedupe_entries(all_entries)
    print(f"After dedup: {len(all_entries)} entries")

    # Classify
    type_rules = classification.get("type_rules", {})
    status_rules = classification.get("status_rules", {})
    importance_rules = classification.get("importance_rules", {})

    for entry in all_entries:
        entry["type"] = classify_doc_type(entry, type_rules)
        entry["status"] = classify_status(entry, status_rules)
        entry["importance"] = classify_importance(entry, importance_rules)

    # Generate output
    return generate_markdown(all_entries, output_config)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build a multi-source document registry"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to JSON config file",
    )
    parser.add_argument(
        "--output",
        default="document_registry.md",
        help="Output markdown file path",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: Config file not found: {args.config}")
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    markdown = build_registry(config)

    out_path = Path(args.output)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"Registry saved to {out_path}")


if __name__ == "__main__":
    main()
