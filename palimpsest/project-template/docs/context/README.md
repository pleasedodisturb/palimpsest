# Context Directory

Background information, transcripts, digests, and reference materials for the program.

---

## Structure

```
context/
  daily-digests/       # Daily summaries (public)
  meeting-notes/       # Meeting notes and action items (public)
  transcripts/         # Raw meeting transcripts (private, gitignored)
  private-notes/       # Personal notes and drafts (private, gitignored)
  slack-digests/       # Channel summaries (private, gitignored)
  team-structures/     # Org charts and team info (private, gitignored)
```

## Public vs Private

### Public (tracked in git)

- Daily digests and summaries
- Meeting notes (action items and decisions only)
- Reference documents and research

### Private (gitignored)

- Raw transcripts with names and internal discussion
- Slack channel exports
- Team structure and organizational details
- Personal working notes

## Privacy Rules

1. **Never commit private context to git** — the `.gitignore` handles this, but double-check
2. **Summarize, don't copy** — public notes should capture decisions and actions, not verbatim quotes
3. **No credentials or tokens** in any context file
4. **When in doubt, keep it private** — you can always promote something to public later
