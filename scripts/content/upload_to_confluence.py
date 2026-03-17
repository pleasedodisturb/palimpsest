#!/usr/bin/env python3
"""Upload markdown content to Confluence as a new page.

Converts markdown to Confluence storage format (XHTML) and creates
or updates pages via the Confluence REST API.

Usage:
    python upload_to_confluence.py <space_key> <markdown_file> <title> [parent_id]

Environment (required, no defaults):
    ATLASSIAN_EMAIL      -- Atlassian account email
    ATLASSIAN_API_TOKEN  -- API token for authentication
    ATLASSIAN_DOMAIN     -- Confluence domain (e.g., mycompany.atlassian.net)
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
# Shared regex patterns (constants to avoid duplication)
# ---------------------------------------------------------------------------

_TABLE_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
_CHECKBOX_RE = re.compile(r"^[-*]\s+\[([ xX])\]\s+(.*)")
_BULLET_RE = re.compile(r"^[-*+]\s+")
_NUMBERED_RE = re.compile(r"^\d+\.\s+")
_HORIZONTAL_RULE_RE = re.compile(r"^[-*_]{3,}\s*$")
_CODE_FENCE = "```"


# ---------------------------------------------------------------------------
# Markdown -> Confluence XHTML
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
        if _TABLE_SEPARATOR_RE.match(stripped):
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


def _convert_code_block(lines, i):
    """Parse a fenced code block and return Confluence macro HTML.

    Returns:
        tuple: (html_string, new_line_index)
    """
    lang = lines[i].strip().lstrip("`").strip() or "none"
    code_lines = []
    i += 1
    while i < len(lines) and not lines[i].strip().startswith(_CODE_FENCE):
        code_lines.append(lines[i])
        i += 1
    i += 1  # skip closing fence
    code = "\n".join(code_lines)
    html = (
        f'<ac:structured-macro ac:name="code">'
        f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
        f"<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>"
        f"</ac:structured-macro>"
    )
    return html, i


def _convert_table_block(lines, i):
    """Parse consecutive table lines and return Confluence table HTML.

    Returns:
        tuple: (html_string, new_line_index)
    """
    table_lines = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        table_lines.append(lines[i])
        i += 1
    return convert_table(table_lines), i


def _collect_list_items(lines, i, pattern):
    """Collect consecutive list items matching a regex pattern.

    Returns:
        tuple: (list_of_item_texts, new_line_index)
    """
    items = []
    while i < len(lines) and pattern.match(lines[i]):
        items.append(_inline(pattern.sub("", lines[i])))
        i += 1
    return items, i


def _convert_heading(line):
    """Convert a heading line to Confluence HTML, or return None."""
    heading_match = _HEADING_RE.match(line)
    if not heading_match:
        return None
    level = len(heading_match.group(1))
    text = _inline(heading_match.group(2))
    return f"<h{level}>{text}</h{level}>"


def _convert_checkbox(line):
    """Convert a checkbox line to Confluence HTML, or return None."""
    checkbox_match = _CHECKBOX_RE.match(line)
    if not checkbox_match:
        return None
    checked = checkbox_match.group(1).lower() == "x"
    text = _inline(checkbox_match.group(2))
    icon = "(/)" if checked else "(x)"
    return f"<p>{icon} {text}</p>"


def _convert_list_block(lines, i, pattern, tag):
    """Convert a bullet or numbered list block to Confluence HTML.

    Returns:
        tuple: (html_string, new_line_index)
    """
    items, i = _collect_list_items(lines, i, pattern)
    html = f"<{tag}>" + "".join(f"<li>{it}</li>" for it in items) + f"</{tag}>"
    return html, i


def _convert_single_line(line):
    """Try to convert a single-line block element (blockquote, hr, paragraph).

    Returns:
        str or None: HTML string, or None if the line is empty.
    """
    stripped = line.strip()
    if stripped.startswith(">"):
        text = _inline(re.sub(r"^>\s?", "", stripped))
        return f"<blockquote><p>{text}</p></blockquote>"
    if _HORIZONTAL_RULE_RE.match(stripped):
        return "<hr/>"
    if stripped:
        return f"<p>{_inline(stripped)}</p>"
    return None


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

        # Multi-line blocks (code, table, lists) advance i themselves
        if line.strip().startswith(_CODE_FENCE):
            html, i = _convert_code_block(lines, i)
            html_parts.append(html)
            continue

        if line.strip().startswith("|"):
            html, i = _convert_table_block(lines, i)
            html_parts.append(html)
            continue

        if _BULLET_RE.match(line):
            html, i = _convert_list_block(lines, i, _BULLET_RE, "ul")
            html_parts.append(html)
            continue

        if _NUMBERED_RE.match(line):
            html, i = _convert_list_block(lines, i, _NUMBERED_RE, "ol")
            html_parts.append(html)
            continue

        # Single-line block elements
        heading = _convert_heading(line)
        if heading:
            html_parts.append(heading)
            i += 1
            continue

        checkbox = _convert_checkbox(line)
        if checkbox:
            html_parts.append(checkbox)
            i += 1
            continue

        result = _convert_single_line(line)
        if result:
            html_parts.append(result)

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
