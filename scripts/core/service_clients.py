#!/usr/bin/env python3
"""
Service Clients for Palimpsest

Unified interface for all external services:
- Google Drive (docs, sheets)
- Atlassian (Confluence, Jira)
- Slack
- Glean
- GitHub

Each client gracefully handles missing credentials and is fully
config-driven via environment variables.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

# Load environment
SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / '.env')


class ServiceStatus:
    """Track service availability."""

    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}

    def set(self, name: str, available: bool, message: str = "") -> None:
        self.services[name] = {"available": available, "message": message}

    def is_available(self, name: str) -> bool:
        return self.services.get(name, {}).get("available", False)

    def summary(self) -> str:
        lines = ["Service Status:"]
        for name, info in self.services.items():
            icon = "OK" if info["available"] else "FAIL"
            msg = f" - {info['message']}" if info["message"] else ""
            lines.append(f"  [{icon}] {name}{msg}")
        return "\n".join(lines)


status = ServiceStatus()


# =============================================================================
# GOOGLE DRIVE
# =============================================================================

def get_google_drive_client():
    """Get Google Drive client with auto-refresh.

    Looks for ``token.json`` in SCRIPT_DIR.  If the token is expired it will
    be refreshed automatically and the file re-written.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        token_path = SCRIPT_DIR / 'token.json'
        if not token_path.exists():
            status.set("google_drive", False, "No token.json")
            return None

        creds = Credentials.from_authorized_user_file(
            str(token_path),
            ['https://www.googleapis.com/auth/drive.readonly']
        )

        # Auto-refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)
        status.set("google_drive", True, "Connected")
        return service

    except Exception as e:
        status.set("google_drive", False, str(e)[:50])
        return None


# =============================================================================
# ATLASSIAN (Confluence / Jira)
# =============================================================================

