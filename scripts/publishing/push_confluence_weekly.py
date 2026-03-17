#!/usr/bin/env python3
"""Push weekly summary updates to a Confluence page.

Generates a weekly program summary with calendar week info,
manages a rolling archive of past weeks, and updates the
designated Confluence page.

Usage:
    python push_confluence_weekly.py [--dry-run] [--date YYYY-MM-DD]

Environment:
    ATLASSIAN_DOMAIN               — Confluence domain
    ATLASSIAN_EMAIL                — Account email
    ATLASSIAN_API_TOKEN            — API token
    PAGES_CONFIG                   — Path to pages.json config file
    PAC_CONFLUENCE_WEEKLY_PAGE_ID  — Fallback page ID for weekly page
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
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: Environment variable {name} is not set.")
        sys.exit(1)
    return value


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


def get_page_id():
    """Get the weekly page ID from config or environment.

    Returns:
        str: Confluence page ID.
    """
    config_path = os.environ.get("PAGES_CONFIG")
    if config_path:
        path = Path(config_path)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if "weekly_page_id" in data:
                return data["weekly_page_id"]

    page_id = os.environ.get("PAC_CONFLUENCE_WEEKLY_PAGE_ID")
    if page_id:
        return page_id

    print("ERROR: No weekly page ID configured. Set PAGES_CONFIG or PAC_CONFLUENCE_WEEKLY_PAGE_ID.")
    sys.exit(1)


def get_auth():
    return (
        _validate_domain(_require_env("ATLASSIAN_DOMAIN")),
        _require_env("ATLASSIAN_EMAIL"),
        _require_env("ATLASSIAN_API_TOKEN"),
    )


# ---------------------------------------------------------------------------
# Confluence API
# ---------------------------------------------------------------------------

def get_page(page_id):
    """Fetch a Confluence page."""
    domain, email, token = get_auth()
    url = _confluence_api_url(domain, page_id)
    params = {"expand": "body.storage,version"}
    resp = requests.get(url, params=params, auth=(email, token), timeout=30)
    resp.raise_for_status()
    return resp.json()


def update_page(page_id, title, content, version_number):
    """Update a Confluence page."""
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
        url, json=payload, auth=(email, token),
        headers={"Content-Type": "application/json"}, timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def set_agent_marker(page_id):
    """Set PAC agent marker property on the page."""
    domain, email, token = get_auth()
    url = _confluence_api_url(domain, page_id, "/property/pac.agent_marker")
    marker = {
        "agent": "push_confluence_weekly",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
    }
    payload = {"key": "pac.agent_marker", "value": marker}
    resp = requests.put(
        url, json=payload, auth=(email, token),
        headers={"Content-Type": "application/json"}, timeout=30,
    )
    if resp.status_code == 404:
        post_url = _confluence_api_url(domain, page_id, "/property")
        requests.post(
            post_url, json=payload, auth=(email, token),
            headers={"Content-Type": "application/json"}, timeout=30,
        )


# ---------------------------------------------------------------------------
# Week calculations
# ---------------------------------------------------------------------------

def get_week_info(date_str):
    """Calculate calendar week info for a given date.

    Args:
        date_str: Date string in YYYY-MM-DD format.

    Returns:
        dict: {cw, year, week_start, week_end, date_range}
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    iso = dt.isocalendar()
    cw = iso[1]
    year = iso[0]

    # Monday of this week
    week_start = dt - timedelta(days=dt.weekday())
    week_end = week_start + timedelta(days=4)  # Friday

    return {
        "cw": cw,
        "year": year,
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_end": week_end.strftime("%Y-%m-%d"),
        "date_range": f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
        "label": f"CW{cw} {year}",
    }


# ---------------------------------------------------------------------------
# Content generators
# ---------------------------------------------------------------------------

def generate_weekly_summary(week_info, context=None):
    """Generate a weekly summary panel in Confluence format.

    Args:
        week_info: Dict from get_week_info().
        context: Optional dict with additional context (achievements, blockers, next_week).

    Returns:
        str: Confluence storage format HTML.
    """
    context = context or {}
    achievements = context.get("achievements", ["Weekly summary generated by automation"])
    blockers = context.get("blockers", [])
    next_week = context.get("next_week", [])

    html = (
        f'<ac:structured-macro ac:name="panel">'
        f'<ac:parameter ac:name="panelType">success</ac:parameter>'
        f'<ac:rich-text-body>'
        f'<h2>{week_info["label"]} - {week_info["date_range"]}</h2>'
    )

    # Achievements
    html += "<h3>Achievements</h3><ul>"
    for item in achievements:
        html += f"<li>{item}</li>"
    html += "</ul>"

    # Blockers
    if blockers:
        html += "<h3>Blockers</h3><ul>"
        for item in blockers:
            html += f"<li>{item}</li>"
        html += "</ul>"

    # Next week
    if next_week:
        html += "<h3>Next Week</h3><ul>"
        for item in next_week:
            html += f"<li>{item}</li>"
        html += "</ul>"

    html += "</ac:rich-text-body></ac:structured-macro>"
    return html


