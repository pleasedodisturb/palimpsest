# Formatting Standards

This document defines the markdown syntax, document structure, and writing style standards for all program artifacts. Every agent and every human contributor follows these rules.

These standards exist for a practical reason: documents flow between tools (git, Confluence, Google Docs, Slack, PDF export). Fancy formatting breaks in at least one of those destinations. Standard markdown works everywhere.

## Markdown Syntax Requirements

### The Rules

| Element | DO | DO NOT |
|---------|-----|--------|
| H1 | `# Title` | Emoji or symbol prefixes |
| H2 | `## Section` | `## [emoji] Section` |
| H3 | `### Subsection` | Decorative headers |
| Bullets | `- item` | `* item`, special characters, arrows |
| Nested bullets | `  - sub-item` (2 spaces) | Tabs, inconsistent nesting |
| Numbered lists | `1. item` | `a)`, `i.`, custom numbering |
| Tables | Pipe tables `\| A \| B \|` | Whitespace-aligned columns |
| Dividers | `---` | Unicode lines, box-drawing characters |
| Bold | `**text**` | `__text__` |
| Italic | `_text_` | `*text*` (ambiguous with bullets) |
| Code inline | `` `code` `` | Fancy quotes or backtick variants |
| Code blocks | Triple backticks with language | Indented code blocks |
| Links | `[text](url)` | Raw URLs in body text |
| Images | `![alt](path)` | HTML img tags |

### Common Violations and Fixes

| Violation | Fix |
|-----------|-----|
| `[emoji] Header Title` | `# Header Title` |
| `* bullet point` | `- bullet point` |
| `[arrow] sub-item` | `  - sub-item` |
| `[unicode line]` | `---` |
| ALL CAPS HEADER | `## Normal Case Header` |
| `Header:` (colon in header) | `## Header` (no colon) |

## Inverted Pyramid Structure

Every document longer than a paragraph should follow inverted pyramid structure:

### Level 1 — TL;DR (required)

The first paragraph answers: what is this, why does it matter, what should the reader do?

A reader who stops here should have the essential information.

### Level 2 — Key Details

The most important supporting information. Data, decisions, deadlines, dependencies.

### Level 3 — Supporting Context

Background, history, related work, methodology. Important for full understanding but not urgent.

### Level 4 — Appendix

Raw data, full lists, reference tables, archives. Only for readers who need the details.

## Document Template

```markdown
# Document Title

[One paragraph TL;DR: what this is, why it matters, what to do about it.]

## Key Points

- [Most important point]
- [Second most important point]
- [Third most important point]

## Details

[Expanded information organized by topic.]

### Subtopic A

[Details for subtopic A.]

### Subtopic B

[Details for subtopic B.]

## Context

[Background, history, related work.]

## Appendix

[Raw data, reference tables, archives.]
```

## Writing Style

### Human, Not Robot

Write like you are briefing a smart colleague, not generating corporate documentation.

| DO | DO NOT |
|-----|--------|
| "The migration is blocked by API rate limits" | "It has been determined that the migration process is experiencing impediments due to API rate limiting constraints" |
| "3 of 5 items are done" | "Significant progress has been made" |
| "We need a decision by Friday" | "It would be advisable to reach a consensus by the end of the business week" |
| "This broke because X" | "An unexpected issue was encountered" |

### Rules

- **Active voice.** "The team decided" not "It was decided by the team."
- **Short paragraphs.** 3-4 sentences maximum. Break up walls of text.
- **Concrete numbers.** "3 of 5 complete" not "most are done."
- **No hedge words.** Remove "basically", "essentially", "arguably", "it should be noted that."
- **No jargon without context.** If a term is domain-specific, explain it once.

## Visual Hierarchy

Use formatting to create scannable documents:

- **Headers** create the skeleton. A reader should understand the document from headers alone.
- **Bold** highlights key terms and decisions (use sparingly — if everything is bold, nothing is).
- **Tables** organize comparative or structured data. Do not use tables for single-column lists.
- **Code blocks** are for code, commands, and exact output. Do not use them for emphasis.
- **Horizontal rules** (`---`) separate major sections. Do not overuse.

## Publishing Checklist

Before sharing any document externally (Confluence, Google Docs, Slack):

1. [ ] No emoji in headers
2. [ ] No unicode bullets or special characters
3. [ ] No internal repo paths (use summaries, not file references)
4. [ ] No credentials, tokens, or sensitive data
5. [ ] TL;DR paragraph at the top
6. [ ] Headers form a readable outline on their own
7. [ ] Tables render correctly in the target format
8. [ ] Links are valid and accessible to the audience

## Anti-Patterns

Avoid these common documentation mistakes:

- **The wall of text.** No headers, no structure, no mercy. Break it up.
- **The emoji forest.** Every header has an emoji. Every bullet has a symbol. Strip them.
- **The hedge document.** Everything is "potentially", "arguably", "it might be." Be direct.
- **The changelog disguised as a document.** Lists every change but never explains what it means. Add context.
- **The orphan document.** Exists but is not linked from anywhere. Nobody will find it. Link it from the relevant index.
- **The stale document.** Was accurate six months ago. Update it or archive it.
- **The copy-paste artifact.** Contains formatting from the source (Slack, email, Confluence) that does not translate to markdown. Clean it up.
