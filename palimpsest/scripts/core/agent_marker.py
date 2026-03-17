#!/usr/bin/env python3
"""
Agent metadata markers for Drive/Confluence.

Markers are invisible to users but machine-parsable, allowing agents to
track provenance of automated changes.

Configuration (all via env vars):
- ``PAC_AGENT`` -- agent name recorded in markers (default ``"cursor"``).
- ``ENABLE_AGENT_MARKERS`` -- set to ``0`` to disable (default ``1``).
- ``MARKER_DEBUG`` -- set to ``1`` for debug output.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict, Optional


MARKER_VERSION = "1"
CONFLUENCE_MARKER_KEY = "pac.agent_marker"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _markers_enabled() -> bool:
    return os.getenv("ENABLE_AGENT_MARKERS", "1").strip().lower() in {
        "1", "true", "yes", "y",
    }


def _debug(msg: str) -> None:
    if os.getenv("MARKER_DEBUG", "").strip().lower() in {"1", "true", "yes", "y"}:
        print(f"[marker] {msg}")


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _actor_user() -> str:
    return os.getenv("USER") or os.getenv("USERNAME") or "unknown"


def _agent_name() -> str:
    return os.getenv("PAC_AGENT", "cursor")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_marker(
    action: str,
    source: str,
    target_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a marker dict describing an agent action."""
    marker: Dict[str, Any] = {
        "marker_version": int(MARKER_VERSION),
        "uid": uuid4().hex,
        "timestamp_utc": _now_utc(),
        "action": action,
        "source": source,
        "agent": _agent_name(),
        "user": _actor_user(),
    }
    if target_id:
        marker["target_id"] = target_id
    if extra:
        marker.update(extra)
    return marker


def upsert_drive_marker(
    drive_service,
    file_id: str,
    action: str,
    source: str,
) -> bool:
    """Store marker in Drive ``appProperties`` (not visible in UI).

    Keeps original ``created_*`` fields if they already exist.
    """
    if not _markers_enabled():
        return False

    existing_props: Dict[str, str] = {}
    try:
        meta = drive_service.files().get(
            fileId=file_id, fields="appProperties",
        ).execute()
        existing_props = meta.get("appProperties", {}) or {}
    except Exception:
        existing_props = {}

    marker = build_marker(action=action, source=source, target_id=file_id)
    now = marker["timestamp_utc"]
    uid = marker["uid"]

    update_props = {
        "pac_marker_version": MARKER_VERSION,
        "pac_updated_at_utc": now,
        "pac_updated_uid": uid,
        "pac_updated_by": marker["user"],
        "pac_updated_agent": marker["agent"],
        "pac_updated_source": source,
        "pac_updated_action": action,
    }

    if not existing_props.get("pac_created_at_utc"):
        update_props.update({
            "pac_created_at_utc": now,
            "pac_created_uid": uid,
            "pac_created_by": marker["user"],
            "pac_created_agent": marker["agent"],
            "pac_created_source": source,
            "pac_created_action": action,
        })

    merged = {**existing_props, **update_props}
    try:
        drive_service.files().update(
            fileId=file_id,
            body={"appProperties": merged},
            fields="id, appProperties",
        ).execute()
        return True
    except Exception as exc:
        _debug(f"Drive marker update failed for {file_id}: {exc}")
        return False


def set_confluence_marker(
    page_id: str,
    headers: Dict[str, str],
    domain: str,
    action: str,
    source: str,
    page_version: Optional[int] = None,
    dry_run: bool = False,
) -> bool:
    """Store marker in Confluence content property (not visible in UI)."""
    if dry_run:
        return True

    if not _markers_enabled():
        return False

    import requests

    try:
        marker = build_marker(
            action=action,
            source=source,
            target_id=page_id,
            extra={"page_version": page_version},
        )
        base_url = f"https://{domain}"
        prop_url = (
            f"{base_url}/wiki/rest/api/content/{page_id}"
            f"/property/{CONFLUENCE_MARKER_KEY}"
        )

        resp = requests.get(prop_url, headers=headers)
        if resp.status_code == 404:
            create_url = f"{base_url}/wiki/rest/api/content/{page_id}/property"
            payload = {"key": CONFLUENCE_MARKER_KEY, "value": marker}
            create_resp = requests.post(create_url, headers=headers, json=payload)
            return create_resp.ok

        if not resp.ok:
            return False

        data = resp.json()
        version = data.get("version", {}).get("number", 1) + 1
        payload = {
            "key": CONFLUENCE_MARKER_KEY,
            "value": marker,
            "version": {"number": version},
        }
        update_resp = requests.put(prop_url, headers=headers, json=payload)
        return update_resp.ok
    except Exception as exc:
        _debug(f"Confluence marker update failed for {page_id}: {exc}")
        return False
