# Privacy Model

## Why This Matters

Your program repo contains information of varying sensitivity. Some of it is fine to share on GitHub. Some of it should never leave your machine. Getting this wrong isn't a minor mistake — it's a career-affecting one.

Palimpsest handles this with a two-tier structure. It's simple by design, because complicated privacy models get ignored.

## Two-Tier Structure

### Tier 1: Public (Committed to Git)

Files that are tracked in git and pushed to your remote repository. Visible to anyone with repo access.

What goes here:

- Program overview and methodology docs
- Sanitized status updates and dashboards
- Decision logs (the decisions, not the politics behind them)
- Process documentation and templates
- Architecture diagrams and technical docs
- Retrospective summaries

### Tier 2: Private (Gitignored)

Files that exist on your local machine only. The AI can read them (they're local files), but they never get committed or pushed.

What goes here:

- Raw meeting transcripts
- Slack digests with names and quotes
- Private notes ("Person X is underperforming," "Team Y is disengaged")
- Team structure details with personal information
- Salary, headcount, or budget data
- Vendor pricing and contract details
- Anything involving individual performance
- Draft communications before they're sent
- Credentials and API tokens

## .gitignore Patterns

Your `.gitignore` should include at minimum:

```gitignore
# Private context - NEVER commit
docs/context/transcripts/
docs/context/private-notes/
docs/context/slack-digests/
docs/context/team-structures/
docs/context/sensitive/

# Credentials
.env
*.json
!package.json
token.json
credentials.json

# Local AI state
.cursor/
.vscode/
*.db

# OS files
.DS_Store
Thumbs.db
```

When in doubt, add it to `.gitignore`. You can always remove a gitignore entry later. You can't un-push a file from git history (well, you can, but it's painful and doesn't guarantee it wasn't already cloned).

## How AI Reads vs. What AI Outputs

This is the critical distinction:

**The AI reads everything locally.** Both Tier 1 and Tier 2 files. When you ask "what did the team discuss about the API migration?" the AI reads your private meeting transcripts, your Slack digests, your private notes — the full picture.

**The AI outputs selectively.** When it generates a stakeholder update, it synthesizes from all sources but the output goes into a Tier 1 file. The output should contain insights derived from private context, not the private context itself.

Example:

- Private transcript says: "John mentioned he's worried about burnout on his team and might lose two engineers"
- AI-generated stakeholder update says: "Engineering capacity is a risk factor for Q2 delivery. Recommend contingency planning for potential team changes."

Same insight. No private details. The AI does this naturally if you instruct it to — but you should still review before publishing.

## External Publishing Rules

When content flows from your repo to external systems (Confluence, Slack, Google Docs):

| Rule | Rationale |
|------|-----------|
| Only Tier 1 content gets published automatically | Private content requires manual review |
| Scripts that publish externally require `ALLOW_GOOGLE_WRITE=1` or equivalent | Prevents accidental publishes |
| Published content gets a review step before going live | Human-in-the-loop for external visibility |
| Never reference repo file paths in external docs | External readers don't need to know about your repo structure |
| Sanitize names in public artifacts if context is sensitive | "A senior engineer" not "John in Platform Team" |

## Practical Rules

These are the rules I actually follow day-to-day:

1. **If it mentions a specific person by name in a negative or sensitive context** — gitignore it.
2. **If it contains raw quotes from private conversations** — gitignore it.
3. **If you would be uncomfortable with your skip-level seeing it** — gitignore it.
4. **If it contains any credential, token, or password** — gitignore it (and rotate it if you accidentally committed it).
5. **If in doubt** — gitignore it. Always err on the side of privacy.

## The Sanitized Mirror

For programs where you want to share the methodology or the structure publicly (like this repo), maintain a sanitized mirror:

- Copy the structure, not the content
- Replace specific program details with generic examples
- Remove all names, dates, and identifiable details
- Keep the templates and methodology docs intact

This gives you something you can show at conferences, in blog posts, or to other teams without exposing your actual program state.

## What About the AI Provider?

Depending on your AI editor and model:

- **Local models** (Ollama, etc.): Data never leaves your machine. Maximum privacy.
- **Cloud models with enterprise agreements** (Azure OpenAI, AWS Bedrock): Data handling governed by your company's contract. Usually acceptable for business data.
- **Consumer cloud models** (direct OpenAI, Anthropic APIs): Check the data retention and training policies. Most providers now offer opt-out of training, but verify.
- **AI editors**: Check whether the editor itself transmits your files to a cloud service beyond the model API call.

Your company's security team should be involved in this decision. Palimpsest as a methodology is provider-agnostic — you pick the privacy level that matches your requirements.

---

Previous: [Personal AI Assistant](09-personal-ai-assistant.md)
