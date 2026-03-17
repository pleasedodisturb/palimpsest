#!/bin/bash
#
# Palimpsest Setup Script
# Creates a new project structure for AI-augmented program management
#
# Usage:
#   ./setup.sh my-program-name
#   ./setup.sh my-program-name --with-glean
#   ./setup.sh my-program-name --with-github
#   ./setup.sh my-program-name --minimal
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'
SEPARATOR='-------------------------------------------'

info() { local msg="$1"; echo -e "${BLUE}>${NC} ${msg}"; return 0; }
success() { local msg="$1"; echo -e "${GREEN}+${NC} ${msg}"; return 0; }
warn() { local msg="$1"; echo -e "${YELLOW}!${NC} ${msg}"; return 0; }
# shellcheck disable=SC2317 -- exit 1 terminates; return is unreachable but satisfies linters
error() { local msg="$1"; echo -e "${RED}x${NC} ${msg}"; exit 1; return 1; }

# Defaults
WITH_GLEAN=false
WITH_GITHUB=false
MINIMAL=false
PROJECT_NAME=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --with-glean)  WITH_GLEAN=true ;;
        --with-github) WITH_GITHUB=true ;;
        --minimal)     MINIMAL=true ;;
        --help|-h)
            echo "Palimpsest Setup - Create a new program-as-code project"
            echo ""
            echo "Usage: ./setup.sh <project-name> [options]"
            echo ""
            echo "Options:"
            echo "  --with-glean    Include Glean MCP configuration"
            echo "  --with-github   Include GitHub MCP configuration"
            echo "  --minimal       Create minimal structure only"
            echo "  --help, -h      Show this help"
            echo ""
            echo "Example:"
            echo "  ./setup.sh my-crm-program --with-glean --with-github"
            exit 0
            ;;
        -*)  error "Unknown option: $arg" ;;
        *)   [[ -z "$PROJECT_NAME" ]] && PROJECT_NAME="$arg" ;;
    esac
done

[[ -z "$PROJECT_NAME" ]] && error "Please provide a project name: ./setup.sh my-program-name"
[[ -d "$PROJECT_NAME" ]] && error "Directory '$PROJECT_NAME' already exists"

echo ""
echo "$SEPARATOR"
echo "  Palimpsest Setup"
echo "$SEPARATOR"
echo ""
info "Creating project: $PROJECT_NAME"
echo ""

# Create directory structure
info "Creating directory structure..."
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

mkdir -p docs/context/transcripts
mkdir -p docs/context/private-notes
mkdir -p docs/context/daily-digests
mkdir -p docs/templates
mkdir -p .cursor/memory
mkdir -p logs

success "Directory structure created"

# Create README
info "Creating README.md..."
cat > README.md << READMEEOF
# $PROJECT_NAME

A Palimpsest repository for managing your program with AI assistance.

## Quick Start