def count_weekly_panels(content):
    """Count the number of weekly panels in the page content.

    Args:
        content: Confluence page HTML content.

    Returns:
        int: Number of CW panels found.
    """
    return len(re.findall(r'<h2>CW\d+', content))


def archive_old_weeks(content, max_weeks=8):
    """Move old weekly panels into a collapsed archive section.

    Keeps the most recent max_weeks panels visible and archives
    older ones in an expand macro.

    Args:
        content: Current page HTML content.
        max_weeks: Maximum number of visible weekly panels.

    Returns:
        str: Updated content with old weeks archived.
    """
    # Find all CW panels
    panel_pattern = (
        r'(<ac:structured-macro ac:name="panel">.*?'
        r'<h2>(CW\d+ \d{4}).*?</ac:structured-macro>)'
    )
    panels = list(re.finditer(panel_pattern, content, re.DOTALL))

    if len(panels) <= max_weeks:
        return content

    # Sort by CW number (most recent first)
    def extract_cw(match):
        cw_match = re.search(r'CW(\d+) (\d{4})', match.group(2))
        if cw_match:
            return int(cw_match.group(2)) * 100 + int(cw_match.group(1))
        return 0

    panels.sort(key=extract_cw, reverse=True)

    # Archive older panels
    to_archive = panels[max_weeks:]
    if not to_archive:
        return content

    archive_html = (
        '<ac:structured-macro ac:name="expand">'
        '<ac:parameter ac:name="title">Previous Weeks</ac:parameter>'
        '<ac:rich-text-body>'
    )

    for panel in to_archive:
        archive_html += panel.group(1)
        content = content.replace(panel.group(1), "")

    archive_html += "</ac:rich-text-body></ac:structured-macro>"

    # Remove existing archive if present, then append new one
    content = re.sub(
        r'<ac:structured-macro ac:name="expand">.*?Previous Weeks.*?</ac:structured-macro>',
        '',
        content,
        flags=re.DOTALL,
    )
    content += archive_html

    return content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def push_weekly_update(week_info, context=None, dry_run=False):
    """Build and push the weekly update to Confluence.

    Args:
        week_info: Dict from get_week_info().
        context: Optional context dict for the summary.
        dry_run: If True, print output without updating.

    Returns:
        str: Final page content.
    """
    page_id = get_page_id()
    print(f"Updating weekly page (ID: {page_id}) for {week_info['label']}")

    page = get_page(page_id)
    title = page["title"]
    version = page["version"]["number"]
    current_content = page["body"]["storage"]["value"]

    # Check if this week's panel already exists
    if week_info["label"] in current_content:
        print(f"Panel for {week_info['label']} already exists. Replacing...")
        # Remove existing panel for this week
        pattern = (
            r'<ac:structured-macro ac:name="panel">.*?'
            + re.escape(week_info["label"])
            + r'.*?</ac:structured-macro>'
        )
        current_content = re.sub(pattern, '', current_content, flags=re.DOTALL)

    # Generate new weekly panel
    new_panel = generate_weekly_summary(week_info, context)

    # Insert at top
    updated_content = new_panel + current_content

    # Archive old weeks
    updated_content = archive_old_weeks(updated_content)

    if dry_run:
        print("\n--- DRY RUN OUTPUT ---")
        print(updated_content[:2000])
        print(f"--- (total: {len(updated_content)} chars) ---")
        return updated_content

    update_page(page_id, title, updated_content, version)
    set_agent_marker(page_id)

    domain = _require_env("ATLASSIAN_DOMAIN")
    print(f"Updated: https://{domain}/wiki/pages/viewpage.action?pageId={quote(str(page_id), safe='')}")
    return updated_content


def load_weekly_context():
    """Load weekly context from a local JSON file if available.

    Returns:
        dict or None: Context with achievements, blockers, next_week.
    """
    context_path = Path("weekly_context.json")
    if context_path.exists():
        try:
            return json.loads(context_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Push weekly summary to Confluence"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate content without updating Confluence",
    )
    parser.add_argument(
        "--date",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        help="Date to calculate week from (default: today)",
    )
    args = parser.parse_args()

    week_info = get_week_info(args.date)
    context = load_weekly_context()
    push_weekly_update(week_info, context, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
