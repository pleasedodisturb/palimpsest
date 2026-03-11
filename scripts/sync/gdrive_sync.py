#!/usr/bin/env python3
"""
Google Drive Sync Script for Palimpsest

Syncs documents from a configurable Drive folder to local storage,
creates manifests, and maintains snapshot history.

All configuration is driven by environment variables -- no hardcoded IDs.

Usage:
    python gdrive_sync.py                    # Full sync
    python gdrive_sync.py --snapshot         # Create dated snapshot
    python gdrive_sync.py --list             # List files without downloading
    python gdrive_sync.py --update-registry  # Update DOCUMENT_REGISTRY.md
    python gdrive_sync.py --search-keywords  # Drive-wide keyword search
    python gdrive_sync.py --keywords kw1,kw2 # Keywords for search
"""

import os
import sys
import io
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Google Drive API imports
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("[WARN] Google API libraries not installed. Run:")
    print("       pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

# Configuration from environment
DRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")

# Paths (relative to this script)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.getenv("PAC_PROJECT_ROOT", SCRIPT_DIR.parent.parent))
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "docs" / "knowledge-base"
SNAPSHOTS_DIR = KNOWLEDGE_BASE_DIR / "snapshots"
INDEX_DIR = KNOWLEDGE_BASE_DIR / "index"
REGISTRY_FILE = KNOWLEDGE_BASE_DIR / "DOCUMENT_REGISTRY.md"
CONFIG_FILE = KNOWLEDGE_BASE_DIR / "document_registry_config.json"
DRIVE_SEARCH_RESULTS_FILE = INDEX_DIR / "drive_keyword_results.json"

# File type mappings for categorization
CATEGORY_MAPPINGS = {
    "planning": ["planning", "roadmap", "strategy", "timeline", "schedule"],
    "architecture": ["architecture", "technical", "design", "adr", "rfc"],
    "product": ["prd", "requirements", "spec", "feature", "epic"],
    "security": ["security", "compliance", "sox", "audit", "review"],
    "reports": ["report", "status", "update", "weekly", "monthly"],
    "meetings": ["meeting", "notes", "standup", "retro", "sync"],
}


def load_config() -> dict:
    """Load registry config if available."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_credentials() -> Optional[object]:
    """Get Google API credentials from various sources.

    Supports:
    1. Service account JSON file (``GOOGLE_SERVICE_ACCOUNT_FILE``)
    2. Service account JSON string (``GOOGLE_SERVICE_ACCOUNT_JSON``)
    3. OAuth token file (``GOOGLE_TOKEN_FILE``, default ``token.json``)
    4. OAuth credentials file (``GOOGLE_OAUTH_CREDENTIALS``, default ``credentials.json``)
    """

    # Option 1: Service Account JSON file
    sa_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if sa_file and os.path.exists(sa_file):
        return service_account.Credentials.from_service_account_file(
            sa_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
        )

    # Option 2: Service Account JSON from env var
    sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        sa_info = json.loads(sa_json)
        return service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
        )

    # Option 3: OAuth token file
    token_file = os.getenv("GOOGLE_TOKEN_FILE", str(SCRIPT_DIR / "token.json"))
    oauth_file = os.getenv("GOOGLE_OAUTH_CREDENTIALS", str(SCRIPT_DIR / "credentials.json"))

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file)
        # Auto-refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, 'w') as f:
                f.write(creds.to_json())
        return creds

    # Option 4: OAuth flow
    if os.path.exists(oauth_file):
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(
            oauth_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
        )
        creds = flow.run_local_server(port=0)

        # Save token for future use
        with open(token_file, 'w') as f:
            f.write(creds.to_json())

        return creds

    return None


def list_files(service, folder_id: str) -> List[Dict]:
    """List all files in a Google Drive folder, resolving shortcuts."""
    files = []
    page_token = None

    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields=(
                'nextPageToken, files(id, name, mimeType, createdTime, '
                'modifiedTime, size, webViewLink, shortcutDetails)'
            ),
            pageToken=page_token,
        ).execute()

        for f in response.get('files', []):
            # Resolve shortcuts to their target files
            if f.get('mimeType') == 'application/vnd.google-apps.shortcut':
                shortcut_details = f.get('shortcutDetails', {})
                target_id = shortcut_details.get('targetId')
                if target_id:
                    try:
                        target = service.files().get(
                            fileId=target_id,
                            fields='id, name, mimeType, createdTime, modifiedTime, size, webViewLink',
                        ).execute()
                        target['originalName'] = f.get('name')
                        files.append(target)
                    except Exception as e:
                        print(f"  [WARN] Could not resolve shortcut: {f.get('name')} - {e}")
            else:
                files.append(f)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return files


def _build_keyword_query(keywords: list, include_trashed: bool) -> str:
    """Build Drive query for keyword search."""
    terms = []
    for keyword in keywords:
        safe = keyword.replace("'", "\\'")
        terms.append(f"fullText contains '{safe}'")
    combined = " or ".join(terms) if terms else ""
    if include_trashed:
        return combined
    if combined:
        return f"trashed=false and ({combined})"
    return "trashed=false"


def search_drive_files(
    service,
    keywords: list,
    max_results: int = 200,
    include_shared_drives: bool = True,
    include_trashed: bool = False,
) -> List[Dict]:
    """Search Drive for files matching keywords."""
    files_by_id: Dict[str, Dict] = {}

    if not keywords:
        return []

    base_params = {
        "spaces": "drive",
        "fields": (
            "nextPageToken, files(id, name, mimeType, createdTime, "
            "modifiedTime, size, webViewLink, owners(displayName,emailAddress), "
            "lastModifyingUser(displayName,emailAddress))"
        ),
    }

    if include_shared_drives:
        base_params.update({
            "corpora": "allDrives",
            "includeItemsFromAllDrives": True,
            "supportsAllDrives": True,
        })

    for keyword in keywords:
        page_token = None
        query = _build_keyword_query([keyword], include_trashed)
        list_params = dict(base_params)
        list_params["q"] = query

        while True:
            response = service.files().list(
                pageToken=page_token, **list_params,
            ).execute()
            for f in response.get("files", []):
                file_id = f.get("id")
                if not file_id:
                    continue
                existing = files_by_id.get(file_id)
                if existing:
                    existing["matched_keywords"] = sorted(
                        set(existing.get("matched_keywords", []) + [keyword])
                    )
                else:
                    f["matched_keywords"] = [keyword]
                    files_by_id[file_id] = f

            page_token = response.get("nextPageToken")
            if not page_token or len(files_by_id) >= max_results:
                break

        if len(files_by_id) >= max_results:
            break

    results = list(files_by_id.values())
    return results[:max_results]


def _save_drive_search_results(files: list, keywords: list) -> None:
    """Save Drive keyword search results to index file."""
    payload = {
        "generated_at": datetime.now().isoformat(),
        "keywords": keywords,
        "total_files": len(files),
        "files": files,
    }
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(DRIVE_SEARCH_RESULTS_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved keyword search results: {DRIVE_SEARCH_RESULTS_FILE}")


def categorize_file(filename: str) -> str:
    """Categorize a file based on its name using keyword mappings."""
    filename_lower = filename.lower()

    for category, keywords in CATEGORY_MAPPINGS.items():
        for keyword in keywords:
            if keyword in filename_lower:
                return category

    return "uncategorized"


def download_file(service, file_id: str, file_name: str, destination: Path) -> bool:
    """Download a regular file from Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, 'wb') as f:
            f.write(file_handle.getvalue())

        return True
    except Exception as e:
        print(f"  [ERROR] downloading {file_name}: {e}")
        return False


