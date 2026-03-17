#!/usr/bin/env python3
"""
Google write guardrails for Palimpsest scripts.

Use before any Drive/Docs write/move/delete/share action.

Environment variables:
- ``ALLOW_GOOGLE_WRITE`` -- set to ``1`` to permit writes (required).
- ``GOOGLE_WRITE_ALLOWLIST`` -- optional comma-separated list of allowed
  target IDs or aliases (e.g. ``"my-drive,<folder_id>"``).
"""

from __future__ import annotations

import os
import sys
from typing import Iterable, Optional, Set


def _parse_allowlist(raw: str) -> Set[str]:
    return {item.strip() for item in raw.split(",") if item.strip()}


def require_write_enabled(
    action: str,
    target_ids: Optional[Iterable[str]] = None,
    allow_my_drive: bool = True,
) -> None:
    """Enforce explicit opt-in for Google writes.

    Raises ``SystemExit`` when writes are not permitted.

    Parameters
    ----------
    action : str
        Human-readable description of the intended write.
    target_ids : iterable of str, optional
        File/folder IDs that will be modified.
    allow_my_drive : bool
        When *True* and no *target_ids* are given, treat the write as
        targeting ``"my-drive"`` (which must appear in the allowlist if one
        is configured).
    """
    allow = os.getenv("ALLOW_GOOGLE_WRITE", "").strip().lower() in {
        "1", "true", "yes", "y",
    }
    if not allow:
        _abort(f"Write blocked. Set ALLOW_GOOGLE_WRITE=1 to allow: {action}")

    allowlist_raw = os.getenv("GOOGLE_WRITE_ALLOWLIST", "").strip()
    if not allowlist_raw:
        return

    allowlist = _parse_allowlist(allowlist_raw)
    targets = {t for t in (target_ids or []) if t}

    if allow_my_drive and not targets:
        targets = {"my-drive"}

    if not targets:
        _abort("Write blocked: allowlist set but no target ids provided.")

    if not (targets & allowlist):
        _abort(
            "Write blocked by allowlist. Targets "
            f"{sorted(targets)} not in GOOGLE_WRITE_ALLOWLIST."
        )


def _abort(message: str) -> None:
    print(f"[BLOCKED] {message}")
    print("  Set ALLOW_GOOGLE_WRITE=1 to enable writes.")
    if os.getenv("GOOGLE_WRITE_ALLOWLIST"):
        print("  Ensure target folder/file id is listed in GOOGLE_WRITE_ALLOWLIST.")
        print("  Examples: my-drive, <folder_id>")
    sys.exit(1)
