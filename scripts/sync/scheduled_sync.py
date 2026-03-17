#!/usr/bin/env python3
"""
Scheduled Sync Runner for Palimpsest

Runs all sync operations in three phases and auto-commits changes to git.
Can be run manually or via cron/launchd.

Phases:
  1. Gather -- Drive sync, link extraction, registry build
  2. Push   -- Confluence page updates
  3. Git    -- Stage, commit, push

All configuration is driven by environment variables.

Usage:
    python scheduled_sync.py              # Full sync + commit
    python scheduled_sync.py --dry-run    # Preview without committing
    python scheduled_sync.py --no-push    # Commit but don't push
    python scheduled_sync.py --skip-drive # Skip Google Drive sync
    python scheduled_sync.py --skip-links # Skip link extraction
    python scheduled_sync.py --full-update # Full sync + Confluence push
"""

import os
import sys
import subprocess
import argparse
import json
import re
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

import requests

# Paths -- all derived from environment or relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.getenv(
    "PAC_PROJECT_ROOT",
    str(SCRIPT_DIR.parent.parent),
))
VENV_PYTHON = Path(os.getenv(
    "PAC_PYTHON",
    str(SCRIPT_DIR / "venv" / "bin" / "python"),
))

# Load environment variables
load_dotenv(SCRIPT_DIR / ".env")


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log(msg: str, level: str = "INFO") -> None:
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    symbols = {
        "INFO": "[i]",
        "OK": "[+]",
        "WARN": "[!]",
        "ERROR": "[x]",
        "RUN": "[~]",
    }
    symbol = symbols.get(level, "[.]")
    print(f"[{timestamp}] {symbol} {msg}")


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------

def run_command(
    cmd: list,
    cwd: Optional[Path] = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd or PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=check,
        )
        return result
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {' '.join(cmd)}", "ERROR")
        log(f"  stdout: {e.stdout[:200] if e.stdout else 'none'}", "ERROR")
        log(f"  stderr: {e.stderr[:200] if e.stderr else 'none'}", "ERROR")
        raise


def check_git_status() -> bool:
    """Check if there are uncommitted changes."""
    result = run_command(["git", "status", "--porcelain"])
    return bool(result.stdout.strip())


def get_changed_files() -> list:
    """Get list of changed files."""
    result = run_command(["git", "status", "--porcelain"])
    files = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            files.append(line[3:].strip())
    return files


# ---------------------------------------------------------------------------
# Phase 1: Gather
# ---------------------------------------------------------------------------

def run_gdrive_sync() -> bool:
    """Run Google Drive sync."""
    log("Running Google Drive sync...", "RUN")

    try:
        result = run_command(
            [str(VENV_PYTHON), "gdrive_sync.py"],
            cwd=SCRIPT_DIR,
        )
        output = result.stdout
        if "Found" in output:
            log("Drive sync complete", "OK")
        return True
    except Exception as e:
        log(f"Drive sync failed: {e}", "ERROR")
        return False


def run_link_extractor() -> bool:
    """Run link extractor on synced documents."""
    log("Extracting links from documents...", "RUN")

    try:
        result = run_command(
            [str(VENV_PYTHON), "link_extractor.py"],
            cwd=SCRIPT_DIR,
            check=False,
        )
        if result.returncode == 0:
            log("Link extraction complete", "OK")
        else:
            log("Link extraction skipped (no new docs)", "WARN")
        return True
    except Exception as e:
        log(f"Link extraction failed: {e}", "WARN")
        return False


def _run_drive_keyword_search() -> bool:
    """Run Drive keyword search."""
    log("Running Drive keyword search...", "RUN")

    try:
        run_command(
            [str(VENV_PYTHON), "gdrive_sync.py", "--search-keywords"],
            cwd=SCRIPT_DIR,
            check=False,
        )
        log("Drive keyword search complete", "OK")
        return True
    except Exception as e:
        log(f"Drive keyword search failed: {e}", "WARN")
        return False


def build_registry() -> bool:
    """Build unified document registry."""
    log("Building document registry...", "RUN")

    try:
        run_command(
            [str(VENV_PYTHON), "build_document_registry.py"],
            cwd=SCRIPT_DIR,
        )
        log("Registry built", "OK")
        return True
    except Exception as e:
        log(f"Registry build failed: {e}", "ERROR")
        return False


# ---------------------------------------------------------------------------
# Phase 2: Push to Confluence
# ---------------------------------------------------------------------------