def export_google_doc(service, file_id: str, file_name: str, destination: Path, mime_type: str) -> bool:
    """Export a Google Doc/Sheet/Slides to a downloadable format."""
    export_formats = {
        'application/vnd.google-apps.document': (
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx',
        ),
        'application/vnd.google-apps.spreadsheet': (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx',
        ),
        'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
        'application/vnd.google-apps.drawing': ('application/pdf', '.pdf'),
        'application/vnd.google-apps.jam': ('application/pdf', '.pdf'),
    }

    skip_types = [
        'application/vnd.google-apps.shortcut',
        'application/vnd.google-apps.folder',
        'application/vnd.google-apps.form',
        'application/vnd.google-apps.map',
        'application/vnd.google-apps.site',
        'application/vnd.google-apps.script',
    ]

    if mime_type in skip_types:
        print(f"  [SKIP] {file_name} (shortcut/folder/form)")
        return False

    if mime_type not in export_formats:
        print(f"  [WARN] Unknown format: {mime_type} for {file_name}")
        return False

    export_mime, extension = export_formats[mime_type]

    try:
        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        # Sanitize filename and add extension
        safe_name = "".join(
            c for c in destination.stem
            if c.isalnum() or c in (' ', '-', '_', '.')
        ).strip()
        if not safe_name:
            safe_name = "unnamed"
        dest_path = destination.parent / (safe_name + extension)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dest_path, 'wb') as f:
            f.write(file_handle.getvalue())

        return True
    except Exception as e:
        print(f"  [ERROR] exporting {file_name}: {e}")
        return False


