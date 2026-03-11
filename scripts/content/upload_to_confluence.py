#!/usr/bin/env python3
"""Upload markdown content to Confluence as a new page.

Converts markdown to Confluence storage format (XHTML) and creates
or updates pages via the Confluence REST API.

Usage:
    python upload_to_confluence.py <space_key> <markdown_file> <title> [parent_id]

Environment (required, no defaults):
    ATLASSIAN_EMAIL      — Atlassian account email
    ATLASSIAN_API_TOKEN  — API token for authentication
    ATLASSIAN_DOMAIN     — Confluence domain (e.g., mycompany.atlassian.net)
"""

import argparse
import os
import re
import sys
from pathlib import Path

import requests


def _require_env(name):
    """Get a required environment variable or exit."""
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: Environment variable {name} is not set.")
        sys.exit(1)
    return value


def _get_auth():
    """Return (domain, email, token) from environment."""
    return (
        _require_env("ATLASSIAN_DOMAIN"),
        _require_env("ATLASSIAN_EMAIL"),
        _require_env("ATLASSIAN_API_TOKEN"),
    )


# ---------------------------------------------------------------------------
# Markdown → Confluence XHTML
# ---------------------------------------------------------------------------

def convert_table(lines):
    """Convert markdown table lines to Confluence XHTML table.

    Args:
        lines: List of markdown table row strings (with leading |).

    Returns:
        str: Confluence storage format table HTML.
    """
    rows = []
    for line in lines:
        stripped = line.strip()
        # Skip separator rows
        if re.match(r"^\|[\s\-:|]+\|$", stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return ""

    html = "<table><tbody>"
    for idx, row in enumerate(rows):
        tag = "th" if idx == 0 else "td"
        html += "<tr>"
        for cell in row:
            html += f"<{tag}>{cell}</{tag}>"
        html += "</tr>"
    html += "</tbody></table>"
    return html


def markdown_to_confluence(markdown_text):
    """Convert markdown text to Confluence storage format (XHTML).

    Supports: headers, bold, italic, inline code, links, tables,
    bullet lists, numbered lists, blockquotes, checkboxes, code blocks.

    Args:
        markdown_text: Raw markdown string.

    Returns:
        str: Confluence storage format XHTML.
    """
    lines = markdown_text.split("\n")
    html_parts = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code block
        if line.strip().startswith("```"):
            lang = line.strip().lstrip("`").strip() or "none"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing
            code = "\n".join(code_lines)
            html_parts.append(
                f'<ac:structured-macro ac:name="code">'
                f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
                f"<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>"
                f"</ac:structured-macro>"
            )
            continue

        # Table
        if line.strip().startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            html_parts.append(convert_table(table_lines))
            continue

        # Heading
        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if heading_match:
            level = len(heading_match.group(1))
            text = _inline(heading_match.group(2))
            html_parts.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        # Checkbox
        checkbox_match = re.match(r"^[-*]\s+\[([ xX])\]\s+(.*)", line)
        if checkbox_match:
            checked = checkbox_match.group(1).lower() == "x"
            text = _inline(checkbox_match.group(2))
            icon = "(/)" if checked else "(x)"
            html_parts.append(f"<p>{icon} {text}</p>")
            i += 1
            continue

        # Bullet list
        if re.match(r"^[-*+]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                items.append(_inline(re.sub(r"^[-*+]\s+", "", lines[i])))
                i += 1
            html_parts.append(
                "<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>"
            )
            continue

        # Numbered list
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(_inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            html_parts.append(
                "<ol>" + "".join(f"<li>{it}</li>" for it in items) + "</ol>"
            )
            continue

        # Blockquote
        if line.strip().startswith(">"):
            text = _inline(re.sub(r"^>\s?", "", line.strip()))
            html_parts.append(f"<blockquote><p>{text}</p></blockquote>")
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^[-*_]{3,}\s*$", line.strip()):
            html_parts.append("<hr/>")
            i += 1
            continue

        # Paragraph
        stripped = line.strip()
        if stripped:
            html_parts.append(f"<p>{_inline(stripped)}</p>")

        i += 1

    return "\n".join(html_parts)


def _inline(text):
    """Apply inline formatting: bold, italic, code, links."""
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


# ---------------------------------------------------------------------------
# Confluence API
# ---------------------------------------------------------------------------

def create_page(space_key, title, content, parent_id=None):
    """Create a new Confluence page.

    Args:
        space_key: Confluence space key.
        title: Page title.
        content: Confluence storage format HTML.
        parent_id: Optional parent page ID.

    Returns:
        dict: API response with page id and URL.
    """
    domain, email, token = _get_auth()
    url = f"https://{domain}/wiki/rest/api/content"

    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage",
            }
        },
    }

    if parent_id:
        payload["ancestors"] = [{"id": str(parent_id)}]

    resp = requests.post(
        url,
        json=payload,
        auth=(email, token),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    page_url = f"https://{domain}/wiki{data['_links']['webui']}"
    print(f"Created page: {page_url}")
    return data


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Upload markdown to Confluence"
    )
    parser.add_argument("space_key", help="Confluence space key")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument("title", help="Page title")
    parser.add_argument("parent_id", nargs="?", default=None, help="Parent page ID")
    args = parser.parse_args()

    md_path = Path(args.file)
    if not md_path.exists():
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    markdown_text = md_path.read_text(encoding="utf-8")
    html_content = markdown_to_confluence(markdown_text)
    create_page(args.space_key, args.title, html_content, args.parent_id)


if __name__ == "__main__":
    main()
