#!/usr/bin/env python3
"""
Calendar Sync Script for Palimpsest

Fetches calendar events and creates events for task time-blocking.
All configuration is driven by environment variables.

Environment variables:
- ``CALENDAR_ID`` -- primary calendar ID (default ``"primary"``)
- ``TASKS_CALENDAR_ID`` -- calendar for task events (no default, optional)
- ``CALENDAR_TIMEZONE`` -- timezone for events (default ``"UTC"``)
- ``EVENT_PREFIX`` -- prefix for agent-created events (default ``"[PAC]"``)

Usage:
    python calendar_sync.py --fetch          # Fetch events for next 2 weeks
    python calendar_sync.py --fetch-all      # Fetch ALL events (not just program-related)
    python calendar_sync.py --create-event   # Create a test task event
    python calendar_sync.py --list-calendars # List available calendars
    python calendar_sync.py --days 7 --save  # Save 7-day events to markdown
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration from environment
SCRIPT_DIR = Path(__file__).resolve().parent
TOKEN_FILE = SCRIPT_DIR / os.getenv("GOOGLE_TOKEN_FILE", "token.json")
OUTPUT_DIR = Path(os.getenv(
    "PAC_CALENDAR_OUTPUT_DIR",
    str(SCRIPT_DIR.parent.parent / "docs" / "context" / "calendar"),
))

# Calendar settings from env
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")
TASKS_CALENDAR_ID = os.getenv("TASKS_CALENDAR_ID")
CALENDAR_TIMEZONE = os.getenv("CALENDAR_TIMEZONE", "UTC")
EVENT_PREFIX = os.getenv("EVENT_PREFIX", "[PAC]")
DEFAULT_EVENT_DURATION_MINUTES = 30


def get_credentials() -> Optional[Credentials]:
    """Load and return Google credentials, refreshing if needed."""
    if not TOKEN_FILE.exists():
        print(f"[ERROR] Token file not found: {TOKEN_FILE}")
        print("  Run: python google_auth.py")
        return None

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            temp_path = SCRIPT_DIR / "token_temp.json"
            with open(str(temp_path), 'w') as f:
                f.write(creds.to_json())
            shutil.move(str(temp_path), str(TOKEN_FILE))
        except Exception as e:
            print(f"[ERROR] Failed to refresh token: {e}")
            return None

    return creds


def get_calendar_service():
    """Build and return Calendar API service."""
    creds = get_credentials()
    if not creds:
        return None

    try:
        return build('calendar', 'v3', credentials=creds)
    except HttpError as e:
        if 'accessNotConfigured' in str(e):
            print("[ERROR] Calendar API not enabled!")
            print("  Enable at: https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview")
        else:
            print(f"[ERROR] Calendar API error: {e}")
        return None


def list_calendars() -> List[Dict[str, Any]]:
    """List all available calendars."""
    service = get_calendar_service()
    if not service:
        return []

    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])

        print(f"\nFound {len(calendars)} calendars:\n")
        for cal in calendars:
            primary = " (PRIMARY)" if cal.get('primary') else ""
            access = cal.get('accessRole', 'unknown')
            print(f"  - {cal.get('summary', 'Unknown')}{primary}")
            print(f"    ID: {cal.get('id')}")
            print(f"    Access: {access}")
            print()

        return calendars
    except HttpError as e:
        print(f"[ERROR] listing calendars: {e}")
        return []


def fetch_events(
    days_ahead: int = 14,
    calendar_id: Optional[str] = None,
    include_all: bool = False,
) -> List[Dict[str, Any]]:
    """Fetch calendar events for the specified period.

    Parameters
    ----------
    days_ahead : int
        Number of days to look ahead.
    calendar_id : str, optional
        Calendar to fetch from (defaults to ``CALENDAR_ID``).
    include_all : bool
        If *False*, filter to agent-created and program-related events only.
    """
    service = get_calendar_service()
    if not service:
        return []

    cal_id = calendar_id or CALENDAR_ID
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

    try:
        events_result = service.events().list(
            calendarId=cal_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime',
        ).execute()

        events = events_result.get('items', [])

        if not include_all:
            filtered = []
            program_keywords = os.getenv(
                "PAC_CALENDAR_KEYWORDS",
                "sync,planning,review,standup,retro,council,steerco",
            ).split(",")
            program_keywords = [k.strip().lower() for k in program_keywords if k.strip()]

            for event in events:
                summary = event.get('summary', '').lower()
                description = event.get('description', '').lower()

                is_agent = EVENT_PREFIX.lower() in summary
                is_program = any(
                    kw in summary or kw in description
                    for kw in program_keywords
                )

                if is_agent or is_program:
                    filtered.append(event)

            events = filtered

        print(f"\nFound {len(events)} events in next {days_ahead} days")
        return events

    except HttpError as e:
        print(f"[ERROR] fetching events: {e}")
        return []


def format_events_markdown(events: List[Dict[str, Any]]) -> str:
    """Format events as a markdown table."""
    if not events:
        return "_No calendar events found._\n"

    lines = ["| Date | Time | Event | Duration |", "|------|------|-------|----------|"]

    for event in events:
        start = event.get('start', {})
        end = event.get('end', {})

        if 'date' in start:
            date_str = start['date']
            time_str = "All day"
            duration = ""
        else:
            start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
            date_str = start_dt.strftime('%Y-%m-%d')
            time_str = start_dt.strftime('%H:%M')
            duration_mins = int((end_dt - start_dt).total_seconds() / 60)
            duration = f"{duration_mins}m"

        summary = event.get('summary', 'Untitled')
        lines.append(f"| {date_str} | {time_str} | {summary} | {duration} |")

    return "\n".join(lines) + "\n"


def create_task_event(
    title: str,
    description: str = "",
    start_time: Optional[datetime] = None,
    duration_minutes: int = DEFAULT_EVENT_DURATION_MINUTES,
    calendar_id: Optional[str] = None,
    visibility: str = "private",
) -> Optional[Dict[str, Any]]:
    """Create a calendar event for a task.

    Events are created in ``TASKS_CALENDAR_ID`` (if set) or ``CALENDAR_ID``.

    Parameters
    ----------
    title : str
        Event title (will be prefixed with ``EVENT_PREFIX``).
    description : str
        Event description.
    start_time : datetime, optional
        Start time (defaults to tomorrow 9am).
    duration_minutes : int
        Duration in minutes.
    calendar_id : str, optional
        Override target calendar.
    visibility : str
        One of ``"private"``, ``"default"``, ``"public"``.
    """
    service = get_calendar_service()
    if not service:
        return None

    target_cal = calendar_id or TASKS_CALENDAR_ID or CALENDAR_ID

    if start_time is None:
        tomorrow = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        tomorrow += timedelta(days=1)
        start_time = tomorrow

    end_time = start_time + timedelta(minutes=duration_minutes)

    event_body = {
        'summary': f"{EVENT_PREFIX} {title}",
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': CALENDAR_TIMEZONE,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': CALENDAR_TIMEZONE,
        },
        'visibility': visibility,
        'reminders': {
            'useDefault': False,
            'overrides': [],
        },
    }

    try:
        event = service.events().insert(
            calendarId=target_cal,
            body=event_body,
        ).execute()

        print(f"[OK] Created event: {event.get('summary')}")
        print(f"     Link: {event.get('htmlLink')}")
        return event

    except HttpError as e:
        print(f"[ERROR] creating event: {e}")
        return None


def create_events_from_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create calendar events from a list of task dicts.

    Expected task format::

        {
            "title": str,
            "description": str,       # optional
            "due_date": str,           # ISO format, optional
            "priority": str,           # P0-P4, optional
            "duration_minutes": int,   # optional
        }
    """
    created_events = []

    priority_duration = {
        'P0': 60,
        'P1': 45,
        'P2': 30,
        'P3': 30,
        'P4': 15,
    }

    for task in tasks:
        title = task.get('title', 'Untitled Task')
        description = task.get('description', '')
        priority = task.get('priority', 'P2')

        start_time = None
        if 'due_date' in task:
            try:
                start_time = datetime.fromisoformat(task['due_date'].replace('Z', ''))
            except ValueError:
                pass

        duration = task.get('duration_minutes', priority_duration.get(priority, 30))

        event = create_task_event(
            title=title,
            description=f"Priority: {priority}\n\n{description}",
            start_time=start_time,
            duration_minutes=duration,
            visibility="private",
        )

        if event:
            created_events.append(event)

    return created_events


