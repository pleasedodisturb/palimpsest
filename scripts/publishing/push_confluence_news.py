#!/usr/bin/env python3
"""Push daily news/updates to a Confluence page.

Manages a rolling updates page with daily panels, status sections,
and weekly archival of old content.

Usage:
    python push_confluence_news.py [--dry-run] [--date YYYY-MM-DD]

Environment:
    ATLASSIAN_DOMAIN               — Confluence domain
    ATLASSIAN_EMAIL                — Account email
    ATLASSIAN_API_TOKEN            — API token
    PAGES_CONFIG                   — Path to pages.json config file
    PAC_CONFLUENCE_UPDATES_PAGE_ID — Fallback page ID for updates page
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from urllib.parse import quote


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _require_env(name):
    """Get a required environment variable or exit."""
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: Environment variable {name} is not set.")
        sys.exit(1)
    return value


def get_page_config():
    """Load page IDs from config file or environment.

    Returns:
        dict: Configuration with 'updates_page_id' key.
    """
    config_path = os.environ.get("PAGES_CONFIG")
    if config_path:
        path = Path(config_path)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data

    # Fallback to direct env var
    page_id = os.environ.get("PAC_CONFLUENCE_UPDATES_PAGE_ID")
    if page_id:
        return {"updates_page_id": page_id}

    print("ERROR: No page configuration found. Set PAGES_CONFIG or PAC_CONFLUENCE_UPDATES_PAGE_ID.")
    sys.exit(1)


def _validate_domain(domain):
    """Validate that domain is a clean hostname with no path separators."""
    if any(c in domain for c in "/?#\\ @:"):
        print(f"ERROR: ATLASSIAN_DOMAIN contains invalid characters: {domain!r}")
        sys.exit(1)
    return domain


def _confluence_api_url(domain, page_id, suffix=""):
    """Build a Confluence REST API URL with sanitized path segments."""
    safe_domain = _validate_domain(domain)
    safe_id = quote(str(page_id), safe="")
    base = f"https://{safe_domain}/wiki/rest/api/content/{safe_id}"
    return f"{base}{suffix}" if suffix else base


def get_auth():
    """Return (domain, email, token) tuple."""
    return (
        _validate_domain(_require_env("ATLASSIAN_DOMAIN")),
        _require_env("ATLASSIAN_EMAIL"),
        _require_env("ATLASSIAN_API_TOKEN"),
    )


# ---------------------------------------------------------------------------
# Confluence API helpers
# ---------------------------------------------------------------------------

def get_page(page_id):
    """Fetch a Confluence page by ID.

    Args:
        page_id: Confluence page ID.

    Returns:
        dict: Page data with title, version, body.
    """
    domain, email, token = get_auth()
    url = _confluence_api_url(domain, page_id)
    params = {"expand": "body.storage,version,metadata.properties"}

    resp = requests.get(url, params=params, auth=(email, token), timeout=30)
    resp.raise_for_status()
    return resp.json()


def update_page(page_id, title, content, version_number):
    """Update a Confluence page with new content.

    Increments the version number automatically.

    Args:
        page_id: Confluence page ID.
        title: Page title.
        content: Confluence storage format HTML.
        version_number: Current version number (will be incremented).

    Returns:
        dict: Updated page data.
    """
    domain, email, token = get_auth()
    url = _confluence_api_url(domain, page_id)

    payload = {
        "id": str(page_id),
        "type": "page",
        "title": title,
        "version": {"number": version_number + 1},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage",
            }
        },
    }

    resp = requests.put(
        url,
        json=payload,
        auth=(email, token),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def set_agent_marker(page_id):
    """Set the pac.agent_marker property on a Confluence page.

    Args:
        page_id: Confluence page ID.
    """
    domain, email, token = get_auth()
    url = _confluence_api_url(domain, page_id, "/property/pac.agent_marker")

    marker = {
        "agent": "push_confluence_news",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
    }

    # Try update first, then create
    payload = {"key": "pac.agent_marker", "value": marker}

    resp = requests.put(
        url,
        json=payload,
        auth=(email, token),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code == 404:
        post_url = _confluence_api_url(domain, page_id, "/property")
        requests.post(
            post_url,
            json=payload,
            auth=(email, token),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )


# ---------------------------------------------------------------------------
# Content generators
# ---------------------------------------------------------------------------

def generate_daily_panel(date, items, highlight=None):
    """Generate a Confluence panel for a daily update.

    Args:
        date: Date string (YYYY-MM-DD).
        items: List of update item strings.
        highlight: Optional highlight text for the panel header.

    Returns:
        str: Confluence storage format HTML for the panel.
    """
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
    panel_type = "info"

    header = f"<h3>{formatted_date}</h3>"
    if highlight:
        header += f"<p><strong>{highlight}</strong></p>"

    body_items = ""
    for item in items:
        body_items += f"<li>{item}</li>"

    panel = (
        f'<ac:structured-macro ac:name="panel">'
        f'<ac:parameter ac:name="panelType">{panel_type}</ac:parameter>'
        f'<ac:rich-text-body>'
        f'{header}'
        f'<ul>{body_items}</ul>'
        f'</ac:rich-text-body>'
        f'</ac:structured-macro>'
    )
    return panel


def generate_current_status_section(date, jira_data=None):
    """Generate a status summary section.

    Args:
        date: Current date string.
        jira_data: Optional dict with Jira project metrics.

    Returns:
        str: Confluence storage format HTML.
    """
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
    html = f"<h2>Current Status - {formatted_date}</h2>"

    if jira_data:
        html += "<table><tbody>"
        html += "<tr><th>Metric</th><th>Value</th></tr>"

        for key, value in jira_data.items():
            label = key.replace("_", " ").title()
            html += f"<tr><td>{label}</td><td>{value}</td></tr>"

        html += "</tbody></table>"
    else:
        html += "<p>No Jira data available for status update.</p>"

    return html


def manage_weekly_archive(content, current_date):
    """Archive panels older than 7 days into a collapsed section.

    Moves daily panels from the main body into an expandable archive
    section to keep the page manageable.

    Args:
        content: Current page HTML content.
        current_date: Current date string (YYYY-MM-DD).

    Returns:
        str: Updated content with old panels archived.
    """
    current = datetime.strptime(current_date, "%Y-%m-%d")
    cutoff = current - timedelta(days=7)

    # Find all date headers in panels
    date_pattern = r'<h3>([A-Z][a-z]+ \d{1,2}, \d{4})</h3>'
    matches = list(re.finditer(date_pattern, content))

    panels_to_archive = []
    for match in matches:
        try:
            panel_date = datetime.strptime(match.group(1), "%B %d, %Y")
            if panel_date < cutoff:
                panels_to_archive.append(match.group(1))
        except ValueError:
            continue

    if not panels_to_archive:
        return content

    # Wrap old panels in an expand macro
    archive_section = (
        '<ac:structured-macro ac:name="expand">'
        '<ac:parameter ac:name="title">Archived Updates</ac:parameter>'
        '<ac:rich-text-body>'
    )

    for date_str in panels_to_archive:
        # Find and extract the panel containing this date
        panel_pattern = (
            r'(<ac:structured-macro ac:name="panel">.*?'
            + re.escape(date_str)
            + r'.*?</ac:structured-macro>)'
        )
        panel_match = re.search(panel_pattern, content, re.DOTALL)
        if panel_match:
            archive_section += panel_match.group(1)
            content = content.replace(panel_match.group(1), "")

    archive_section += "</ac:rich-text-body></ac:structured-macro>"

    # Append archive section at the end
    content += archive_section
    return content


# ---------------------------------------------------------------------------
# Main rebuild
# ---------------------------------------------------------------------------

def rebuild_updates_page(date, jira_data=None, dry_run=False):
    """Rebuild the updates page with current data.

    Fetches the existing page, generates new daily content,
    manages archives, and updates the page.

    Args:
        date: Date string (YYYY-MM-DD).
        jira_data: Optional dict with Jira metrics.
        dry_run: If True, print output but do not update Confluence.

    Returns:
        str: Updated page content.
    """
    config = get_page_config()
    page_id = config["updates_page_id"]

    print(f"Rebuilding updates page (ID: {page_id}) for {date}")

    # Fetch current page
    page = get_page(page_id)
    title = page["title"]
    version = page["version"]["number"]
    current_content = page["body"]["storage"]["value"]

    # Generate new daily panel
    items = [
        f"Daily update generated for {date}",
        "Pipeline status: see current status section below",
    ]
    if jira_data:
        total = sum(v for v in jira_data.values() if isinstance(v, (int, float)))
        items.append(f"Jira metrics updated ({total} total items tracked)")

    new_panel = generate_daily_panel(date, items)

    # Generate status section
    status_section = generate_current_status_section(date, jira_data)

    # Insert new panel at top, status section after
    # Remove old status section if present
    current_content = re.sub(
        r'<h2>Current Status.*?(?=<ac:structured-macro|<h[12]|$)',
        '',
        current_content,
        flags=re.DOTALL,
    )

    updated_content = status_section + new_panel + current_content

    # Archive old panels
    updated_content = manage_weekly_archive(updated_content, date)

    if dry_run:
        print("\n--- DRY RUN OUTPUT ---")
        print(updated_content[:2000])
        print(f"--- (total: {len(updated_content)} chars) ---")
        return updated_content

    # Update page
    update_page(page_id, title, updated_content, version)
    set_agent_marker(page_id)
    domain = get_auth()[0]
    print(f"Page updated: https://{domain}/wiki/pages/viewpage.action?pageId={quote(str(page_id), safe='')}")

    return updated_content


# ---------------------------------------------------------------------------
# Data loaders (optional integrations)
# ---------------------------------------------------------------------------

def load_jira_data():
    """Load Jira metrics from a local cache file or return None.

    Returns:
        dict or None: Jira metrics if available.
    """
    cache_path = Path("jira_metrics.json")
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Push daily updates to Confluence"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate content without updating Confluence",
    )
    parser.add_argument(
        "--date",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        help="Date for the update (default: today)",
    )
    args = parser.parse_args()

    jira_data = load_jira_data()
    rebuild_updates_page(args.date, jira_data, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
