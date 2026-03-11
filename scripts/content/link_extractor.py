#!/usr/bin/env python3
"""Extract, categorize, and index links from documents.

Scans files in multiple formats (markdown, PDF, JSON, plain text) and
produces a categorized link index with deduplication.

Usage:
    python link_extractor.py <directory> [--output-dir OUTPUT_DIR]

Supported link categories:
    Confluence, Jira, Google (Docs/Sheets/Drive), GitHub, Slack,
    Figma, Notion, Other
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Link categorization
# ---------------------------------------------------------------------------

_CATEGORY_PATTERNS = [
    ("confluence", [r"atlassian\.net/wiki", r"confluence\."]),
    ("jira", [r"atlassian\.net/browse", r"atlassian\.net/rest/api", r"jira\."]),
    ("google_docs", [r"docs\.google\.com/document"]),
    ("google_sheets", [r"docs\.google\.com/spreadsheets"]),
    ("google_drive", [r"drive\.google\.com", r"docs\.google\.com/(?!document|spreadsheets)"]),
    ("github", [r"github\.com", r"github\.io"]),
    ("slack", [r"slack\.com", r"\.slack\.com"]),
    ("figma", [r"figma\.com"]),
    ("notion", [r"notion\.so", r"notion\.site"]),
]


def categorize_link(url):
    """Categorize a URL into a known service or 'other'.

    Args:
        url: URL string.

    Returns:
        str: Category name (e.g., 'confluence', 'github', 'other').
    """
    url_lower = url.lower()
    for category, patterns in _CATEGORY_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return category
    return "other"


# ---------------------------------------------------------------------------
# Extraction from different formats
# ---------------------------------------------------------------------------

_URL_PATTERN = re.compile(
    r"https?://[^\s\)\]\}\>\"\',;`]+",
    re.IGNORECASE,
)

_MD_LINK_PATTERN = re.compile(
    r"\[([^\]]+)\]\((https?://[^\s\)]+)\)",
    re.IGNORECASE,
)


def extract_from_text(text, source_file=None):
    """Extract URLs from plain text.

    Args:
        text: Input text.
        source_file: Optional source file path for metadata.

    Returns:
        list[dict]: Link entries with url, title, source, category.
    """
    links = []
    seen = set()

    for match in _URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(".,;:!?)")
        if url not in seen:
            seen.add(url)
            links.append({
                "url": url,
                "title": "",
                "source": str(source_file) if source_file else "",
                "category": categorize_link(url),
            })

    return links


def extract_from_markdown(text, source_file=None):
    """Extract URLs from markdown, preserving link titles.

    Finds both [title](url) links and bare URLs.

    Args:
        text: Markdown text.
        source_file: Optional source file path.

    Returns:
        list[dict]: Link entries.
    """
    links = []
    seen = set()

    # Named links first
    for match in _MD_LINK_PATTERN.finditer(text):
        title = match.group(1).strip()
        url = match.group(2).rstrip(".,;:!?)")
        if url not in seen:
            seen.add(url)
            links.append({
                "url": url,
                "title": title,
                "source": str(source_file) if source_file else "",
                "category": categorize_link(url),
            })

    # Bare URLs
    for match in _URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(".,;:!?)")
        if url not in seen:
            seen.add(url)
            links.append({
                "url": url,
                "title": "",
                "source": str(source_file) if source_file else "",
                "category": categorize_link(url),
            })

    return links


def extract_from_pdf(pdf_path):
    """Extract URLs from a PDF file.

    Requires PyPDF2 or pypdf to be installed.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        list[dict]: Link entries.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            print(f"WARNING: pypdf/PyPDF2 not installed, skipping PDF: {pdf_path}")
            return []

    links = []
    seen = set()

    try:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            text = page.extract_text() or ""
            for match in _URL_PATTERN.finditer(text):
                url = match.group(0).rstrip(".,;:!?)")
                if url not in seen:
                    seen.add(url)
                    links.append({
                        "url": url,
                        "title": "",
                        "source": str(pdf_path),
                        "category": categorize_link(url),
                    })

            # Also check annotations for hyperlinks
            if page.get("/Annots"):
                for annot in page["/Annots"]:
                    obj = annot.get_object()
                    if obj.get("/A") and obj["/A"].get("/URI"):
                        url = str(obj["/A"]["/URI"])
                        if url not in seen:
                            seen.add(url)
                            links.append({
                                "url": url,
                                "title": "",
                                "source": str(pdf_path),
                                "category": categorize_link(url),
                            })
    except Exception as e:
        print(f"WARNING: Failed to read PDF {pdf_path}: {e}")

    return links


def extract_from_json(json_path):
    """Extract URLs from a JSON file (recursively searches all string values).

    Args:
        json_path: Path to the JSON file.

    Returns:
        list[dict]: Link entries.
    """
    try:
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"WARNING: Failed to parse JSON {json_path}: {e}")
        return []

    text_parts = []
    _extract_strings(data, text_parts)
    combined = " ".join(text_parts)
    return extract_from_text(combined, source_file=json_path)


