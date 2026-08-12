---
name: reminders
description: "Apple Reminders via rem CLI: add, list, search, update, complete, delete."
---

# Reminders

Use this for Apple Reminders tasks. Prefer `rem` over Things/AppleScript when
the user wants an AI-friendly personal todo backend on macOS.

## Tool

- CLI: `rem`
- Repo: `https://github.com/BRO3886/rem`
- Install:

```bash
GOBIN=/opt/homebrew/bin go install github.com/BRO3886/rem/cmd/rem@latest
```

`rem` uses EventKit for normal reads/writes. It may need Reminders permission for
the calling app in System Settings > Privacy & Security.

## Start

Check access:

```bash
rem lists -o json
rem today -o json
```

Use JSON for anything scripted or verified:

```bash
rem list --incomplete -o json
rem search "flight" -o json
rem show <id> -o json
```

## Add Tasks

Default: add directly, then verify by search/show.

```bash
rem add "Book LHR-SFO nonstop business flight" --due "tomorrow 9am" --priority high --notes "Nonstop only." -o json
rem search "LHR-SFO" -o json
```

Useful flags:

- `--list "Name"`: target list
- `--due "tomorrow 9am"`: due date/time; natural language is supported
- `--priority high|medium|low|none`
- `--notes "text"`
- `--url https://...`
- `--silent`: due date without notification
- `--remind-me 15m`: alarm before due time
- `--repeat daily|weekly|monthly|yearly`

## Update / Complete / Delete

Find the UUID first, then mutate by id or unique short id:

```bash
rem search "flight" -o json
rem update <id> --name "New title" --due "friday 2pm" --notes "..." -o json
rem complete <id> -o json
rem delete <id> --force
```

Always read back after writes; do not trust exit status alone.

## Lists

```bash
rem lists --count -o json
rem list-mgmt create "Travel"
rem list-mgmt rename "Old" "New"
rem list-mgmt delete "Name" --force
```

## Conventions

- Use executable task titles. Rewrite vague notes into the next concrete action.
- Preserve user wording when they clearly want verbatim capture.
- Split multiple unrelated actions into separate reminders.
- Use the default list unless the user names a list or the category is obvious.
- Do not add calendar events here; use calendar tooling instead.
- For current date math, run `date`; do not guess.

## Gotchas

- macOS only.
- First run may fail with `reminders access denied` until the calling app has
  Reminders permission.
- The default local list may be localized, e.g. `Erinnerungen`.
- `rem` search is plain query search, not shell regex.
- `--due` creates an alarm at the due time unless `--silent` is passed.
- Flagged reminders use private ReminderKit under the hood and may be more OS
  fragile than ordinary CRUD.
