---
name: openclaw-relay
description: "OpenClaw session relay: prompts/posts via local/remote acpx over SSH."
---

# OpenClaw Relay

Use this when the job is:

- "talk to Molty"
- "relay this into an OpenClaw channel session"
- "use acpx"
- "send this through the gateway via acp"
- "work through a remote OpenClaw bridge over SSH"

One skill. Two transports:

1. `local`
2. `ssh`

Default to `local` for direct telephone-game work from the current OpenClaw checkout. Use `ssh` when the target agent/session lives on another machine.

For Peter's setup, Molty normally lives on the Mac Studio gateway, reached as `steipete@steipete-macstudio.local`; avoid the `mac-studio` SSH alias for one-shot relay work because that alias auto-attaches tmux.

Script path: `scripts/openclaw_relay.py`

Target aliases file: `config/session_aliases.json`

## Mode Selection

Choose `local` when:

- the user explicitly says `acpx`
- the target session is on the current machine
- the goal is quick relay or private ask

Choose `ssh` when:

- the target agent/session lives on another host
- you want a persistent bridge session
- you need async queue/wait/show flows on a remote machine

## Defaults

The script avoids baked-in personal paths. Override with env or flags when needed.

- transport: `local`
- local repo cwd: current working directory
- local acpx repo: `<cwd>/extensions/acpx`
- ssh host: `steipete@steipete-macstudio.local`
- remote repo cwd: `<remote-home>/clawdbot`
- remote acpx repo: `<remote-home>/Projects/oss/acpx`
- gateway token file: `<home>/.openclaw/gateway.token`
- control session name: `codex-bridge`
- target aliases file: `config/session_aliases.json`

Useful env vars:

- `OPENCLAW_RELAY_TRANSPORT`
- `OPENCLAW_RELAY_HOST`
- `OPENCLAW_RELAY_CWD`
- `OPENCLAW_RELAY_ACPX_REPO`
- `OPENCLAW_RELAY_GATEWAY_URL`
- `OPENCLAW_RELAY_GATEWAY_TOKEN_FILE`
- `OPENCLAW_RELAY_SESSION`
- `OPENCLAW_RELAY_TARGETS_FILE`

## Quick Start

Health check:

```bash
python3 scripts/openclaw_relay.py doctor
```

List known target aliases:

```bash
python3 scripts/openclaw_relay.py targets
```

Resolve a target alias:

```bash
python3 scripts/openclaw_relay.py resolve --target maintainers
```

Ask a target session a question privately:

```bash
python3 scripts/openclaw_relay.py ask \
  --target maintainers \
  --message "Summarize the current vibe in this channel."
```

Force-send text to the resolved target:

```bash
python3 scripts/openclaw_relay.py force-send \
  --target maintainers \
  --text "Deploy is done."
```

For multiline posts, use `--text-file <path>` or `--text-file -` instead of
shell-quoting the message.

Force-send media when the user explicitly wants a channel post:

```bash
python3 scripts/openclaw_relay.py force-send \
  --transport ssh \
  --host steipete@steipete-macstudio.local \
  --target maintainers \
  --text "Demo video." \
  --media /tmp/demo.mp4
```

Use the persistent control session:

```bash
python3 scripts/openclaw_relay.py ensure
python3 scripts/openclaw_relay.py send --message "Reply with exactly OK."
python3 scripts/openclaw_relay.py show
```

Remote host example:

```bash
python3 scripts/openclaw_relay.py doctor --transport ssh --host steipete@steipete-macstudio.local
python3 scripts/openclaw_relay.py send \
  --transport ssh \
  --host steipete@steipete-macstudio.local \
  --message "Reply with exactly OK."
```

## Async Workflow

Queue work and poll the same control session:

```bash
python3 scripts/openclaw_relay.py start --message "Work on X and reply when done."
python3 scripts/openclaw_relay.py wait --after-seq <last-seq>
python3 scripts/openclaw_relay.py show
```

## Target Aliases

`config/session_aliases.json` ships with placeholders. Replace them with real values for your setup.

Example shape:

```json
{
  "main": "agent:<agentId>:main",
  "maintainers": "agent:<agentId>:discord:channel:<channelId>"
}
```

## Session Rules

Use these rules when choosing a command:

- Want a private reply from a specific session: `ask`
- Want the target session to decide whether to post: `publish`
- Want a guaranteed direct post: `force-send`
- Want blocking continuity with the control brain: `send`
- Want fire-and-forget async: `start`, then `wait` and `show`
- Want to stop queued work: `cancel`

## Failure Handling

If relay work fails:

1. Run `doctor`.
2. Run `status`.
3. Run `show`.
4. If the control session is wedged, run `cancel`, then `ensure`, then retry.

If route discovery is uncertain:

1. Resolve the target first.
2. Prefer alias or exact session key.
3. Use a tiny probe ask before sending the real payload.

## Output Relay

Return the actual assistant text or delivery result, not shell noise.

For relay tasks, report:

- transport used
- target session key
- whether the route probe/resolve succeeded
- final posted or returned result