def _extract_strings(obj, accumulator):
    """Recursively extract all string values from a JSON structure."""
    if isinstance(obj, str):
        accumulator.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _extract_strings(v, accumulator)
    elif isinstance(obj, list):
        for item in obj:
            _extract_strings(item, accumulator)


# ---------------------------------------------------------------------------
# Directory scanner
# ---------------------------------------------------------------------------

_FORMAT_MAP = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".log": "text",
    ".csv": "text",
    ".json": "json",
    ".pdf": "pdf",
    ".rst": "text",
    ".html": "text",
    ".htm": "text",
}


def scan_directory(directory, recursive=True):
    """Scan a directory for files and extract links from each.

    Args:
        directory: Root directory path.
        recursive: Whether to scan subdirectories.

    Returns:
        list[dict]: All extracted link entries.
    """
    root = Path(directory)
    if not root.is_dir():
        print(f"ERROR: Not a directory: {directory}")
        sys.exit(1)

    all_links = []
    glob_pattern = "**/*" if recursive else "*"

    for file_path in sorted(root.glob(glob_pattern)):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        fmt = _FORMAT_MAP.get(suffix)

        if fmt is None:
            continue

        try:
            if fmt == "markdown":
                text = file_path.read_text(encoding="utf-8", errors="replace")
                all_links.extend(extract_from_markdown(text, file_path))
            elif fmt == "text":
                text = file_path.read_text(encoding="utf-8", errors="replace")
                all_links.extend(extract_from_text(text, file_path))
            elif fmt == "json":
                all_links.extend(extract_from_json(file_path))
            elif fmt == "pdf":
                all_links.extend(extract_from_pdf(file_path))
        except Exception as e:
            print(f"WARNING: Error processing {file_path}: {e}")

    print(f"Scanned {root}: found {len(all_links)} links")
    return all_links


# ---------------------------------------------------------------------------
# Deduplication and output
# ---------------------------------------------------------------------------

def deduplicate_links(links):
    """Deduplicate links by URL, merging sources.

    Args:
        links: List of link entry dicts.

    Returns:
        list[dict]: Deduplicated links with source lists.
    """
    url_map = {}
    for link in links:
        url = link["url"]
        if url in url_map:
            existing = url_map[url]
            if link.get("source") and link["source"] not in existing.get("sources", []):
                existing.setdefault("sources", []).append(link["source"])
            if link.get("title") and not existing.get("title"):
                existing["title"] = link["title"]
        else:
            entry = dict(link)
            if entry.get("source"):
                entry["sources"] = [entry.pop("source")]
            else:
                entry["sources"] = []
                entry.pop("source", None)
            url_map[url] = entry

    return list(url_map.values())


def generate_markdown_report(links):
    """Generate a categorized markdown report of links.

    Args:
        links: List of deduplicated link entries.

    Returns:
        str: Markdown report text.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Link Index",
        "",
        f"Generated: {now}",
        f"Total unique links: {len(links)}",
        "",
    ]

    # Group by category
    by_category = defaultdict(list)
    for link in links:
        by_category[link.get("category", "other")].append(link)

    for category in sorted(by_category.keys()):
        cat_links = by_category[category]
        lines.append(f"## {category.replace('_', ' ').title()} ({len(cat_links)})")
        lines.append("")

        for link in sorted(cat_links, key=lambda l: l.get("title", l["url"])):
            title = link.get("title") or urlparse(link["url"]).path.split("/")[-1] or link["url"]
            lines.append(f"- [{title}]({link['url']})")
            sources = link.get("sources", [])
            if sources:
                source_names = [Path(s).name for s in sources[:3]]
                lines.append(f"  - Sources: {', '.join(source_names)}")

        lines.append("")

    return "\n".join(lines)


def save_index(links, output_dir):
    """Save the link index as both JSON and markdown.

    Args:
        links: Deduplicated link entries.
        output_dir: Directory for output files.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # JSON index
    json_path = out / "link_index.json"
    json_path.write_text(
        json.dumps(links, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"JSON index: {json_path}")

    # Markdown report
    md_path = out / "link_index.md"
    md_path.write_text(
        generate_markdown_report(links),
        encoding="utf-8",
    )
    print(f"Markdown report: {md_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract and categorize links from documents"
    )
    parser.add_argument("directory", help="Directory to scan for documents")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: <directory>/link_index)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not scan subdirectories",
    )
    args = parser.parse_args()

    links = scan_directory(args.directory, recursive=not args.no_recursive)
    links = deduplicate_links(links)

    output_dir = args.output_dir or str(Path(args.directory) / "link_index")
    save_index(links, output_dir)

    # Print summary
    by_cat = defaultdict(int)
    for link in links:
        by_cat[link.get("category", "other")] += 1

    print(f"\nSummary: {len(links)} unique links")
    for cat in sorted(by_cat.keys()):
        print(f"  {cat}: {by_cat[cat]}")


if __name__ == "__main__":
    main()
