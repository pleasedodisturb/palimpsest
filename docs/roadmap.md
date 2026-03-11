# Roadmap

## Current Form Factor

Palimpsest is a **methodology + toolkit**. You clone the repo, run `setup.sh`, use the scripts. This is the right form factor for early adopters — TPMs comfortable with git and a terminal.

The repo IS the product.

## Near-Term: Proper CLI

Expand the `pac` entry point into a real CLI:

```bash
palimpsest init my-program          # what setup.sh does today
palimpsest sync                     # run all configured syncs
palimpsest status                   # program health summary
palimpsest publish confluence       # push updates to Confluence
palimpsest briefing                 # generate morning briefing
```

This is the natural next step. The scripts already do these things — they just need a unified interface.

**Trigger:** first real users asking "how do I run this more easily?"

## Near-Term: PyPI Publish

```bash
pip install palimpsest
```

Makes adoption frictionless. The package is already structured for it (`pyproject.toml`, entry points). Just needs a PyPI account and a publish workflow in CI.

**Trigger:** CLI is stable enough to version properly.

## Medium-Term: Plugin System for Data Sources

Right now, adding a new data source (e.g., Linear instead of Jira, Notion instead of Confluence) means writing a new script. A plugin architecture would let people contribute adapters:

```python
# palimpsest-linear/adapter.py
class LinearAdapter(DataSource):
    def fetch_tickets(self, project_key): ...
    def create_ticket(self, title, description): ...
```

**Trigger:** someone wants to use Palimpsest with a tool stack we don't support.

## What This Should NOT Become

### Web App / SaaS

Not yet, probably not ever in the traditional sense. The entire point of Palimpsest is that your program state lives in YOUR repo, not someone else's server. A web dashboard that reads from your repo could make sense eventually — but building infrastructure before proving the methodology is backwards.

If this becomes a SaaS, something went wrong with the original thesis.

### Desktop App (Electron/Tauri)

Solves no problem the CLI and editor don't already solve. The AI editor IS the UI. Adding another application just adds friction.

### Mobile App

Tempting for the "approve from your phone" workflow (AI proposes a Slack message, you approve with a tap). But this is a notification/approval problem, not an app problem. A Slack bot or Telegram bot handles this better than a custom app.

## The Real Question

The real product evolution question isn't "should this be an app?" — it's "should the agents run continuously?"

Right now: you trigger things manually or on cron. The future: agents watch for events (new Slack message, calendar change, Jira update) and respond in real-time.

That's the leap from toolkit to product. And it requires:

1. A lightweight daemon or hosted runner
2. Event-driven triggers (webhooks, file watchers)
3. An approval queue (AI proposes, human approves)
4. State management across agent runs

This is the architecture that would justify packaging as a proper application. But only after the methodology is validated by real users beyond the author.

Build the right thing, then build the thing right.

## Future: BMAD Integration

[BMAD](https://github.com/bmadcode/BMAD-METHOD) (Build Measure Analyze Decide) is a multi-agent development framework that could serve as the orchestration layer for productizing Palimpsest. Instead of hand-wiring agent triggers and approval flows, BMAD provides the scaffolding: agent roles, task decomposition, iterative delivery.

The idea: Palimpsest provides the TPM methodology and data layer. BMAD provides the agent orchestration and product development framework. Together, they could turn "a repo with scripts" into a proper product with structured agent workflows.

This is the "productivize" path — not by building a web app, but by formalizing the agent architecture so it's reproducible and extensible.

**Trigger:** methodology validated, CLI stable, ready to invest in agent orchestration seriously.

---

Previous: [Privacy Model](10-privacy-model.md)