def sync_confluence_pages() -> bool:
    """Fetch Confluence space structure and update local index."""
    log("Syncing Confluence page structure...", "RUN")

    email = os.getenv("ATLASSIAN_EMAIL")
    token = os.getenv("ATLASSIAN_API_TOKEN")
    domain = os.getenv("ATLASSIAN_DOMAIN")
    space_key = os.getenv("CONFLUENCE_SPACE_KEY")

    if not all([email, token, domain]):
        log("Missing Atlassian credentials, skipping Confluence sync", "WARN")
        return True  # Non-fatal

    if not space_key:
        log("CONFLUENCE_SPACE_KEY not set, skipping Confluence sync", "WARN")
        return True  # Non-fatal

    try:
        auth_bytes = base64.b64encode(f"{email}:{token}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json",
        }

        url = f"https://{domain}/wiki/rest/api/content"
        params = {
            "spaceKey": space_key,
            "expand": "version",
            "limit": 100,
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        pages = []
        for page in data.get("results", []):
            pages.append({
                "title": page["title"],
                "id": page["id"],
                "version": page.get("version", {}).get("number", "-"),
                "url": f"https://{domain}/wiki/spaces/{space_key}/pages/{page['id']}",
            })

        pages.sort(key=lambda p: p["title"])

        # Update CONTEXT_INDEX.md if it exists
        context_index = PROJECT_ROOT / "docs" / "CONTEXT_INDEX.md"
        if context_index.exists():
            content = context_index.read_text()

            # Build new table
            table_lines = [
                "| Page | ID | URL | Version |",
                "|------|-----|-----|---------|",
            ]
            for p in pages:
                table_lines.append(
                    f"| {p['title']} | {p['id']} | {p['url']} | {p['version']} |"
                )
            new_table = "\n".join(table_lines)

            # Replace the Confluence pages section
            pattern = (
                r"(## Confluence Pages.*?> \*Auto-synced section.*?\*\n\n)"
                r"(\|.*?\n)+(\n---)"
            )
            replacement = f"\\1{new_table}\n\n---"
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

            # Update timestamp
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            new_content = re.sub(
                r"\*\*Last Updated:\*\* .*",
                f"**Last Updated:** {timestamp}",
                new_content,
            )

            context_index.write_text(new_content)
            log(f"Updated CONTEXT_INDEX.md with {len(pages)} Confluence pages", "OK")
        else:
            log("CONTEXT_INDEX.md not found, skipping update", "WARN")

        return True

    except Exception as e:
        log(f"Confluence sync failed: {e}", "ERROR")
        return False


# ---------------------------------------------------------------------------
# Phase 3: Git
# ---------------------------------------------------------------------------

def git_commit_and_push(dry_run: bool = False, no_push: bool = False) -> bool:
    """Commit changes and push to remote."""
    if not check_git_status():
        log("No changes to commit", "INFO")
        return True

    changed = get_changed_files()
    log(f"Changed files: {len(changed)}", "INFO")
    for f in changed[:5]:
        log(f"  - {f}", "INFO")
    if len(changed) > 5:
        log(f"  ... and {len(changed) - 5} more", "INFO")

    if dry_run:
        log("DRY RUN -- would commit and push", "WARN")
        return True

    # Stage all changes
    log("Staging changes...", "RUN")
    run_command(["git", "add", "-A"])

    # Commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"chore: automated sync - {timestamp}\n\nFiles updated: {len(changed)}"

    log("Committing...", "RUN")
    try:
        run_command(["git", "commit", "-m", commit_msg])
        log("Committed successfully", "OK")
    except subprocess.CalledProcessError:
        log("Nothing to commit", "WARN")
        return True

    # Push
    if no_push:
        log("Skipping push (--no-push flag)", "WARN")
        return True

    log("Pushing to remote...", "RUN")
    try:
        run_command(["git", "push"])
        log("Pushed successfully", "OK")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Push failed: {e}", "ERROR")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scheduled sync for Palimpsest")
    parser.add_argument("--dry-run", action="store_true", help="Preview without committing")
    parser.add_argument("--no-push", action="store_true", help="Commit but don't push")
    parser.add_argument("--skip-drive", action="store_true", help="Skip Drive sync")
    parser.add_argument("--skip-links", action="store_true", help="Skip link extraction")
    parser.add_argument("--full-update", action="store_true", help="Full sync + Confluence push")
    args = parser.parse_args()

    log("=" * 50, "INFO")
    log("Palimpsest - Scheduled Sync", "INFO")
    log("=" * 50, "INFO")
    log(f"Project root: {PROJECT_ROOT}", "INFO")
    log(f"Dry run: {args.dry_run}", "INFO")
    if args.full_update:
        log("Mode: FULL UPDATE (sync + Confluence push)", "INFO")

    os.chdir(PROJECT_ROOT)

    success = True

    # ========================================
    # PHASE 1: GATHER DATA
    # ========================================
    log("-" * 50, "INFO")
    log("PHASE 1: Gathering Data", "INFO")
    log("-" * 50, "INFO")

    # Step 1.1: Drive sync
    if not args.skip_drive:
        if not run_gdrive_sync():
            success = False

    # Step 1.2: Drive keyword search
    if not args.skip_drive:
        _run_drive_keyword_search()  # Non-fatal

    # Step 1.3: Link extraction
    if not args.skip_links:
        run_link_extractor()  # Non-fatal

    # Step 1.4: Build registry
    if not args.skip_drive and not build_registry():
        success = False

    # ========================================
    # PHASE 2: PUSH TO CONFLUENCE
    # ========================================
    if args.full_update:
        log("-" * 50, "INFO")
        log("PHASE 2: Pushing to Confluence", "INFO")
        log("-" * 50, "INFO")

        if not sync_confluence_pages():
            success = False

    # ========================================
    # PHASE 3: COMMIT & PUSH
    # ========================================
    log("-" * 50, "INFO")
    log("PHASE 3: Git Commit & Push", "INFO")
    log("-" * 50, "INFO")

    if not git_commit_and_push(dry_run=args.dry_run, no_push=args.no_push):
        success = False

    log("=" * 50, "INFO")
    if success:
        log("Sync completed successfully", "OK")
    else:
        log("Sync completed with errors", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
