---
name: things-todo
description: "Things 3 via things CLI: add, list, search, update, delete, verify."
---

# Things Todo

Use this for Things 3 tasks on Peter's Macs. Prefer `things` for Things-backed
todos; use `$reminders` only when the user asks for Apple Reminders.

## Tool

- CLI: `things`
- Repo: `https://github.com/ossianhempel/things3-cli`
- Install:

```bash
GOBIN=/opt/homebrew/bin go install github.com/ossianhempel/things3-cli/cmd/things@latest
```

Auth for update URL operations:

```bash
source ~/.profile >/dev/null 2>&1 || true
things auth
```

`THINGS_AUTH_TOKEN` should come from `~/.profile` or 1Password. Never print it.
`things update --dry-run` must redact it as `auth-token=***`.

## Start

Use JSON for scripted reads and verification:

```bash
things tasks --format json --limit 20
things today --format json
things search "query" --format json
```

Things DB reads may need Full Disk Access for the calling app. Writes should go
through Things URL Scheme or AppleScript via `things`; do not write the SQLite DB
directly.

## Add

Default: add, then search/read back.

```bash
things add "Book LHR-SFO nonstop business flight" --notes "Nonstop only." --when tomorrow --tags travel
things tasks --search "LHR-SFO" --format json
```

Useful flags:

- `--notes "text"`
- `--when today|tomorrow|evening|anytime|someday|YYYY-MM-DD`
- `--deadline YYYY-MM-DD`
- `--list "Project or Area"`
- `--tags tag1,tag2`
- `--checklist-item "text"` repeatable
- `--dry-run` to inspect the `things:///` URL without mutating.

## Update / Delete

Find the UUID first, then mutate by id:

```bash
things tasks --search "flight" --format json
things update --id <uuid> "New title" --notes "Updated notes"
things tasks --search "New title" --format json
things delete --id <uuid> --confirm <uuid>
things tasks --search "New title" --format json
things trash --search "New title" --format json
```

Always read back after writes. Delete moves items to Things Trash; verify normal
search is empty and trash search contains the item when cleanup matters.

## Conventions

- Turn vague asks into concrete next-action titles.
- Preserve wording when the user clearly wants capture, not rewriting.
- Split unrelated actions into separate to-dos.
- Use Today only when the user implies it; otherwise use Inbox/Anytime defaults.
- Prefer `--dry-run` before bulk updates/deletes.
- For current date math, run `date`; do not guess.

## Gotchas

- macOS only; remote hosts may show Things.app version as `UNKNOWN` if the app is
  absent or not visible there.
- `update` needs `THINGS_AUTH_TOKEN`; `add` does not.
- `--tags` is plural for add/update; `tasks --tag` is singular for filtering.
- `today` JSON may show `start: Anytime` plus a real `start_date`; use command
  membership/read-back, not one field alone, to verify Today placement.
