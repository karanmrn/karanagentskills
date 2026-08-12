---
name: telecrawl
description: "Telegram archive: chats, messages, contacts, folders, search; import from Telegram Desktop/macOS."
---

# Telecrawl

Use this for Telegram history questions. Local archive first; the Telegram apps only for live/current state.

## Sources

- DB: `~/.telecrawl/telecrawl.db`
- Import source: Telegram Desktop `tdata` or native macOS Telegram Postbox (auto-detected)
- CLI: `telecrawl`
- Archive host: the populated archive currently lives on `clawmac` (~200 chats). Local DBs on other Macs may be empty — check `status` first and prefer SSH to the archive host over answering from an empty DB:

```bash
ssh -o RequestTTY=no -o RemoteCommand=none steipete@clawmac 'zsh -lc "telecrawl --json status"'
```

## Freshness

```bash
telecrawl --json status
```

Empty counts mean no import has run on this machine, not "no Telegram data".

## Queries

All read commands take `--json`.

```bash
telecrawl --json chats --limit 20
telecrawl --json chats --unread
telecrawl --json messages --chat <ID> --limit 50 --after 2026-01-01
telecrawl --json search "query" [--chat ID]
telecrawl --json contacts --limit 50
telecrawl --json folders
telecrawl --json topics --chat <ID>
```

## Import / Refresh

```bash
telecrawl doctor                 # verify a Telegram data source is readable
telecrawl import                 # merge-import from detected local Telegram app
telecrawl import --fetch-media   # also pull Telegram cloud media
```

Imports merge by default; `--restore` replaces the archive — treat as destructive and confirm first.

## Backup

Encrypted age shards to a git repo:

```bash
telecrawl backup status
telecrawl backup push
```
