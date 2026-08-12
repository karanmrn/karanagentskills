---
name: whatsapp
description: "WhatsApp router: history/search/read/send; wacrawl read, wacli live."
---

# WhatsApp

Use this as the first stop for WhatsApp work. Keep the source boundary sharp:

- `wacrawl`: primary WhatsApp Desktop archive. Read-only, best local history, no network, no sending.
- `wacli`: linked-device accounts. Use for alt accounts, live sync, auth, sending, chat/group mutation, and WhatsApp Web protocol questions.

If the user names `wacrawl` or `wacli` repo work specifically, read that tool's own skill too.

## Routing

- Primary WhatsApp reads/search/history: use `wacrawl`.
- Read/unread counts from WhatsApp Desktop: use `wacrawl`; it has chat-level unread counts, not per-message read state.
- Freshness-sensitive primary reads: check `wacrawl status`; run `wacrawl sync` when asked or when current data matters.
- Alt accounts such as `me`, `molty`, or named stores: use `wacli --account NAME`.
- Sending, reactions, presence, archive/pin/mute/mark-read, group/channel mutations: use `wacli` only after explicit user intent.
- Comparing coverage between sources: treat `wacrawl` as Desktop archive truth for primary history, and `wacli` as linked-device/live coverage with protocol limits.

## Safety

- Never send or mutate WhatsApp state unless explicitly requested.
- Prefer read-only `wacli` commands for inspection: pass `--read-only` or set `WACLI_READONLY=1`.
- Do not write into WhatsApp Desktop's app container.
- Do not edit `wacli` `session.db` directly.
- Keep named `wacli` accounts isolated; do not merge stores.
- Report source freshness, account name, and known gaps when answering from local stores.

## Common Commands

### Primary Archive

Freshness and status:

```bash
wacrawl status
wacrawl doctor
wacrawl sync
```

Unread triage:

```bash
wacrawl chats --limit 20
wacrawl unread --limit 20
wacrawl --json unread --limit 100
```

Search and slice messages:

```bash
wacrawl messages --after 2026-01-01 --limit 50
wacrawl messages --chat JID --asc --limit 100
wacrawl messages --has-media --limit 50
wacrawl --json search "query"
wacrawl search "query" --after 2026-01-01 --from-them
```

Archive media or backups, only when asked:

```bash
wacrawl import --copy-media
wacrawl backup status
wacrawl --sync never backup push
```

### Alt/Live Accounts

Account discovery and read-only inspection:

```bash
wacli accounts list --json
wacli --account me auth status --read-only --json
wacli --account me chats list --read-only --json
wacli --account me messages list --read-only --json --limit 50
wacli --account me messages search --read-only --json "query"
```

Background live sync, only when requested. Prefer `tmux` for follow-mode:

```bash
wacli --account me sync --follow --events
wacli --account me sync --once --events
```

Media, sending, and live mutations, only when explicitly requested:

```bash
wacli --account me media download --chat JID --id MESSAGE_ID
wacli --account me send text --to JID_OR_NAME --message "message"
wacli --account me send file --to JID_OR_NAME --file ./file.jpg --caption "caption"
wacli --account me send text --to JID --reply-to MESSAGE_ID --message "reply"
```

### Comparisons

When comparing `wacrawl` and `wacli`, compare both counts and overlap:

- message counts and date spans
- chat counts
- newest message timestamp
- overlap by `msg_id`
- overlap by `chat_jid + msg_id` when JIDs are normalized enough
- obvious gaps explained by linked-device history limits vs Desktop archive coverage

## Repo Pointers

- `~/Projects/wacrawl`: Desktop archive importer/search/backup.
- `~/Projects/wacli`: linked-device client/sync/send.
- Global skill copies: `~/Projects/agent-scripts/skills/wacrawl` and `~/Projects/agent-scripts/skills/wacli`.