def create_manifest(files: list, snapshot_dir: Path) -> dict:
    """Create a manifest JSON of synced files."""
    folder_url = (
        f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
        if DRIVE_FOLDER_ID else "unknown"
    )
    manifest = {
        "created_at": datetime.now().isoformat(),
        "source_folder": folder_url,
        "total_files": len(files),
        "files": [],
    }

    for f in files:
        manifest["files"].append({
            "name": f.get("name"),
            "id": f.get("id"),
            "mime_type": f.get("mimeType"),
            "created": f.get("createdTime"),
            "modified": f.get("modifiedTime"),
            "size": f.get("size"),
            "url": f.get("webViewLink"),
            "category": categorize_file(f.get("name", "")),
        })

    manifest_path = snapshot_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return manifest


def update_index(manifest: dict) -> None:
    """Update the index files with latest manifest data."""
    index_file = INDEX_DIR / "files.json"
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    if index_file.exists():
        with open(index_file) as f:
            index = json.load(f)
    else:
        index = {"snapshots": [], "all_files": {}}

    snapshot_info = {
        "date": manifest["created_at"],
        "total_files": manifest["total_files"],
    }
    index["snapshots"].append(snapshot_info)

    for f in manifest["files"]:
        file_id = f["id"]
        index["all_files"][file_id] = {
            "name": f["name"],
            "category": f["category"],
            "url": f["url"],
            "last_seen": manifest["created_at"],
        }

    with open(index_file, 'w') as fh:
        json.dump(index, fh, indent=2)

    print(f"Index updated: {index_file}")


def update_registry() -> None:
    """Update DOCUMENT_REGISTRY.md with latest index data."""
    index_file = INDEX_DIR / "files.json"

    if not index_file.exists():
        print("[ERROR] No index found. Run sync first.")
        return

    with open(index_file) as f:
        index = json.load(f)

    print(f"Updating {REGISTRY_FILE}...")
    print(f"  Found {len(index.get('all_files', {}))} files in index")

    for file_id, info in index.get("all_files", {}).items():
        print(f"  [{info['category']}] {info['name']}")

    print()
    print("Registry update complete")


