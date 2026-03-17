#!/usr/bin/env python3
"""
Google OAuth Authentication Script

Authenticates with multiple Google APIs and saves a unified token.
Run this locally to get tokens for:
- Google Drive
- Google Sheets
- Gmail
- Google Calendar
- Google Tasks
- People API (Contacts + Directory)

All paths are config-driven -- no hardcoded project references.
"""

import os
import sys
import json
import shutil
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# All scopes we want access to
SCOPES = [
    # Drive & Sheets
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets',

    # Profile - required for People API
    'https://www.googleapis.com/auth/userinfo.profile',

    # Contacts
    'https://www.googleapis.com/auth/contacts.readonly',

    # Workspace Directory
    'https://www.googleapis.com/auth/directory.readonly',

    # Gmail
    'https://www.googleapis.com/auth/gmail.modify',

    # Calendar
    'https://www.googleapis.com/auth/calendar',

    # Tasks
    'https://www.googleapis.com/auth/tasks',
]

SCRIPT_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = SCRIPT_DIR / "credentials.json"
TOKEN_FILE = SCRIPT_DIR / "token.json"


def _load_existing_token():
    """Load and validate an existing token file, or return None."""
    if not TOKEN_FILE.exists():
        return None

    print(f"Found existing token: {TOKEN_FILE}")
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.scopes:
        missing_scopes = set(SCOPES) - set(creds.scopes)
        if missing_scopes:
            print(f"Token missing scopes: {missing_scopes}")
            print("Will re-authenticate to get all scopes...")
            return None

    return creds


def _refresh_token(creds):
    """Attempt to refresh expired credentials, return None on failure."""
    if not (creds and creds.expired and creds.refresh_token):
        return creds
    print("Refreshing expired token...")
    try:
        creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Refresh failed: {e}")
        return None


def _run_oauth_flow():
    """Run the interactive OAuth flow and save the token."""
    if not CREDENTIALS_FILE.exists():
        print(f"Missing credentials file: {CREDENTIALS_FILE}")
        print()
        print("To get credentials:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop app)")
        print("3. Download JSON and save as 'credentials.json'")
        return None

    print("Starting OAuth flow...")
    print("A browser window will open for authentication.")
    print(f"Requesting {len(SCOPES)} scopes:")
    for scope in SCOPES:
        print(f"  - {scope.split('/')[-1]}")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES,
    )

    creds = flow.run_local_server(
        port=0,
        prompt='consent',
        access_type='offline',
    )

    # Save token via temp file
    token_data = creds.to_json()
    temp_path = SCRIPT_DIR / "token_temp.json"
    with open(str(temp_path), 'w') as f:
        f.write(token_data)
    shutil.move(str(temp_path), str(TOKEN_FILE))
    print(f"Token saved to: {TOKEN_FILE}")

    return creds


def authenticate():
    """Run OAuth flow and save token.

    Returns valid ``Credentials`` or *None* on failure.
    """
    creds = _load_existing_token()
    creds = _refresh_token(creds)

    if not creds or not creds.valid:
        creds = _run_oauth_flow()

    return creds


def test_apis(creds):
    """Test that we can access each API.

    Returns a dict mapping API name to a boolean success flag.
    """
    print()
    print("Testing API access...")
    print()

    from googleapiclient.discovery import build

    results = {}

    # Drive
    try:
        drive = build('drive', 'v3', credentials=creds)
        about = drive.about().get(fields="user").execute()
        user = about.get('user', {})
        print(f"[OK]   Drive API: Connected as {user.get('displayName', 'Unknown')}")
        results['drive'] = True
    except Exception as e:
        print(f"[FAIL] Drive API: {e}")
        results['drive'] = False

    # Sheets
    try:
        build('sheets', 'v4', credentials=creds)
        print("[OK]   Sheets API: Ready")
        results['sheets'] = True
    except Exception as e:
        print(f"[FAIL] Sheets API: {e}")
        results['sheets'] = False

    # Gmail
    try:
        gmail = build('gmail', 'v1', credentials=creds)
        profile = gmail.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')
        total = profile.get('messagesTotal', 0)
        print(f"[OK]   Gmail API: Connected as {email} ({total:,} messages)")
        results['gmail'] = True
    except Exception as e:
        print(f"[FAIL] Gmail API: {e}")
        results['gmail'] = False

    # Calendar
    try:
        calendar = build('calendar', 'v3', credentials=creds)
        calendar_list = calendar.calendarList().list(maxResults=5).execute()
        calendars = calendar_list.get('items', [])
        primary = next((c for c in calendars if c.get('primary')), None)
        if primary:
            print(f"[OK]   Calendar API: Primary calendar: {primary.get('summary', 'Unknown')}")
        else:
            print(f"[OK]   Calendar API: Found {len(calendars)} calendars")
        results['calendar'] = True
    except Exception as e:
        print(f"[FAIL] Calendar API: {e}")
        results['calendar'] = False

    # Tasks
    try:
        tasks = build('tasks', 'v1', credentials=creds)
        task_lists = tasks.tasklists().list(maxResults=10).execute()
        lists = task_lists.get('items', [])
        print(f"[OK]   Tasks API: Found {len(lists)} task lists")
        for tl in lists[:3]:
            print(f"         - {tl['title']}")
        results['tasks'] = True
    except Exception as e:
        print(f"[FAIL] Tasks API: {e}")
        results['tasks'] = False

    # People API
    try:
        people = build('people', 'v1', credentials=creds)
        profile = people.people().get(
            resourceName='people/me',
            personFields='names,emailAddresses',
        ).execute()
        name = profile.get('names', [{}])[0].get('displayName', 'Unknown')
        print(f"[OK]   People API: Profile access OK ({name})")
        results['people'] = True

        # Contacts
        try:
            connections = people.people().connections().list(
                resourceName='people/me',
                pageSize=10,
                personFields='names,emailAddresses',
            ).execute()
            count = len(connections.get('connections', []))
            print(f"[OK]   Contacts: Found {count} contacts")
            results['contacts'] = True
        except Exception as e:
            print(f"[WARN] Contacts: {e}")
            results['contacts'] = False

        # Directory
        try:
            directory = people.people().listDirectoryPeople(
                readMask='names,emailAddresses,organizations',
                sources=['DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE'],
                pageSize=10,
            ).execute()
            count = len(directory.get('people', []))
            print(f"[OK]   Directory: Found {count} domain users")
            results['directory'] = True
        except Exception as e:
            print(f"[WARN] Directory: {e}")
            results['directory'] = False

    except Exception as e:
        print(f"[FAIL] People API: {e}")
        results['people'] = False

    return results


def main():
    print("=" * 60)
    print("Google API Authentication")
    print("=" * 60)
    print()

    creds = authenticate()

    if creds:
        print()
        print("=" * 60)
        print("Token Info")
        print("=" * 60)
        print(f"Token file: {TOKEN_FILE}")
        print(f"Valid: {creds.valid}")
        print(f"Expired: {creds.expired}")
        print(f"Has refresh token: {bool(creds.refresh_token)}")
        print("Scopes granted:")
        for scope in (creds.scopes or []):
            print(f"  - {scope.split('/')[-1]}")

        print()
        print("=" * 60)
        results = test_apis(creds)

        print()
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        working = sum(1 for v in results.values() if v)
        print(f"{working}/{len(results)} APIs accessible")
    else:
        print()
        print("Authentication failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
