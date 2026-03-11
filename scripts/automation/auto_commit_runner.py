#!/usr/bin/env python3
"""Automated git commit runner for Palimpsest workspaces.

Watches for file changes and commits them on a schedule, filtering
by allowlist/denylist patterns.

Usage:
    python auto_commit_runner.py [--config CONFIG] [--once]

Config file format (auto_commit_config.json):
    {
        "interval": 900,
        "repo_path": ".",
        "allowlist": ["docs/**", "*.md"],
        "denylist": [".env", "*.secret", "token_*"],
        "message_template": "chore: auto-commit {count} file(s) at {timestamp}"
    }
"""

import argparse
import fnmatch
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CONFIG = {
    "interval": 900,
    "repo_path": ".",
    "allowlist": ["*"],
    "denylist": [".env", "*.secret", "token_*", "*.pyc", "__pycache__/*"],
    "message_template": "chore: auto-commit {count} file(s) at {timestamp}",
}


def is_git_repo(path):
    """Check if the given path is inside a git repository.

    Args:
        path: Directory path to check.

    Returns:
        bool: True if path is in a git repo.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=path,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def list_changes(repo_path):
    """List changed and untracked files in the repository.

    Args:
        repo_path: Path to the git repository.

    Returns:
        list[str]: File paths relative to the repo root.
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    entries = []
    for line in result.stdout.strip().splitlines():
        if len(line) > 3:
            filepath = line[3:].strip()
            entries.append(filepath)
    return entries


def stage_changes(repo_path, entries, allowlist, denylist):
    """Stage files matching allowlist but not denylist.

    Args:
        repo_path: Path to the git repository.
        entries: List of changed file paths.
        allowlist: Glob patterns for allowed files.
        denylist: Glob patterns for denied files.

    Returns:
        int: Number of files staged.
    """
    staged = 0
    for filepath in entries:
        # Check denylist first
        denied = any(fnmatch.fnmatch(filepath, pat) for pat in denylist)
        if denied:
            continue

        # Check allowlist
        allowed = any(fnmatch.fnmatch(filepath, pat) for pat in allowlist)
        if not allowed:
            continue

        subprocess.run(
            ["git", "add", filepath],
            cwd=repo_path,
            capture_output=True,
        )
        staged += 1

    return staged


def has_staged_changes(repo_path):
    """Check if there are staged changes ready to commit.

    Args:
        repo_path: Path to the git repository.

    Returns:
        bool: True if there are staged changes.
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_path,
        capture_output=True,
    )
    return result.returncode != 0


def commit_changes(repo_path, message):
    """Create a git commit with the given message.

    Args:
        repo_path: Path to the git repository.
        message: Commit message string.

    Returns:
        bool: True if commit succeeded.
    """
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"Committed: {message}")
        return True
    else:
        print(f"Commit failed: {result.stderr.strip()}")
        return False


def run_once(config):
    """Execute a single commit cycle.

    Args:
        config: Configuration dict.

    Returns:
        bool: True if a commit was made.
    """
    repo_path = config["repo_path"]

    if not is_git_repo(repo_path):
        print(f"ERROR: {repo_path} is not a git repository.")
        return False

    entries = list_changes(repo_path)
    if not entries:
        print("No changes detected.")
        return False

    count = stage_changes(repo_path, entries, config["allowlist"], config["denylist"])
    if count == 0 or not has_staged_changes(repo_path):
        print("No eligible files to commit.")
        return False

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    message = config["message_template"].format(count=count, timestamp=timestamp)
    return commit_changes(repo_path, message)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Automated git commit runner"
    )
    parser.add_argument(
        "--config",
        default="auto_commit_config.json",
        help="Path to config JSON file",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single cycle and exit",
    )
    args = parser.parse_args()

    config = dict(DEFAULT_CONFIG)
    config_path = Path(args.config)
    if config_path.exists():
        user_config = json.loads(config_path.read_text(encoding="utf-8"))
        config.update(user_config)
        print(f"Loaded config from {config_path}")

    if args.once:
        run_once(config)
        return

    print(f"Auto-commit runner started (interval: {config['interval']}s)")
    try:
        while True:
            run_once(config)
            time.sleep(config["interval"])
    except KeyboardInterrupt:
        print("\nAuto-commit runner stopped.")


if __name__ == "__main__":
    main()
