---
name: codexbar
description: "AI service usage/quota via CodexBar CLI: Codex/OpenAI, Claude, Kimi and other provider limits, credits, reset times."
---

# CodexBar

Use this when asked about AI subscription usage, rate limits, remaining credits, or "how much Codex/Claude/Kimi do I have left".

## CLI

- Binary: `codexbar` (Homebrew)
- Default invocation honors the in-app provider toggles:

```bash
codexbar usage
codexbar usage --format json
```

- Specific provider (`--provider` accepts codex, claude, kimi, gemini, copilot, cursor, openrouter, and many more — see `codexbar --help`):

```bash
codexbar usage --provider codex --json
codexbar usage --provider claude --json
```

- Multiple accounts: `--account <label>`, `--account-index <n>`, or `--all-accounts` (single provider only).

## Auth model

Provider fetches ride existing sessions — OAuth caches, CLI credentials, or browser cookies. No secrets are passed on the command line.

- Codex: OpenAI web dashboard via oauth; falls back to Codex CLI.
- Claude: claude.ai API via browser session cookie; falls back to Claude CLI. "No Claude session key found in browser cookies" means log in to claude.ai in a supported browser (or rely on the CLI fallback).
- Token-based providers read the CodexBar config file.

## Dashboard endpoints

The menu bar app serves its dashboard on loopback. The page pulls
`/dashboard/v1/snapshot` and `/cost`; there is no `/api/*` namespace, so those
paths 404 rather than telling you that you guessed. The snapshot endpoint
requires auth, so when the CLI is unavailable the quickest honest check is to
open the dashboard in a browser.

`usage --all-accounts` polls every account serially and takes well over ninety
seconds. If it produces *zero* bytes on both stdout and stderr, it is not slow,
it is blocked: the CLI is a helper inside `CodexBar.app`, and a pending macOS
Gatekeeper prompt stops it dead with no output. Screenshot the screen before
debugging the command.

## Interpreting output

- Errors for providers that were never configured are noise, not failures — only report providers the user actually uses.
- Report percentage left, pace vs. expected, and reset time; the pace line ("in deficit"/"in reserve") is the actionable bit.
- Claude rows read `claude-swap` **stored backups**, which produces two
  confusing readings. The currently active slot shows as having no stored
  credentials, because the live login is an `active profile` and its backup only
  materialises when you switch away. And `claude-swap` keeps a `last seen`
  percentage that keeps rendering for accounts whose credentials are gone, so a
  dead account can read as healthy for days. A plausible percentage is not proof
  of a working credential; only `refresh token yes` in
  `claude-swap list --token-status` is.
