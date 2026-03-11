# Setup Guide

## Prerequisites

Before you start, you need:

- **Git** installed and configured (you probably already have this)
- **An AI-capable editor** — Cursor, VS Code with Copilot, Claude Code, Windsurf, Kiro, Aider — pick one
- **Python 3.9+** (for automation scripts, optional but recommended)
- **A program to manage** (the methodology doesn't help if you have nothing to manage)

That's it. No Kubernetes cluster. No cloud infrastructure. No enterprise license.

## Quick Start (Recommended)

Clone the template and run the setup script:

```bash
git clone https://github.com/your-org/palimpsest.git my-program
cd my-program
chmod +x setup.sh
./setup.sh
```

The setup script will:

1. Create the directory structure
2. Generate template files with sensible defaults
3. Set up `.gitignore` for private files
4. Initialize the Memory Bank for agent continuity
5. Create a Python virtual environment (if Python is available)
6. Print next steps

After setup, open the repo in your AI editor and start talking to it.

## Manual Setup

If you prefer to understand every piece, here's what the setup script does:

### Directory Structure

```
my-program/
  CLAUDE.md              # Instructions for AI agents
  AGENTS.md              # Memory Bank protocol
  docs/
    PROGRAM_OVERVIEW.md   # High-level program state
    DASHBOARD.md          # Current metrics and status
    CONTEXT_INDEX.md      # Key people, channels, links
    GUIDELINES.md         # Team processes and norms
    context/
      daily-digests/      # Daily summaries
        latest.md
      meeting-notes/      # Structured meeting notes
      decisions/          # Decision log
      transcripts/        # Raw transcripts (private)
      private-notes/      # Your private notes (private)
    knowledge-base/
      scripts/            # Automation scripts
      snapshots/          # Point-in-time archives
  .cursor/
    memory/
      sessionLog.md       # Agent session history
      activeContext.md    # Current focus areas
      progress.md         # Recent milestones
  templates/              # Reusable document templates
```

### Create the Core Files

Start with these four. They're the minimum viable Palimpsest setup:

1. **PROGRAM_OVERVIEW.md** — What is this program? What are the workstreams? What's the timeline?
2. **DASHBOARD.md** — Current status of each workstream. Red/amber/green. Key metrics.
3. **CONTEXT_INDEX.md** — Who's who. What channel is for what. Where to find things.
4. **CLAUDE.md** — Instructions for your AI editor. What it should know. How it should behave.

Don't overthink these. Write them in plain markdown. You'll iterate.

## API Integrations

Integrations are optional but they're what turn Palimpsest from "organized notes" into "automated program management." Here's the priority order — set them up in this sequence.

### Priority 1: GitHub

Why first: your repo is already on GitHub (or GitLab). This is free.

What it gives you: version history, collaboration, CI/CD for automation, issue tracking if you want it.

No additional setup needed if you're already using git.

### Priority 2: Google Drive

Why second: most program artifacts live in Google Drive. Syncing them into your repo means the AI can read them.

What it gives you: automated sync of meeting notes, shared documents, and program artifacts into your repo as markdown.

Scopes needed:

```
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/calendar.readonly
https://www.googleapis.com/auth/documents.readonly
```

Setup:

1. Create a Google Cloud project (or use an existing one)
2. Enable Drive, Calendar, and Docs APIs
3. Create OAuth 2.0 credentials (Desktop application type)
4. Download the credentials JSON
5. Run the auth script: `./venv/bin/python scripts/google_auth.py`
6. Complete the OAuth flow in your browser

### Priority 3: Atlassian (Confluence + Jira)

Why third: if your org uses Confluence, you'll want to publish TO it. If they use Jira, you'll want to read FROM it.

What it gives you: bidirectional sync — read Jira ticket states into your repo, publish formatted updates to Confluence.

Setup:

1. Generate an Atlassian API token at https://id.atlassian.com/manage-profile/security/api-tokens
2. Note your Confluence space key and Jira project key

### Priority 4: Slack

Why fourth: Slack context is valuable but noisy. Selective sync is better than full sync.

What it gives you: ability to pull relevant Slack threads into your context, post summaries to channels.

Setup:

1. Create a Slack app in your workspace
2. Add required scopes: `channels:history`, `channels:read`, `chat:write`
3. Install to workspace and grab the bot token

### Priority 5: Glean (or equivalent enterprise search)

Why last: Glean is a nice-to-have for searching across tools you haven't integrated yet.

What it gives you: fallback search when something isn't in your repo yet.

Setup: typically requires IT to provision API access.

## Environment Variables

Create a `.env` file in your scripts directory (it's gitignored by default):

```bash
# Google
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json

# Atlassian
ATLASSIAN_URL=https://yourorg.atlassian.net
ATLASSIAN_EMAIL=your.email@company.com
ATLASSIAN_API_TOKEN=your-token-here
CONFLUENCE_SPACE_KEY=YOURSPACE
JIRA_PROJECT_KEY=YOURPROJECT

# Slack
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNELS=channel1,channel2

# Glean
GLEAN_API_TOKEN=your-token
GLEAN_INSTANCE=your-instance

# Safety
ALLOW_GOOGLE_WRITE=0
```

The `ALLOW_GOOGLE_WRITE=0` default is intentional. Scripts will read from Google but won't write to it unless you explicitly flip that flag. You don't want your automation accidentally modifying shared documents.

## MCP Configuration

If your AI editor supports MCP (Model Context Protocol) servers, you can connect external tools directly. Example configuration for Claude Code / Cursor:

```json
{
  "mcpServers": {
    "memory": {
      "command": "mcp-memory-service",
      "args": ["--db-path", "./memory.db"]
    },
    "confluence": {
      "command": "mcp-atlassian",
      "args": ["--confluence-url", "https://yourorg.atlassian.net"]
    },
    "slack": {
      "command": "mcp-slack",
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
      }
    }
  }
}
```

MCP servers let the AI interact with external tools directly — reading Confluence pages, posting to Slack, querying Jira — without you having to manually copy-paste content.

## Verification

After setup, verify everything works:

```bash
# Check repo structure
ls -la docs/

# Check Python environment (if using scripts)
./venv/bin/python --version

# Check API access (if configured)
./venv/bin/python scripts/preflight_check.py --service all

# Open in your AI editor and ask:
# "Read the PROGRAM_OVERVIEW.md and summarize the current state"
```

If the AI can read your files and give you a coherent summary, you're done. Everything else is iteration.

---

Previous: [The Solution](02-the-solution.md) | Next: [Use Cases](04-use-cases.md)