1. Open this folder in your AI-powered editor (Cursor, VS Code, etc.)
2. Start a conversation: "Tell me about this project structure"
3. Edit \`docs/PROGRAM_OVERVIEW.md\` with your program details

## Structure

\`\`\`
docs/
  PROGRAM_OVERVIEW.md      # Program state (keep current)
  DASHBOARD.md             # Quick status view
  BACKLOG.md               # Your task list
  context/
    transcripts/           # Meeting transcripts (private)
    private-notes/         # Sensitive notes (private)
    daily-digests/         # AI summaries (public)
  templates/               # Reusable templates
.cursor/
  mcp.json                 # MCP integrations
  memory/                  # AI memory bank
\`\`\`

## Key Documents

| Document | Purpose |
|----------|---------|
| [PROGRAM_OVERVIEW.md](./docs/PROGRAM_OVERVIEW.md) | Full program state |
| [DASHBOARD.md](./docs/DASHBOARD.md) | Quick status for stakeholders |
| [BACKLOG.md](./docs/BACKLOG.md) | Personal task list |

---

*Powered by [Palimpsest](https://github.com/pleasedodisturb/palimpsest)*
READMEEOF
success "README.md created"

# Create PROGRAM_OVERVIEW
info "Creating docs/PROGRAM_OVERVIEW.md..."
cat > docs/PROGRAM_OVERVIEW.md << 'EOF'
# Program Overview

**Last Updated:** [DATE]
**Status:** [GREEN/YELLOW/RED]

---

## Program Summary

[1-2 sentence description of what this program is about]

## Current Status

### Key Metrics

| Metric | Value | Trend |
|--------|-------|-------|
| Days to Launch | [X] | - |
| Open Blockers | [X] | - |
| Completed Milestones | [X/Y] | - |

### Component Status

| Component | Status | Notes |
|-----------|--------|-------|
| [Component 1] | Ready/At Risk/Blocked | - |
| [Component 2] | Ready/At Risk/Blocked | - |

## Active Blockers

### 1. [Blocker Name]
- **Impact:** [What can't happen until resolved]
- **Owner:** [Who is responsible]
- **ETA:** [Expected resolution]

## Key Decisions

| Date | Decision | Rationale | Decided By |
|------|----------|-----------|------------|
| [DATE] | [What] | [Why] | [Who] |

## Timeline

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| [Milestone 1] | [DATE] | On Track/At Risk/Blocked |

## Team

| Role | Person | Contact |
|------|--------|---------|
| TPM | [Name] | [channel] |
| PM | [Name] | [channel] |
| Eng Lead | [Name] | [channel] |

## Links

| Resource | Link |
|----------|------|
| Slack Channel | [#your-channel] |
| Jira Board | [link] |
| Confluence | [link] |

---

*Update this document whenever program state changes*
EOF
success "docs/PROGRAM_OVERVIEW.md created"

# Create DASHBOARD
info "Creating docs/DASHBOARD.md..."
cat > docs/DASHBOARD.md << 'EOF'
# Program Dashboard

**Updated:** [DATE] | **Status:** On Track / At Risk / Blocked

## At a Glance

| Metric | Value |
|--------|-------|
| **Launch Date** | [DATE] |
| **Days Remaining** | [X] |
| **Open Blockers** | [X] |

## Blockers

| # | Issue | Owner | ETA |
|---|-------|-------|-----|
| 1 | [Blocker] | [Name] | [Date] |

## This Week

### Completed
- [x] [Task 1]

### In Progress
- [ ] [Task 2]

### Blocked
- [ ] [Task 3] - *blocked by [reason]*

## Quick Links

| Resource | Link |
|----------|------|
| Full Overview | [PROGRAM_OVERVIEW.md](./PROGRAM_OVERVIEW.md) |
| Slack | [#your-channel] |
EOF
success "docs/DASHBOARD.md created"

# Create BACKLOG
info "Creating docs/BACKLOG.md..."
cat > docs/BACKLOG.md << 'EOF'
# TPM Backlog

## This Week

- [ ] **[High Priority Task]**
  - Details here

## Next Week

- [ ] [Future task]

## Parked

- [ ] [Nice to have]

## Done (Recent)

- [x] [Completed task] - [DATE]
EOF
success "docs/BACKLOG.md created"

# Create context README
info "Creating docs/context/README.md..."
cat > docs/context/README.md << 'EOF'
# Context Files

This folder contains context that helps the AI understand your program.

## Privacy Rules

### Private (gitignored)
- `transcripts/` - Meeting recordings and transcripts
- `private-notes/` - 1:1 notes, sensitive observations

### Public (committed)
- `daily-digests/` - Sanitized summaries safe to share
EOF
success "docs/context/README.md created"

# Create .gitignore
info "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Credentials
.env
.env.*
!.env.example
credentials.json
token*.json
*.pem
*.key
*-service-account.json

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp
*~

# OS
.DS_Store
Thumbs.db

# Private context
docs/context/transcripts/
docs/context/private-notes/
docs/context/slack-digests/
docs/context/team-structures/
**/*Transcript*

# Logs
logs/*.log

# Keep these
!docs/context/README.md
!docs/context/daily-digests/
EOF
success ".gitignore created"

# Create templates
if [[ "$MINIMAL" = false ]]; then
    info "Creating templates..."
    cat > docs/templates/STAKEHOLDER_UPDATE.md << 'EOF'
# Weekly Status Update - [DATE]

**Program:** [Program Name]
**Status:** On Track / At Risk / Blocked

## Summary

[1-2 sentence summary]

## Completed This Week

- [Achievement 1]
- [Achievement 2]

## In Progress

- [Work item] - [Status/ETA]

## Blocked

| Issue | Impact | Action Needed | Owner |
|-------|--------|---------------|-------|
| [Blocker] | [Impact] | [What we need] | [Who] |

## Next Week Focus

1. [Priority 1]
2. [Priority 2]
EOF
    success "Templates created"
fi

# Create MCP config
info "Creating MCP configuration..."

MCP_SERVERS=""
if [[ "$WITH_GLEAN" = true ]]; then
    MCP_SERVERS="${MCP_SERVERS}
    \"glean\": {
      \"command\": \"npx\",
      \"args\": [\"-y\", \"@anthropic/mcp-glean\"],
      \"env\": {
        \"GLEAN_API_TOKEN\": \"\${GLEAN_API_TOKEN}\",
        \"GLEAN_INSTANCE\": \"\${GLEAN_INSTANCE}\"
      }
    }"
fi

if [[ "$WITH_GITHUB" = true ]]; then
    [[ -n "$MCP_SERVERS" ]] && MCP_SERVERS="${MCP_SERVERS},"
    MCP_SERVERS="${MCP_SERVERS}
    \"github\": {
      \"command\": \"npx\",
      \"args\": [\"-y\", \"@anthropic/mcp-github\"],
      \"env\": {
        \"GITHUB_TOKEN\": \"\${GITHUB_TOKEN}\"
      }
    }"
fi

if [[ -n "$MCP_SERVERS" ]]; then
    cat > .cursor/mcp.json << MCPEOF
{
  "mcpServers": {${MCP_SERVERS}
  }
}
MCPEOF
else
    echo '{"mcpServers": {}}' > .cursor/mcp.json
fi

success "MCP configuration created"

# Create memory bank files
info "Creating Memory Bank..."
cat > .cursor/memory/sessionLog.md << 'EOF'
# Session Log

## Active Sessions

_No active sessions_

## Session History

_No sessions yet. Start one by opening this project in your AI editor._
EOF

cat > .cursor/memory/activeContext.md << 'EOF'
# Active Context

## Current Focus

_Not yet initialized. Add your current focus here._

## Recent Events

_No events recorded yet._
EOF

cat > .cursor/memory/progress.md << 'EOF'
# Progress

## Milestones

_No milestones recorded yet._

## Recent Completions

_Nothing completed yet._

## Next Steps

- [ ] Initialize program overview
- [ ] Add first context documents
- [ ] Configure MCP integrations
EOF

success "Memory Bank initialized"

# Initialize git
info "Initializing git repository..."
git init -q
git add .
git commit -q -m "Initial Palimpsest setup"
success "Git repository initialized"

# Output
echo ""
echo "$SEPARATOR"
echo -e "  ${GREEN}Setup complete!${NC}"
echo "$SEPARATOR"
echo ""
echo "Next steps:"
echo ""
echo "  1. cd $PROJECT_NAME"
echo ""
echo "  2. Open in your editor:"
echo "     cursor .    # or: code ."
echo ""
echo "  3. Start a conversation:"
echo "     \"Tell me about this project structure\""
echo ""
echo "  4. Edit docs/PROGRAM_OVERVIEW.md with your program details"
echo ""

if [[ "$WITH_GLEAN" = true ]]; then
    warn "Set GLEAN_API_TOKEN and GLEAN_INSTANCE in your environment"
fi
if [[ "$WITH_GITHUB" = true ]]; then
    warn "Set GITHUB_TOKEN in your environment"
fi

echo "$SEPARATOR"
echo ""
