# CLAUDE.md - Instructions for Claude Code

This is the `palimpsest` repository — an open-source framework for AI-augmented Technical Program Management.

## Repo Structure

| Directory | Purpose |
|-----------|---------|
| `docs/` | Methodology guides (10 documents) |
| `case-study/` | Wolt CRM migration narrative |
| `templates/` | TPM document templates |
| `agents/` | AI agent configs (Cursor, Claude Code, Cline) + Memory Bank protocol |
| `scripts/` | Python automation toolkit (core, sync, content, automation, publishing) |
| `playbooks/` | TPM playbooks for common situations |
| `showcase/` | Demo prompts and quick wins |
| `project-template/` | What `setup.sh` generates |

## Key Conventions

- **Markdown**: Standard syntax only. No emoji in headers. See `agents/formatting-standards.md`.
- **Python scripts**: Config-driven (env vars), `--dry-run` where applicable, `pac` namespace for agent markers.
- **Git commits**: `type: description` format. Types: `docs`, `feat`, `fix`, `chore`, `script`.
- **No hardcoded values**: All credentials, domains, IDs from environment variables.

## Working on Scripts

```bash
pip install -e .
python scripts/core/preflight_check.py --service all
python -m pytest scripts/tests/
```

## Working on Docs

All docs use Vitalik's writing voice: direct, specific, evidence-based, self-aware humor, honest about failures, no corporate jargon. See the plan section "Writing Voice" for details.

## What NOT to Include

- Wolt-specific data (employee names, internal URLs, page IDs, credential paths)
- Hardcoded domains (use env vars)
- Real Slack channels, Jira project keys, or Confluence space keys in non-narrative files
- The `mxcrm` namespace (use `pac` everywhere)
