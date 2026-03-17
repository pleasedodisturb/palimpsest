#!/usr/bin/env python3
"""Upload markdown files to Google Docs with full formatting conversion.

Converts markdown content to Google Docs API requests preserving:
- Headings (H1-H4)
- Bold, italic, inline code, links
- Bullet and numbered lists
- Code blocks (monospace)
- Tables
- Blockquotes
- Horizontal rules

Usage:
    python upload_to_docs.py <markdown_file> [title] [--shared] [--folder FOLDER_ID]

Environment:
    PAC_WRITE_GUARD  -- Set to "1" to allow write operations (default: read-only)
    PAC_DOCS_FOLDER  -- Default Google Drive folder ID for uploads
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = SCRIPT_DIR / "token_docs.json"
CREDENTIALS_PATH = SCRIPT_DIR / "credentials.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
]

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_credentials():
    """Load or refresh Google OAuth2 credentials for Docs/Drive APIs."""
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
        print(f"Token saved to {TOKEN_PATH}")

    return creds


# ---------------------------------------------------------------------------
# Write guard
# ---------------------------------------------------------------------------

def check_write_guard():
    """Abort if write operations are not explicitly allowed."""
    if os.environ.get("PAC_WRITE_GUARD", "0") != "1":
        print("ERROR: Write guard is active. Set PAC_WRITE_GUARD=1 to allow writes.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Shared regex patterns
# ---------------------------------------------------------------------------

_CODE_FENCE = "```"
_HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)")
_BLOCKQUOTE_RE = re.compile(r"^>\s?")
_BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*)")
_NUMBERED_RE = re.compile(r"^(\s*)\d+\.\s+(.*)")
_HORIZONTAL_RULE_RE = re.compile(r"^[-*_]{3,}\s*$")
_TABLE_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")


# ---------------------------------------------------------------------------
# Inline formatting
# ---------------------------------------------------------------------------

def process_inline_formatting(text, start_index):
    """Convert inline markdown (bold, italic, code, links) to Docs API requests.

    Returns:
        tuple: (list of insert/style requests, end_index after all text inserted)
    """
    reqs = []
    segments = _tokenise_inline(text)

    current_index = start_index
    for segment in segments:
        seg_text = segment["text"]
        if not seg_text:
            continue

        reqs.append({
            "insertText": {
                "location": {"index": current_index},
                "text": seg_text,
            }
        })

        end = current_index + len(seg_text)

        # Apply styling
        style_updates = {}
        if segment.get("bold"):
            style_updates["bold"] = True
        if segment.get("italic"):
            style_updates["italic"] = True
        if segment.get("code"):
            style_updates["weightedFontFamily"] = {
                "fontFamily": "Courier New",
                "weight": 400,
            }

        if style_updates:
            reqs.append({
                "updateTextStyle": {
                    "range": {"startIndex": current_index, "endIndex": end},
                    "textStyle": style_updates,
                    "fields": ",".join(style_updates.keys()),
                }
            })

        if segment.get("link"):
            reqs.append({
                "updateTextStyle": {
                    "range": {"startIndex": current_index, "endIndex": end},
                    "textStyle": {"link": {"url": segment["link"]}},
                    "fields": "link",
                }
            })

        current_index = end

    return reqs, current_index


def _tokenise_inline(text):
    """Split markdown text into styled segments."""
    segments = []
    pos = 0

    combined = (
        r"(\*\*(.+?)\*\*)"
        r"|(\*(.+?)\*)"
        r"|(`(.+?)`)"
        r"|(\[(.+?)\]\((.+?)\))"
    )

    for match in re.finditer(combined, text):
        # Emit plain text before this match
        if match.start() > pos:
            segments.append({"text": text[pos:match.start()]})

        if match.group(1):  # bold
            segments.append({"text": match.group(2), "bold": True})
        elif match.group(3):  # italic
            segments.append({"text": match.group(4), "italic": True})
        elif match.group(5):  # code
            segments.append({"text": match.group(6), "code": True})
        elif match.group(7):  # link
            segments.append({"text": match.group(8), "link": match.group(9)})

        pos = match.end()

    # Remaining plain text
    if pos < len(text):
        segments.append({"text": text[pos:]})

    return segments


# ---------------------------------------------------------------------------
# Markdown -> Docs requests: block-level helpers
# ---------------------------------------------------------------------------

_HEADING_MAP = {
    1: "HEADING_1",
    2: "HEADING_2",
    3: "HEADING_3",
    4: "HEADING_4",
}


def _emit_code_block(lines, i, index):
    """Convert a fenced code block to Docs API requests.

    Returns:
        tuple: (requests_list, new_line_index, new_doc_index)
    """
    reqs = []
    i += 1  # skip opening fence
    code_lines = []
    while i < len(lines) and not lines[i].strip().startswith(_CODE_FENCE):
        code_lines.append(lines[i])
        i += 1
    i += 1  # skip closing fence
    code_text = "\n".join(code_lines) + "\n"
    reqs.append({
        "insertText": {
            "location": {"index": index},
            "text": code_text,
        }
    })
    end = index + len(code_text)
    reqs.append({
        "updateTextStyle": {
            "range": {"startIndex": index, "endIndex": end},
            "textStyle": {
                "weightedFontFamily": {
                    "fontFamily": "Courier New",
                    "weight": 400,
                },
                "fontSize": {"magnitude": 9, "unit": "PT"},
            },
            "fields": "weightedFontFamily,fontSize",
        }
    })
    reqs.append({
        "updateParagraphStyle": {
            "range": {"startIndex": index, "endIndex": end},
            "paragraphStyle": {
                "shading": {
                    "backgroundColor": {
                        "color": {
                            "rgbColor": {"red": 0.95, "green": 0.95, "blue": 0.95}
                        }
                    }
                }
            },
            "fields": "shading",
        }
    })
    return reqs, i, end


def _emit_table(lines, i, index):
    """Convert markdown table lines to Docs API table requests.

    Returns:
        tuple: (requests_list, new_line_index, new_doc_index)
    """
    reqs = []
    table_lines = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        stripped = lines[i].strip()
        if not _TABLE_SEPARATOR_RE.match(stripped):
            table_lines.append(stripped)
        i += 1

    if not table_lines:
        return reqs, i, index

    rows = []
    for tl in table_lines:
        cells = [c.strip() for c in tl.strip("|").split("|")]
        rows.append(cells)

    n_rows = len(rows)
    n_cols = max(len(r) for r in rows) if rows else 1

    reqs.append({
        "insertTable": {
            "rows": n_rows,
            "columns": n_cols,
            "location": {"index": index},
        }
    })

    cell_index = index + 1  # start of first row
    for row in rows:
        cell_index += 1  # tableRow start
        for cell_text in row:
            cell_index += 1  # tableCell start
            cell_index += 1  # paragraph start
            if cell_text:
                reqs.append({
                    "insertText": {
                        "location": {"index": cell_index},
                        "text": cell_text,
                    }
                })
                cell_index += len(cell_text)
            cell_index += 1  # paragraph end / newline
        # Pad missing cells
        for _ in range(n_cols - len(row)):
            cell_index += 1  # tableCell
            cell_index += 1  # paragraph
            cell_index += 1  # newline
        cell_index += 1  # row end

    return reqs, i, cell_index


def _emit_horizontal_rule(index):
    """Convert a horizontal rule to Docs API requests.

    Returns:
        tuple: (requests_list, new_doc_index)
    """
    reqs = []
    hr_text = "\n"
    reqs.append({
        "insertText": {
            "location": {"index": index},
            "text": hr_text,
        }
    })
    end = index + len(hr_text)
    reqs.append({
        "updateParagraphStyle": {
            "range": {"startIndex": index, "endIndex": end},
            "paragraphStyle": {
                "borderBottom": {
                    "color": {
                        "color": {
                            "rgbColor": {"red": 0.7, "green": 0.7, "blue": 0.7}
                        }
                    },
                    "width": {"magnitude": 1, "unit": "PT"},
                    "dashStyle": "SOLID",
                    "padding": {"magnitude": 6, "unit": "PT"},
                }
            },
            "fields": "borderBottom",
        }
    })
    return reqs, end


def _emit_heading(line_match, index):
    """Convert a heading line to Docs API requests.

    Returns:
        tuple: (requests_list, new_doc_index)
    """
    level = len(line_match.group(1))
    heading_text = line_match.group(2) + "\n"
    inline_reqs, new_index = process_inline_formatting(heading_text, index)
    reqs = list(inline_reqs)
    reqs.append({
        "updateParagraphStyle": {
            "range": {"startIndex": index, "endIndex": new_index},
            "paragraphStyle": {
                "namedStyleType": _HEADING_MAP[level],
            },
            "fields": "namedStyleType",
        }
    })
    return reqs, new_index


def _emit_blockquote(line, index):
    """Convert a blockquote line to Docs API requests.

    Returns:
        tuple: (requests_list, new_doc_index)
    """
    quote_text = re.sub(r"^>\s?", "", line.strip()) + "\n"
    inline_reqs, new_index = process_inline_formatting(quote_text, index)
    reqs = list(inline_reqs)
    reqs.append({
        "updateParagraphStyle": {
            "range": {"startIndex": index, "endIndex": new_index},
            "paragraphStyle": {
                "indentStart": {"magnitude": 36, "unit": "PT"},
                "borderLeft": {
                    "color": {
                        "color": {
                            "rgbColor": {"red": 0.6, "green": 0.6, "blue": 0.6}
                        }
                    },
                    "width": {"magnitude": 3, "unit": "PT"},
                    "dashStyle": "SOLID",
                    "padding": {"magnitude": 6, "unit": "PT"},
                },
            },
            "fields": "indentStart,borderLeft",
        }
    })
    reqs.append({
        "updateTextStyle": {
            "range": {"startIndex": index, "endIndex": new_index},
            "textStyle": {
                "italic": True,
                "foregroundColor": {
                    "color": {
                        "rgbColor": {"red": 0.4, "green": 0.4, "blue": 0.4}
                    }
                },
            },
            "fields": "italic,foregroundColor",
        }
    })
    return reqs, new_index


def _emit_bullet(line_match, index):
    """Convert a bullet list item to Docs API requests.

    Returns:
        tuple: (requests_list, new_doc_index)
    """
    indent_level = len(line_match.group(1)) // 2
    item_text = line_match.group(2) + "\n"
    inline_reqs, new_index = process_inline_formatting(item_text, index)
    reqs = list(inline_reqs)
    reqs.append({
        "createParagraphBullets": {
            "range": {"startIndex": index, "endIndex": new_index},
            "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
        }
    })
    if indent_level > 0:
        reqs.append({
            "updateParagraphStyle": {
                "range": {"startIndex": index, "endIndex": new_index},
                "paragraphStyle": {
                    "indentStart": {
                        "magnitude": 36 * (indent_level + 1),
                        "unit": "PT",
                    },
                    "indentFirstLine": {
                        "magnitude": 36 * (indent_level + 1),
                        "unit": "PT",
                    },
                },
                "fields": "indentStart,indentFirstLine",
            }
        })
    return reqs, new_index


def _emit_numbered(line_match, index):
    """Convert a numbered list item to Docs API requests.

    Returns:
        tuple: (requests_list, new_doc_index)
    """
    item_text = line_match.group(2) + "\n"
    inline_reqs, new_index = process_inline_formatting(item_text, index)
    reqs = list(inline_reqs)
    reqs.append({
        "createParagraphBullets": {
            "range": {"startIndex": index, "endIndex": new_index},
            "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN",
        }
    })
    return reqs, new_index


# ---------------------------------------------------------------------------
# Markdown -> Docs requests: main converter
# ---------------------------------------------------------------------------

def _try_multiline_block(lines, i, index):
    """Handle multi-line blocks (code, table) that advance their own line index.

    Returns:
        tuple: (requests, new_i, new_index) or None if no match.
    """
    line = lines[i]
    if line.strip().startswith(_CODE_FENCE):
        return _emit_code_block(lines, i, index)
    if line.strip().startswith("|") and i + 1 < len(lines):
        return _emit_table(lines, i, index)
    return None


def _try_single_line_block(line, index):
    """Handle single-line block elements (hr, heading, blockquote, lists).

    Returns:
        tuple: (requests, new_index) or None if no match.
    """
    if _HORIZONTAL_RULE_RE.match(line.strip()):
        return _emit_horizontal_rule(index)

    heading_match = _HEADING_RE.match(line)
    if heading_match:
        return _emit_heading(heading_match, index)

    if line.strip().startswith(">"):
        return _emit_blockquote(line, index)

    bullet_match = _BULLET_RE.match(line)
    if bullet_match:
        return _emit_bullet(bullet_match, index)

    num_match = _NUMBERED_RE.match(line)
    if num_match:
        return _emit_numbered(num_match, index)

    return None


def _emit_paragraph_or_blank(line, index):
    """Emit requests for a plain paragraph or empty-line spacer.

    Returns:
        tuple: (requests, new_index)
    """
    if line.strip():
        para_text = line.strip() + "\n"
        return process_inline_formatting(para_text, index)
    return [{"insertText": {"location": {"index": index}, "text": "\n"}}], index + 1


def markdown_to_docs_requests(markdown_text):
    """Convert full markdown text to a list of Google Docs API requests.

    Supports: headings (h1-h4), bold, italic, code spans, links,
    bullet lists, numbered lists, code blocks (monospace), tables,
    blockquotes, and horizontal rules.

    Returns:
        list[dict]: Docs API batchUpdate requests (applied in order).
    """
    lines = markdown_text.split("\n")
    all_requests = []
    index = 1  # Docs body starts at index 1

    i = 0
    while i < len(lines):
        line = lines[i]

        # Multi-line blocks advance i themselves
        multi = _try_multiline_block(lines, i, index)
        if multi:
            reqs, i, index = multi
            all_requests.extend(reqs)
            continue

        # Single-line block elements
        single = _try_single_line_block(line, index)
        if single:
            reqs, index = single
            all_requests.extend(reqs)
            i += 1
            continue

        # Plain paragraph or empty line
        reqs, index = _emit_paragraph_or_blank(line, index)
        all_requests.extend(reqs)
        i += 1

    return all_requests


# ---------------------------------------------------------------------------
# Document creation
# ---------------------------------------------------------------------------

def create_doc_from_markdown(creds, md_file, title=None, folder_id=None):
    """Create a Google Doc from a markdown file.

    Args:
        creds: Google OAuth2 credentials.
        md_file: Path to the markdown file.
        title: Document title (defaults to filename stem).
        folder_id: Google Drive folder ID to move doc into.

    Returns:
        str: URL of the created Google Doc.
    """
    from googleapiclient.discovery import build

    md_path = Path(md_file)
    if not md_path.exists():
        print(f"ERROR: File not found: {md_file}")
        sys.exit(1)

    markdown_text = md_path.read_text(encoding="utf-8")
    if title is None:
        title = md_path.stem.replace("_", " ").replace("-", " ").title()

    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Create empty doc
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"Created document: {doc_url}")

    # Move to folder if specified
    if folder_id:
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            fields="id,parents",
        ).execute()
        print(f"Moved to folder: {folder_id}")

    # Convert markdown to requests and apply
    doc_requests = markdown_to_docs_requests(markdown_text)
    if doc_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": doc_requests},
        ).execute()
        print(f"Applied {len(doc_requests)} formatting requests")

    # Add agent marker as document property
    _add_agent_marker(drive_service, doc_id, md_path.name)

    return doc_url


def _add_agent_marker(drive_service, doc_id, source_file):
    """Set pac agent marker properties on the document."""
    now = datetime.now(timezone.utc).isoformat()
    properties = {
        "pac_agent": "upload_to_docs",
        "pac_source": source_file,
        "pac_timestamp": now,
        "pac_version": "1.0",
    }
    drive_service.files().update(
        fileId=doc_id,
        body={"properties": properties},
        fields="id",
    ).execute()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Upload a markdown file to Google Docs"
    )
    parser.add_argument("file", help="Path to the markdown file")
    parser.add_argument("title", nargs="?", default=None, help="Document title")
    parser.add_argument(
        "--shared",
        action="store_true",
        help="Make the document accessible to anyone with the link",
    )
    parser.add_argument(
        "--folder",
        default=os.environ.get("PAC_DOCS_FOLDER"),
        help="Google Drive folder ID (env: PAC_DOCS_FOLDER)",
    )
    args = parser.parse_args()

    check_write_guard()
    creds = get_credentials()
    doc_url = create_doc_from_markdown(creds, args.file, args.title, args.folder)

    if args.shared:
        from googleapiclient.discovery import build

        drive = build("drive", "v3", credentials=creds)
        drive.permissions().create(
            fileId=doc_url.split("/d/")[1].split("/")[0],
            body={"type": "anyone", "role": "reader"},
        ).execute()
        print("Shared: anyone with the link can view")

    print(f"\nDone: {doc_url}")


if __name__ == "__main__":
    main()
