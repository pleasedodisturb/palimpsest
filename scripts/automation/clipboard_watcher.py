#!/usr/bin/env python3
"""Watch the system clipboard and save new content to timestamped files.

Polls the clipboard at a configurable interval and saves any new text
content that meets minimum length requirements. Useful for capturing
meeting transcripts and other pasted content.

Usage:
    python clipboard_watcher.py [--output-dir DIR] [--prefix PREFIX]
                                [--min-length N] [--interval N]

Platform: macOS (uses pbpaste). Linux support possible via xclip.
"""

import argparse
import hashlib
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def get_clipboard():
    """Get current clipboard text content.

    Uses pbpaste on macOS. Returns empty string on failure.

    Returns:
        str: Clipboard text content.
    """
    try:
        result = subprocess.run(
            ["pbpaste"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout
    except FileNotFoundError:
        # Try xclip for Linux
        try:
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
    except subprocess.TimeoutExpired:
        pass

    return ""


def content_hash(text):
    """Compute an MD5 hash of the text for change detection.

    Args:
        text: Input text.

    Returns:
        str: Hex MD5 digest.
    """
    return hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()


def notify(title, message):
    """Send a desktop notification via osascript (macOS).

    Args:
        title: Notification title.
        message: Notification body text.
    """
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # Silently skip notifications on non-macOS or timeout
        pass


def save_transcript(content, output_dir, prefix="clipboard"):
    """Save clipboard content to a timestamped file.

    Args:
        content: Text content to save.
        output_dir: Directory for output files.
        prefix: Filename prefix.

    Returns:
        Path: Path to the saved file.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.txt"
    filepath = out_dir / filename

    filepath.write_text(content, encoding="utf-8")
    return filepath


def watch_clipboard(output_dir, prefix="clipboard", min_length=50, interval=2):
    """Continuously watch the clipboard for new content.

    Polls at the given interval and saves new content that exceeds
    the minimum length threshold.

    Args:
        output_dir: Directory to save captured content.
        prefix: Filename prefix for saved files.
        min_length: Minimum character count to trigger save.
        interval: Polling interval in seconds.
    """
    print("Clipboard watcher started")
    print(f"  Output: {output_dir}")
    print(f"  Prefix: {prefix}")
    print(f"  Min length: {min_length}")
    print(f"  Interval: {interval}s")
    print("  Press Ctrl+C to stop\n")

    last_hash = ""
    save_count = 0

    try:
        while True:
            text = get_clipboard()

            if text and len(text) >= min_length:
                current_hash = content_hash(text)

                if current_hash != last_hash:
                    filepath = save_transcript(text, output_dir, prefix)
                    save_count += 1
                    last_hash = current_hash

                    preview = text[:80].replace("\n", " ")
                    print(f"[{save_count}] Saved: {filepath.name} ({len(text)} chars)")
                    print(f"    Preview: {preview}...")

                    notify(
                        "Clipboard Watcher",
                        f"Saved {filepath.name} ({len(text)} chars)",
                    )

            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\nStopped. Total captures: {save_count}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Watch clipboard and save new content"
    )
    parser.add_argument(
        "--output-dir",
        default="clipboard_captures",
        help="Directory for saved files (default: clipboard_captures)",
    )
    parser.add_argument(
        "--prefix",
        default="clipboard",
        help="Filename prefix (default: clipboard)",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=50,
        help="Minimum text length to save (default: 50)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Polling interval in seconds (default: 2)",
    )
    args = parser.parse_args()

    watch_clipboard(args.output_dir, args.prefix, args.min_length, args.interval)


if __name__ == "__main__":
    main()
