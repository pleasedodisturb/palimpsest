# Contributing

## The Honest Context

This project started as one TPM trying to survive a complex program. The methodology was built while using it — which means some parts are battle-tested and some parts are aspirational. The scripts were written to solve immediate needs, then generalized.

Most of the documentation was written with AI assistance and lightly curated by hand. If you find something that reads like a chatbot wrote it, you're probably right. PRs that make it sound more human are genuinely appreciated.

## What's Welcome

**Fixes**: If a script doesn't work, an API call is wrong, a scope is missing, or a config pattern doesn't match reality — fix it. These are the most valuable contributions.

**Clarifications**: If the setup guide skips a step, a template is missing a field, or a playbook doesn't make sense — clarify it. Open an issue if you're unsure, submit a PR if you know the fix.

**Your use cases**: Adapted Palimpsest for a different role? Used the Memory Bank with a different tool? Found a workflow that works better? Share it. This methodology benefits from diversity of experience.

**Questions via issues**: Good questions improve the docs. If you tried to follow the instructions and got stuck, that's a documentation bug.

## What's Less Welcome

- PRs that add complexity without clear benefit
- "Best practice" refactors that don't fix actual problems
- Adding dependencies for things that can be done with stdlib
- Making templates more generic to the point of being useless

## How to Contribute

1. Fork the repo
2. Create a branch: `git checkout -b fix/whatever-you-fixed`
3. Make your changes
4. Test what you can (scripts have a `--dry-run` mode for a reason)
5. Submit a PR with a clear description of what and why

## Code Style

- Python: readable over clever. Type hints where they help. Docstrings on public functions.
- Markdown: standard syntax only. No emoji in headers. See `agents/formatting-standards.md`.
- Commit messages: `type: description` format. Types: `docs`, `feat`, `fix`, `chore`, `script`.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

*Thanks for helping make this useful to more people.*
