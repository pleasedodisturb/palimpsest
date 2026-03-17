# FAQ

## "Isn't this just Notion with extra steps?"

No. Three fundamental differences:

1. **Git**: Your program state has real version control. Not "page history" — actual branching, diffing, blame, and log. You can answer "what changed this week?" with a git command, not by manually comparing page versions.

2. **AI-native**: Your entire repo is the context window. Notion AI sees one page at a time. Your AI editor sees everything — every meeting note, every decision, every status update — simultaneously.

3. **Portability**: It's markdown files. If you decide tomorrow that this whole approach is stupid, you still have a perfectly organized folder of documents. Try exporting a Notion workspace sometime. I'll wait.

## "Do I need to know how to code?"

No. You need to know:

- **Markdown** — headers, bullets, tables. You can learn this in 15 minutes.
- **Basic git** — clone, commit, push. Your AI editor handles most of this for you.
- **Talking to AI** — type what you want in plain English.

If you can write a Confluence page, you can do this. The "code" in "Program-as-Code" refers to the methodology (like Infrastructure-as-Code), not to writing actual code.

That said, if you DO know Python or shell scripting, you can automate a lot more. But it's not required.

## "My company uses Confluence. This won't work."

Great. Keep using Confluence. Palimpsest doesn't replace Confluence — it syncs TO it.

Your repo is where you work. Confluence is where you publish. Think of it like writing a blog post in your editor and then publishing it to WordPress. You don't write in WordPress.

The `push_confluence_weekly.py` script takes your markdown and publishes it as a formatted Confluence page. Stakeholders see a Confluence page they're used to. You never have to touch the Confluence editor.

## "How much does this cost?"

- **Git + GitHub**: Free (public repos) or whatever your org already pays
- **AI editor**: Cursor Pro is ~$20/month. VS Code + Copilot is ~$10/month. Claude Code varies by usage. Aider is free (bring your own API key)
- **API keys**: Most APIs have free tiers sufficient for a single program
- **Total**: $0-30/month, depending on your editor choice

Compare that to a Notion Team plan ($10/user/month for your whole team) or Confluence (bundled with Atlassian, but someone's paying).

## "Is this secure? My program has sensitive data."

See the full [Privacy Model](10-privacy-model.md), but the short version:

- Sensitive files go in gitignored directories. They exist on your machine, the AI reads them locally, but they never go to GitHub.
- You control what's committed and what isn't.
- If you're paranoid (and in some industries you should be), use local models only — your data never leaves your machine.
- The repo itself can be private on GitHub with access controls matching your org's policies.

## "Can non-TPMs use this?"

Absolutely. The methodology works for any role that manages complex, multi-stakeholder programs:

- **Engineering Managers** — tracking team initiatives, technical debt, hiring
- **Product Managers** — roadmap state, customer feedback synthesis, launch readiness
- **Chiefs of Staff** — executive initiatives, cross-org coordination
- **Consultants** — client engagement state, deliverable tracking
- **Researchers** — literature context, experiment tracking, collaboration state

The core principle is universal: if you drown in context across multiple tools, a structured repo + AI synthesis helps.

## "What if AI tools become unavailable?"

Then you have a really well-organized folder of markdown files. Which is still better than what most TPMs have.

The methodology degrades gracefully:

- **No AI**: You still have structured docs, git history, and scripts. You just do the synthesis manually.
- **No scripts**: You still have structured docs and git history. You just don't auto-sync.
- **No git**: You still have structured docs. You just lose versioning.

At every level of degradation, you're still better off than "40 docs across 5 tools with no organization."

## "How long until I see value?"

- **Day 1**: If you write PROGRAM_OVERVIEW.md and CONTEXT_INDEX.md, you can immediately ask your AI editor questions and get useful answers.
- **Week 1**: Once you've captured a few meeting notes and updated the dashboard, the AI starts giving you meaningfully better synthesis.
- **Month 1**: With a month of git history, you can do week-over-week diffs and trend analysis. This is where it gets powerful.

The investment is front-loaded. The first day takes the most effort. After that, maintaining the repo takes 10-15 minutes a day — less than the 90 minutes you were spending on manual context gathering.

---

Previous: [Why AI Despite Hallucinations](05-why-ai-despite-hallucinations.md) | Next: [Future Vision](07-future-vision.md)
