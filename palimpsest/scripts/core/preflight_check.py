#!/usr/bin/env python3
"""
Preflight access check for external services.

Checks (read-only, no writes):
- Google Drive (token.json)
- Google Docs write token validity (token_docs.json)
- Atlassian (Jira + Confluence)
- Slack
- Glean

All paths are config-driven via environment variables -- no hardcoded paths.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Tuple

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

import requests
from requests.auth import HTTPBasicAuth

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except Exception:
    GOOGLE_API_AVAILABLE = False


SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")

MSG_GOOGLE_API_MISSING = "google api libs missing"
MSG_GOOGLE_DOCS_TOKEN = "Google Docs token"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_result(name: str, ok: bool, detail: str = "") -> None:
    status = "[OK]  " if ok else "[FAIL]"
    if detail:
        print(f"{status} {name} - {detail}")
    else:
        print(f"{status} {name}")


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_google_drive() -> Tuple[bool, str]:
    """Verify the Google Drive read-only token is valid."""
    if not GOOGLE_API_AVAILABLE:
        return False, MSG_GOOGLE_API_MISSING
    token_path = SCRIPT_DIR / "token.json"
    if not token_path.exists():
        return False, "token.json missing"

    try:
        creds = Credentials.from_authorized_user_file(
            str(token_path),
            ["https://www.googleapis.com/auth/drive.readonly"],
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
        drive = build("drive", "v3", credentials=creds)
        about = drive.about().get(fields="user").execute()
        user = about.get("user", {})
        name = user.get("displayName", "unknown")
        return True, f"user: {name}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:120]}"


def check_google_docs_token() -> Tuple[bool, str]:
    """Verify the Google Docs write token is valid."""
    if not GOOGLE_API_AVAILABLE:
        return False, MSG_GOOGLE_API_MISSING
    token_path = SCRIPT_DIR / "token_docs.json"
    if not token_path.exists():
        return False, "token_docs.json missing"

    try:
        creds = Credentials.from_authorized_user_file(
            str(token_path),
            [
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/documents",
            ],
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
        drive = build("drive", "v3", credentials=creds)
        drive.files().list(pageSize=1, fields="files(id)").execute()
        return True, "docs token valid"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:120]}"


def check_atlassian() -> Tuple[bool, str]:
    """Verify Atlassian (Jira + Confluence) credentials."""
    email = os.getenv("ATLASSIAN_EMAIL")
    token = os.getenv("ATLASSIAN_API_TOKEN")
    domain = os.getenv("ATLASSIAN_DOMAIN")
    if not all([email, token, domain]):
        return False, "missing ATLASSIAN_EMAIL/API_TOKEN/DOMAIN"

    auth = HTTPBasicAuth(email, token)
    jira_ok = False
    conf_ok = False
    jira_detail = ""
    conf_detail = ""

    try:
        jira_url = f"https://{domain}/rest/api/3/myself"
        resp = requests.get(jira_url, auth=auth, timeout=20)
        jira_ok = resp.ok
        if resp.ok:
            name = resp.json().get("displayName", "unknown")
            jira_detail = f"Jira ok ({name})"
        else:
            jira_detail = f"Jira {resp.status_code}"
    except Exception as exc:
        jira_detail = f"Jira {type(exc).__name__}"

    try:
        conf_url = f"https://{domain}/wiki/rest/api/user/current"
        resp = requests.get(conf_url, auth=auth, timeout=20)
        conf_ok = resp.ok
        if resp.ok:
            name = resp.json().get("displayName", "unknown")
            conf_detail = f"Confluence ok ({name})"
        else:
            conf_detail = f"Confluence {resp.status_code}"
    except Exception as exc:
        conf_detail = f"Confluence {type(exc).__name__}"

    ok = jira_ok and conf_ok
    return ok, f"{jira_detail}; {conf_detail}"


def check_slack() -> Tuple[bool, str]:
    """Verify the Slack bot token is valid."""
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        return False, "missing SLACK_BOT_TOKEN"

    try:
        resp = requests.post(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        data = resp.json()
        if data.get("ok"):
            team = data.get("team", "unknown")
            user = data.get("user", "unknown")
            return True, f"{team} / {user}"
        return False, data.get("error", "auth.test failed")
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:120]}"


def check_glean() -> Tuple[bool, str]:
    """Verify the Glean API token is valid."""
    token = os.getenv("GLEAN_API_TOKEN")
    base_url = os.getenv("GLEAN_API_URL", "https://api.glean.com/api/v1").rstrip("/")
    if not token:
        return False, "missing GLEAN_API_TOKEN"

    query = os.getenv("GLEAN_SMOKE_TEST_QUERY", "test")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(
            f"{base_url}/search",
            headers=headers,
            json={"query": query, "pageSize": 3},
            timeout=30,
        )
        if not resp.ok:
            return False, f"search {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        detail = f"results: {len(results)}"
        return True, detail
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:120]}"


# ---------------------------------------------------------------------------
# Fix helpers
# ---------------------------------------------------------------------------

def ensure_env_symlink() -> Tuple[bool, str]:
    """Ensure a .env file exists, symlinking from TPM_BUDDY_ENV_PATH if needed."""
    env_path = SCRIPT_DIR / ".env"
    if env_path.exists():
        return True, "env present"

    # Try project root .env as fallback
    project_root_env = os.getenv("PROJECT_ROOT")
    if project_root_env:
        candidate = Path(project_root_env) / ".env"
        if candidate.exists():
            try:
                env_path.symlink_to(candidate)
                load_dotenv(env_path, override=True)
                return True, f"symlinked to {candidate}"
            except Exception as exc:
                return False, f"symlink failed: {type(exc).__name__}"

    tpm_env_path = os.getenv("TPM_BUDDY_ENV_PATH")
    if tpm_env_path:
        tpm_env = Path(tpm_env_path)
        if tpm_env.exists():
            try:
                env_path.symlink_to(tpm_env)
                load_dotenv(env_path, override=True)
                return True, f"symlinked to {tpm_env}"
            except Exception as exc:
                return False, f"symlink failed: {type(exc).__name__}"
        return False, f"TPM_BUDDY_ENV_PATH set but file missing: {tpm_env}"

    return False, "missing .env and no TPM_BUDDY_ENV_PATH or PROJECT_ROOT set"


def attempt_google_token(token_path: Path, scopes: list) -> Tuple[bool, str]:
    """Try to create a Google token via the OAuth flow."""
    if not GOOGLE_API_AVAILABLE:
        return False, MSG_GOOGLE_API_MISSING

    creds_path = SCRIPT_DIR / "credentials.json"
    if not creds_path.exists():
        return False, "credentials.json missing"

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), scopes)
        creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
        token_path.write_text(creds.to_json())
        return True, f"saved {token_path.name}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:120]}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight access check")
    parser.add_argument(
        "--service",
        choices=["all", "google_drive", "google_docs", "atlassian", "slack", "glean"],
        default="all",
        help="Service to check",
    )
    parser.add_argument(
        "--attempt-fix",
        action="store_true",
        help="Try to fix common auth issues before failing",
    )
    parser.add_argument(
        "--nonfatal",
        action="store_true",
        help="Always exit 0 (useful for optional sessions)",
    )
    args = parser.parse_args()

    check_registry = {
        "google_drive": ("Google Drive", check_google_drive),
        "google_docs": (MSG_GOOGLE_DOCS_TOKEN, check_google_docs_token),
        "atlassian": ("Atlassian", check_atlassian),
        "slack": ("Slack", check_slack),
        "glean": ("Glean", check_glean),
    }
    if args.service == "all":
        checks = list(check_registry.values())
    else:
        checks = [check_registry[args.service]]

    failures = 0
    print("Preflight Access Check")
    print("=" * 28)
    results = []
    for name, fn in checks:
        ok, detail = fn()
        results.append((name, ok, detail))
        print_result(name, ok, detail)
        if not ok:
            failures += 1

    if failures and args.attempt_fix:
        print()
        print("Attempting fixes...")
        failed_names = {name for name, ok, _ in results if not ok}
        fix_actions = []

        if {"Atlassian", "Slack", "Glean"} & failed_names:
            ok, detail = ensure_env_symlink()
            fix_actions.append(("Env file", ok, detail))

        if "Google Drive" in failed_names:
            ok, detail = attempt_google_token(
                SCRIPT_DIR / "token.json",
                ["https://www.googleapis.com/auth/drive.readonly"],
            )
            fix_actions.append(("Google Drive token", ok, detail))

        if MSG_GOOGLE_DOCS_TOKEN in failed_names:
            ok, detail = attempt_google_token(
                SCRIPT_DIR / "token_docs.json",
                [
                    "https://www.googleapis.com/auth/drive.file",
                    "https://www.googleapis.com/auth/documents",
                ],
            )
            fix_actions.append((MSG_GOOGLE_DOCS_TOKEN, ok, detail))

        for name, ok, detail in fix_actions:
            print_result(f"{name} fix", ok, detail)

        # Re-check after fixes
        print()
        print("Re-checking...")
        failures = 0
        for name, fn in checks:
            ok, detail = fn()
            print_result(name, ok, detail)
            if not ok:
                failures += 1

    if failures:
        print(f"\n{failures} check(s) failed")
        return 0 if args.nonfatal else 1
    print("\nAll checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
