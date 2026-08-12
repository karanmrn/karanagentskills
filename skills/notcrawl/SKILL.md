---
name: notcrawl
description: "Notion archive: desktop/API sync, Markdown export, page search, read-only SQL."
---

# notcrawl

Use this for local Notion archive questions. Desktop reads local cache; API sync needs `NOTION_TOKEN` and page access.

## Sources

- DB: `~/.notcrawl/notcrawl.db`
- Pages: `~/.notcrawl/pages`
- CLI: `notcrawl`

## Refresh

```bash
notcrawl doctor
notcrawl status
notcrawl sync --source desktop
```

Use API only when needed and credentials/page access are available:

```bash
notcrawl sync --source api
```

## Query Workflow

1. Check freshness for recent/current Notion questions.
2. Search pages first; use read-only SQL for exact counts or schema-level analysis.
3. Use `export-md` when the user needs Markdown files refreshed.
4. Report date spans, page/database IDs, counts, and source limits.

Use root or subcommand help for syntax: `notcrawl --help`,
`notcrawl search --help`, `notcrawl sql --help`.

Common commands:

```bash
notcrawl search --limit 20 "query"
notcrawl databases
notcrawl sql "select count(*) from pages;"
notcrawl export-md
```
