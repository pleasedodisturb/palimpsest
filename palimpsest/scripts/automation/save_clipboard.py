#!/usr/bin/env python3
"""One-shot save of current clipboard content to a timestamped file.

Captures the current clipboard text and writes it to a file with an
optional desktop notification.

Usage:
    python save_clipboard.py [output_dir]
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_clipboard():
    """Get current clipboard text content via pbpaste."""
    try:
        result = subprocess.run(
            ["pbpaste"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


def notify(title, message):
    """Send a macOS desktop notification."""
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def save_clipboard(output_dir="clipboard_captures"):
    """Save current clipboard to a timestamped file.

    Args:
        output_dir: Directory to save the file in.

    Returns:
        Path or None: Path to saved file, or None if clipboard was empty.
    """
    text = get_clipboard()
    if not text.strip():
        print("Clipboard is empty.")
        return None

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = out_dir / f"clipboard_{timestamp}.txt"
    filepath.write_text(text, encoding="utf-8")

    print(f"Saved: {filepath} ({len(text)} chars)")
    notify("Clipboard Saved", f"{filepath.name} ({len(text)} chars)")
    return filepath


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "clipboard_captures"
    save_clipboard(output_dir)


if __name__ == "__main__":
    main()
