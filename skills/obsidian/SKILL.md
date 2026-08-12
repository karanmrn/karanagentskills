---
name: obsidian
description: "Obsidian vault: search/read/write notes, backlinks, Bases, Canvas."
---

# Obsidian

Use this for local Obsidian vault work. An Obsidian vault is a normal folder of Markdown files plus `.obsidian/` config.

## Sources

- App config: `~/Library/Application Support/obsidian/obsidian.json`
- Default vault name: `obsidian`
- Usual local vault path: `~/obsidian`
- Official CLI: `obsidian`
- Vault commands resolve the vault from cwd; run them from `~/obsidian`.

## First Checks

```bash
command -v obsidian
obsidian version
obsidian vaults
cd ~/obsidian
obsidian commands filter=search:
```

Global commands like `version` and `vaults` work outside a vault. Vault-content
commands may print `Vault not found.` outside `~/obsidian`. Use `obsidian
commands`, not `obsidian help`, for CLI discovery.

If `obsidian` says CLI is disabled:

1. Prefer asking the user to enable Settings -> General -> Advanced -> Command line interface.
2. If you already confirmed the app config shape, `~/Library/Application Support/obsidian/obsidian.json` uses `"cli": true`.
3. Restart Obsidian after changing app-level CLI config.

## Read Workflow

Prefer official CLI for Obsidian-aware lookups:

```bash
cd ~/obsidian
obsidian search query="OpenClaw" format=json
obsidian search:context query="OpenClaw" limit=20 format=json
obsidian read path="Folder/Note.md"
obsidian file path="Folder/Note.md"
obsidian outline path="Folder/Note.md" format=json
obsidian backlinks path="Folder/Note.md" format=json
obsidian links path="Folder/Note.md"
obsidian properties path="Folder/Note.md" format=json
```

Use direct filesystem reads when you already know the path and need exact bytes:

```bash
sed -n '1,220p' "$HOME/obsidian/Folder/Note.md"
rg -n "term" "$HOME/obsidian"
```

Report which source you used when freshness or vault choice matters.

## Write Workflow

Choose the narrowest write path:

- New note: `obsidian create path="Folder/Note.md" content="..."`.
- Append/prepend daily notes: `obsidian daily:append content="..."`.
- Simple note edits: use `apply_patch` on the Markdown file.
- Rename/move notes: prefer `obsidian move path="Old.md" to="Folder/New.md"` so links can update.
- Opening UI after a write: add `open` only when useful or requested.

Common commands:

```bash
cd ~/obsidian
obsidian create path="Notes/New.md" content="# New\n\nBody"
obsidian append path="Notes/New.md" content="More text"
obsidian move path="Notes/New.md" to="Archive/New.md"
obsidian daily:path
obsidian daily:read
obsidian daily:append content="- Follow-up item"
```

For multi-line content, prefer editing the `.md` file with `apply_patch` once the path is known. Avoid fragile shell quoting for long prose.

## Bases, Canvas, Plugins

Use CLI discovery first:

```bash
cd ~/obsidian
obsidian bases
obsidian base:views path="Projects.base"
obsidian base:query path="Projects.base" view="Active" format=json
obsidian plugins format=json
obsidian plugins:enabled format=json
obsidian commands filter=workspace:
```

For `.canvas`, `.base`, and `.json` files, read/edit as structured data when possible. Keep formatting stable and validate JSON after edits.

## Safety

- Do not bulk rewrite the vault. Use targeted paths and review diffs.
- Do not edit `.obsidian/` unless the user asks or the task is explicitly settings/plugin work.
- Do not delete notes unless explicitly asked; prefer trash over permanent delete.
- Do not create hidden dot-folder notes through the Obsidian URI/CLI path.
- Preserve frontmatter and wikilinks unless the task is to refactor them.
- If multiple vaults exist, do not guess; use `obsidian vaults` and `obsidian.json`.