def save_events_to_markdown(
    events: List[Dict[str, Any]],
    filename: str = "calendar_events.md",
) -> None:
    """Save events to a markdown file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename

    content = f"""# Calendar Events

> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> Events: Next 14 days

## Upcoming Events

{format_events_markdown(events)}

---

_Auto-generated by calendar_sync.py_
"""

    temp_path = OUTPUT_DIR / f"temp_{filename}"
    with open(str(temp_path), 'w') as f:
        f.write(content)
    shutil.move(str(temp_path), str(output_path))

    print(f"[OK] Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Calendar sync for Palimpsest')
    parser.add_argument('--fetch', action='store_true', help='Fetch events for next 2 weeks')
    parser.add_argument('--fetch-all', action='store_true', help='Fetch ALL events (not just program-related)')
    parser.add_argument('--list-calendars', action='store_true', help='List available calendars')
    parser.add_argument('--create-event', action='store_true', help='Create a test event')
    parser.add_argument('--days', type=int, default=14, help='Days ahead to fetch')
    parser.add_argument('--save', action='store_true', help='Save events to markdown')

    args = parser.parse_args()

    if args.list_calendars:
        list_calendars()
    elif args.fetch or args.fetch_all:
        events = fetch_events(days_ahead=args.days, include_all=args.fetch_all)

        if events:
            print("\nEvents:")
            for event in events[:10]:
                start = event.get('start', {})
                date = start.get('dateTime', start.get('date', 'Unknown'))[:16]
                print(f"  - {date} - {event.get('summary', 'Untitled')}")

            if len(events) > 10:
                print(f"  ... and {len(events) - 10} more")

        if args.save:
            save_events_to_markdown(events)
    elif args.create_event:
        create_task_event(
            title="Test Task Event",
            description="Test event created by calendar_sync.py",
            visibility="private",
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