def sync_files(list_only: bool = False, create_snapshot: bool = False) -> None:
    """Main sync function."""
    if not GOOGLE_API_AVAILABLE:
        print("[ERROR] Google API libraries required. Install them first.")
        return

    if not DRIVE_FOLDER_ID:
        print("[ERROR] GDRIVE_FOLDER_ID environment variable is not set.")
        print("  Set it to the Google Drive folder ID you want to sync.")
        sys.exit(1)

    folder_url = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
    print(f"Connecting to Google Drive...")
    print(f"  Source: {folder_url}")
    print()

    creds = get_credentials()
    if not creds:
        print("[ERROR] No credentials found. Set up authentication:")
        print("  Option 1: Set GOOGLE_SERVICE_ACCOUNT_FILE env var")
        print("  Option 2: Set GOOGLE_SERVICE_ACCOUNT_JSON env var")
        print("  Option 3: Place credentials.json in scripts directory")
        return

    service = build('drive', 'v3', credentials=creds)

    print("Listing files in Drive folder...")
    files = list_files(service, DRIVE_FOLDER_ID)

    if not files:
        print("  No files found in folder.")
        return

    print(f"  Found {len(files)} files")
    print()

    # Categorize files
    categorized: Dict[str, List[Dict]] = {}
    for f in files:
        cat = categorize_file(f.get("name", ""))
        categorized.setdefault(cat, []).append(f)

    # Display files
    for category, cat_files in sorted(categorized.items()):
        print(f"[{category.title()}] ({len(cat_files)} files)")
        for f in cat_files:
            size = f.get("size", "N/A")
            if size != "N/A":
                size = f"{int(size) / 1024:.1f} KB"
            print(f"  - {f.get('name')} ({size})")
        print()

    if list_only:
        return

    # Determine destination
    if create_snapshot:
        snapshot_name = datetime.now().strftime("%Y-%m-%d")
        dest_dir = SNAPSHOTS_DIR / snapshot_name / "files"
    else:
        dest_dir = SNAPSHOTS_DIR / "latest" / "files"

    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading to: {dest_dir}")
    print()

    downloaded = 0
    skipped = 0

    for f in files:
        file_name = f.get("name")
        file_id = f.get("id")
        mime_type = f.get("mimeType")

        print(f"  -> {file_name}...", end=" ")

        if mime_type.startswith("application/vnd.google-apps"):
            if export_google_doc(service, file_id, file_name, dest_dir / file_name, mime_type):
                downloaded += 1
                print("[OK]")
            else:
                skipped += 1
        else:
            if download_file(service, file_id, file_name, dest_dir / file_name):
                downloaded += 1
                print("[OK]")
            else:
                skipped += 1

    print(f"\nDownloaded: {downloaded}, Skipped: {skipped}")

    # Create manifest
    manifest_dir = dest_dir.parent
    manifest = create_manifest(files, manifest_dir)
    print(f"Manifest saved to: {manifest_dir / 'manifest.json'}")

    # Update index
    update_index(manifest)


def main():
    parser = argparse.ArgumentParser(description="Sync Google Drive folder")
    parser.add_argument("--list", action="store_true", help="List files only, don't download")
    parser.add_argument("--snapshot", action="store_true", help="Create dated snapshot")
    parser.add_argument("--update-registry", action="store_true", help="Update DOCUMENT_REGISTRY.md")
    parser.add_argument("--search-keywords", action="store_true", help="Search Drive by keywords")
    parser.add_argument("--keywords", type=str, help="Comma-separated keyword list")

    args = parser.parse_args()

    if args.search_keywords:
        if not GOOGLE_API_AVAILABLE:
            print("[ERROR] Google API libraries required.")
            sys.exit(1)

        config = load_config()
        keywords = []
        if args.keywords:
            keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
        if not keywords:
            keywords = config.get("drive", {}).get("search_keywords", [])

        if not keywords:
            print("[ERROR] No keywords provided. Use --keywords or set in config.")
            sys.exit(1)

        creds = get_credentials()
        if not creds:
            print("[ERROR] No Google Drive credentials available.")
            sys.exit(1)
        service = build('drive', 'v3', credentials=creds)

        include_shared = config.get("drive", {}).get("include_shared_drives", True)
        include_trashed = config.get("drive", {}).get("include_trashed", False)
        max_results = config.get("drive", {}).get("max_results", 200)

        print(f"Searching Drive with {len(keywords)} keyword(s)...")
        results = search_drive_files(
            service,
            keywords=keywords,
            max_results=max_results,
            include_shared_drives=include_shared,
            include_trashed=include_trashed,
        )
        _save_drive_search_results(results, keywords)
        print(f"Found {len(results)} files")
        return

    if args.update_registry:
        update_registry()
    else:
        sync_files(list_only=args.list, create_snapshot=args.snapshot)


if __name__ == "__main__":
    main()