class AtlassianClient:
    """Client for Confluence and Jira APIs.

    Environment variables (all required, no defaults):
    - ``ATLASSIAN_EMAIL``
    - ``ATLASSIAN_API_TOKEN``
    - ``ATLASSIAN_DOMAIN``
    """

    def __init__(self):
        self.email = os.getenv('ATLASSIAN_EMAIL')
        self.token = os.getenv('ATLASSIAN_API_TOKEN')
        self.domain = os.getenv('ATLASSIAN_DOMAIN')

        if not all([self.email, self.token, self.domain]):
            status.set("atlassian", False, "Missing credentials in .env")
            self.available = False
        else:
            status.set("atlassian", True, f"Domain: {self.domain}")
            self.available = True

    def _request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """Make authenticated request using HTTP Basic Auth."""
        if not self.available:
            return None

        import requests
        from requests.auth import HTTPBasicAuth

        auth = HTTPBasicAuth(self.email, self.token)
        headers = kwargs.pop("headers", {})
        headers.setdefault("Accept", "application/json")
        response = requests.request(method, url, auth=auth, headers=headers, **kwargs)

        if response.ok:
            return response.json() if response.text else {}
        return None

    # ---- Confluence --------------------------------------------------------

    def get_confluence_page(self, page_id: str) -> Optional[Dict]:
        """Get Confluence page content."""
        url = f"https://{self.domain}/wiki/rest/api/content/{page_id}"
        return self._request('GET', url, params={'expand': 'body.storage,version'})

    def search_confluence(self, cql: str, limit: int = 50, start: int = 0) -> Optional[Dict]:
        """Search Confluence with CQL."""
        url = f"https://{self.domain}/wiki/rest/api/content/search"
        params = {
            "cql": cql,
            "limit": limit,
            "start": start,
            "expand": "version,space",
        }
        return self._request('GET', url, params=params)

    def list_confluence_pages(self, space_key: str, limit: int = 50, start: int = 0) -> Optional[Dict]:
        """List Confluence pages in a space."""
        url = f"https://{self.domain}/wiki/rest/api/content"
        params = {
            "spaceKey": space_key,
            "type": "page",
            "limit": limit,
            "start": start,
            "expand": "version,space",
        }
        return self._request('GET', url, params=params)

    def list_confluence_pages_all(self, space_key: str, limit: int = 50) -> List[Dict]:
        """List all pages in a Confluence space (handles pagination)."""
        pages: List[Dict] = []
        start = 0

        while True:
            result = self.list_confluence_pages(space_key, limit=limit, start=start)
            if not result:
                break
            batch = result.get("results", [])
            pages.extend(batch)
            if len(batch) < limit:
                break
            start += limit
        return pages

    def search_confluence_all(self, cql: str, limit: int = 50, max_results: int = 500) -> List[Dict]:
        """Search Confluence with CQL and paginate through all results."""
        results: List[Dict] = []
        start = 0

        while True:
            response = self.search_confluence(cql, limit=limit, start=start)
            if not response:
                break
            batch = response.get("results", [])
            results.extend(batch)
            if len(batch) < limit or len(results) >= max_results:
                break
            start += limit
        return results[:max_results]

    def update_confluence_page(self, page_id: str, title: str, content: str, version: int) -> bool:
        """Update Confluence page content."""
        url = f"https://{self.domain}/wiki/rest/api/content/{page_id}"
        data = {
            "version": {"number": version},
            "title": title,
            "type": "page",
            "body": {"storage": {"value": content, "representation": "storage"}},
        }
        result = self._request(
            'PUT', url, json=data,
            headers={'Content-Type': 'application/json'},
        )
        return result is not None

    # ---- Jira --------------------------------------------------------------

    def get_jira_issue(self, issue_key: str, fields: Optional[str] = None) -> Optional[Dict]:
        """Get Jira issue by key."""
        url = f"https://{self.domain}/rest/api/3/issue/{issue_key}"
        params = {"fields": fields} if fields else None
        return self._request('GET', url, params=params)

    def search_jira(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Search Jira issues with JQL."""
        url = f"https://{self.domain}/rest/api/3/search"
        result = self._request('GET', url, params={'jql': jql, 'maxResults': max_results})
        return result.get('issues', []) if result else []


def get_atlassian_client() -> Optional[AtlassianClient]:
    """Get Atlassian client (returns *None* when credentials are missing)."""
    client = AtlassianClient()
    return client if client.available else None


# =============================================================================
# SLACK
# =============================================================================

class SlackClient:
    """Client for Slack API.

    Environment variable: ``SLACK_BOT_TOKEN``
    """

    def __init__(self):
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')

        if not self.bot_token:
            status.set("slack", False, "No SLACK_BOT_TOKEN in .env")
            self.available = False
        else:
            status.set("slack", True, "Bot token configured")
            self.available = True

    def _request(self, method: str, **kwargs) -> Optional[Dict]:
        """Make Slack Web API request."""
        if not self.available:
            return None

        import requests

        url = f"https://slack.com/api/{method}"
        headers = {"Authorization": f"Bearer {self.bot_token}"}

        response = requests.post(url, headers=headers, json=kwargs)
        data = response.json()

        if data.get('ok'):
            return data
        return None

    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get user info by Slack user ID."""
        result = self._request('users.info', user=user_id)
        return result.get('user') if result else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Look up user by email."""
        result = self._request('users.lookupByEmail', email=email)
        return result.get('user') if result else None

    def list_channels(self, types: str = "public_channel,private_channel") -> List[Dict]:
        """List channels the bot can see."""
        result = self._request('conversations.list', types=types, limit=200)
        return result.get('channels', []) if result else []

    def get_channel_history(self, channel_id: str, limit: int = 100) -> List[Dict]:
        """Get channel message history."""
        result = self._request('conversations.history', channel=channel_id, limit=limit)
        return result.get('messages', []) if result else []

    def get_thread_replies(self, channel_id: str, thread_ts: str, limit: int = 100) -> List[Dict]:
        """Get thread replies for a message."""
        result = self._request(
            'conversations.replies',
            channel=channel_id,
            ts=thread_ts,
            limit=limit,
        )
        return result.get('messages', []) if result else []

    def post_message(self, channel: str, text: str, **kwargs) -> bool:
        """Post a message to a channel."""
        result = self._request('chat.postMessage', channel=channel, text=text, **kwargs)
        return result is not None


def get_slack_client() -> Optional[SlackClient]:
    """Get Slack client."""
    client = SlackClient()
    return client if client.available else None


# =============================================================================
# GLEAN
# =============================================================================

class GleanClient:
    """Client for Glean API.

    Environment variables:
    - ``GLEAN_API_TOKEN`` (required)
    - ``GLEAN_API_URL`` or ``GLEAN_INSTANCE`` (optional, used to resolve base URL)
    - ``GLEAN_WORKSPACE`` / ``GLEAN_SLACK_WORKSPACE`` (optional default workspace)
    - ``GLEAN_SLACK_DOMAIN`` (optional domain filter for Slack results)
    - ``GLEAN_SLACK_CHANNEL_FILTER`` (optional, default ``channelname``)
    """

    def __init__(self):
        self.api_token = os.getenv('GLEAN_API_TOKEN')
        self.base_url = self._resolve_base_url()
        self.default_workspace = os.getenv('GLEAN_WORKSPACE') or os.getenv('GLEAN_SLACK_WORKSPACE')
        self.slack_domain = os.getenv('GLEAN_SLACK_DOMAIN')
        self.channel_filter_key = os.getenv('GLEAN_SLACK_CHANNEL_FILTER', 'channelname')

        if not self.api_token:
            status.set("glean", False, "No GLEAN_API_TOKEN in .env")
            self.available = False
        else:
            status.set("glean", True, "API token configured")
            self.available = True

    @staticmethod
    def _resolve_base_url() -> str:
        api_url = os.getenv('GLEAN_API_URL')
        if api_url:
            return api_url.rstrip("/")
        instance = os.getenv('GLEAN_INSTANCE')
        if instance:
            return f"https://{instance}-be.glean.com/rest/api/v1"
        return "https://api.glean.com/api/v1"

    # ---- filter helpers ----------------------------------------------------

    @staticmethod
    def _format_filter_value(value: str) -> str:
        value = value.strip()
        if not value:
            return value
        if value.startswith('"') and value.endswith('"'):
            return value
        if any(char.isspace() for char in value):
            return f'"{value}"'
        return value

    @classmethod
    def _format_filter(cls, key: str, value: str) -> str:
        normalized = cls._format_filter_value(str(value))
        if not normalized:
            return ""
        return f"{key}:{normalized}"

    @classmethod
    def _parse_dynamic_filters(cls, raw_filters: Optional[str]) -> List[str]:
        if not raw_filters:
            return []
        tokens: List[str] = []
        for part in raw_filters.split("|"):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                key, value = part.split(":", 1)
                tokens.append(cls._format_filter(key.strip(), value.strip()))
            else:
                tokens.append(part)
        return [token for token in tokens if token]

    # ---- query builder -----------------------------------------------------

    def build_query(
        self,
        base_query: str,
        app: Optional[str] = None,
        workspace: Optional[str] = None,
        channel: Optional[str] = None,
        owner: Optional[str] = None,
        from_: Optional[str] = None,
        updated: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        doc_type: Optional[str] = None,
        dynamic_filters: Optional[str] = None,
        raw_filters: Optional[str] = None,
        channel_key: Optional[str] = None,
    ) -> str:
        """Build a Glean search query string with optional filters.

        Parameters
        ----------
        base_query : str
            The core search text.
        app, workspace, channel, owner, from_, updated, after, before, doc_type
            Common Glean filter fields.
        dynamic_filters : str, optional
            Pipe-separated ``key:value`` pairs (e.g. ``"owner:jane|type:doc"``).
        raw_filters : str, optional
            Raw suffix appended verbatim to the query.
        channel_key : str, optional
            Override the channel filter key (defaults to ``self.channel_filter_key``).
        """
        query = base_query.strip() if base_query else "*"
        tokens: List[str] = []

        if app:
            tokens.append(self._format_filter("app", app))
        if workspace:
            tokens.append(self._format_filter("workspace", workspace))
        if channel:
            key = channel_key or self.channel_filter_key
            tokens.append(self._format_filter(key, channel.lstrip("#")))
        if owner:
            tokens.append(self._format_filter("owner", owner))
        if from_:
            tokens.append(self._format_filter("from", from_))
        if updated:
            tokens.append(self._format_filter("updated", updated))
        if after:
            tokens.append(self._format_filter("after", after))
        if before:
            tokens.append(self._format_filter("before", before))
        if doc_type:
            tokens.append(self._format_filter("type", doc_type))

        tokens.extend(self._parse_dynamic_filters(dynamic_filters))
        if raw_filters:
            tokens.append(raw_filters)

        return " ".join([query] + [t for t in tokens if t])

    # ---- domain filtering --------------------------------------------------

    @staticmethod
    def _filter_results_by_domain(results: List[Dict], domain: Optional[str]) -> List[Dict]:
        if not domain:
            return results
        filtered: List[Dict] = []
        for result in results:
            doc = result.get("document", result)
            url = (
                doc.get("url")
                or doc.get("docUrl")
                or doc.get("resource", {}).get("url")
                or result.get("url", "")
            )
            if domain in url:
                filtered.append(result)
        return filtered

    # ---- API calls ---------------------------------------------------------

    def _request(self, endpoint: str, method: str = 'POST', **kwargs) -> Optional[Dict]:
        """Make Glean API request."""
        if not self.available:
            return None

        import requests

        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        response = requests.request(method, url, headers=headers, json=kwargs, timeout=30)

        if response.ok:
            return response.json()
        return None

    def search(
        self,
        query: str,
        page_size: int = 10,
        app: Optional[str] = None,
        workspace: Optional[str] = None,
        channel: Optional[str] = None,
        owner: Optional[str] = None,
        from_: Optional[str] = None,
        updated: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        doc_type: Optional[str] = None,
        dynamic_filters: Optional[str] = None,
        raw_filters: Optional[str] = None,
        slack_domain: Optional[str] = None,
    ) -> List[Dict]:
        """Search Glean with optional filters."""
        if app == "slack" and not workspace:
            workspace = self.default_workspace

        built_query = self.build_query(
            base_query=query,
            app=app,
            workspace=workspace,
            channel=channel,
            owner=owner,
            from_=from_,
            updated=updated,
            after=after,
            before=before,
            doc_type=doc_type,
            dynamic_filters=dynamic_filters,
            raw_filters=raw_filters,
        )

        result = self._request('search', query=built_query, pageSize=page_size)
        results = result.get('results', []) if result else []

        domain_filter = slack_domain or (self.slack_domain if app == "slack" else None)
        return self._filter_results_by_domain(results, domain_filter)

    def search_slack(
        self,
        query: str,
        channels: Optional[List[str]] = None,
        workspace: Optional[str] = None,
        page_size: int = 10,
        updated: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        slack_domain: Optional[str] = None,
    ) -> List[Dict]:
        """Search Slack content via Glean."""
        raw_filters = None
        if channels:
            key = self.channel_filter_key
            channel_tokens = [
                self._format_filter(key, channel.lstrip("#"))
                for channel in channels
                if channel
            ]
            if channel_tokens:
                raw_filters = f"({' OR '.join(channel_tokens)})"

        return self.search(
            query=query,
            page_size=page_size,
            app="slack",
            workspace=workspace,
            updated=updated,
            after=after,
            before=before,
            raw_filters=raw_filters,
            slack_domain=slack_domain,
        )

    def get_person(self, email: str) -> Optional[Dict]:
        """Get person info by email."""
        result = self._request('people', emails=[email])
        people = result.get('people', []) if result else []
        return people[0] if people else None

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document by ID."""
        return self._request(f'documents/{doc_id}', method='GET')


def get_glean_client() -> Optional[GleanClient]:
    """Get Glean client."""
    client = GleanClient()
    return client if client.available else None


# =============================================================================
# GITHUB
# =============================================================================

class GitHubClient:
    """Client for GitHub API.

    Environment variable: ``GITHUB_TOKEN``
    """

    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')

        if not self.token:
            status.set("github", False, "No GITHUB_TOKEN in .env")
            self.available = False
        else:
            status.set("github", True, "Token configured")
            self.available = True

    def _request(self, endpoint: str, method: str = 'GET', **kwargs) -> Optional[Dict]:
        """Make GitHub API request."""
        if not self.available:
            return None

        import requests

        url = f"https://api.github.com/{endpoint}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.request(method, url, headers=headers, **kwargs)

        if response.ok:
            return response.json()
        return None

    def get_repo(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository info."""
        return self._request(f'repos/{owner}/{repo}')

    def list_issues(self, owner: str, repo: str, state: str = 'open') -> List[Dict]:
        """List repository issues."""
        result = self._request(f'repos/{owner}/{repo}/issues', params={'state': state})
        return result if isinstance(result, list) else []

    def get_user(self) -> Optional[Dict]:
        """Get authenticated user."""
        return self._request('user')


def get_github_client() -> Optional[GitHubClient]:
    """Get GitHub client."""
    client = GitHubClient()
    return client if client.available else None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def check_all_services() -> Dict[str, bool]:
    """Initialize and check all services."""
    results = {}

    results['google_drive'] = get_google_drive_client() is not None
    results['atlassian'] = get_atlassian_client() is not None
    results['slack'] = get_slack_client() is not None
    results['glean'] = get_glean_client() is not None
    results['github'] = get_github_client() is not None

    return results


def print_status() -> None:
    """Print status of all services."""
    check_all_services()
    print(status.summary())


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Check service connectivity")
    parser.add_argument(
        '--service',
        choices=['drive', 'atlassian', 'slack', 'glean', 'github', 'all'],
        default='all',
        help="Service to check",
    )
    args = parser.parse_args()

    print("PAC Service Status Check")
    print("=" * 40)

    if args.service == 'all':
        check_all_services()
        print(status.summary())
    else:
        service_map = {
            'drive': ('google_drive', get_google_drive_client),
            'atlassian': ('atlassian', get_atlassian_client),
            'slack': ('slack', get_slack_client),
            'glean': ('glean', get_glean_client),
            'github': ('github', get_github_client),
        }
        name, func = service_map[args.service]
        func()
        print(status.summary())
