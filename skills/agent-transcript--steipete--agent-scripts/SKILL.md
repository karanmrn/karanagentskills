---
name: agent-transcript
description: "Requested GitHub PR/issue agent transcripts: redact, preview, and insert safely."
---

# Agent Transcript

Best-effort local-only provenance for OpenClaw PR/issue bodies. Use only when the user explicitly requests a transcript or preview.

## Contract

- Never use network. Session discovery reads local agent logs only.
- Never upload raw logs. Render sanitized Markdown first.
- Omit transcripts by default; do not offer or ask about them.
- If explicitly requested, offer a local HTML preview before insertion and wait for confirmation before adding the section.
- Fail closed on unresolved secrets, private keys, browser/session/cookie details, or auth URLs.
- Drop system/developer prompts, raw tool outputs, reasoning, env, cookies, tokens, and broad local paths.
- Keep user prompts, assistant visible decisions, terse tool summaries, and test/proof outcomes.
- Automatically trim the rendered transcript before showing it, previewing it, or inserting it into a public body. Never paste the raw full-session render into a PR/issue body just because `render` or `append-body` produced it.
- Remove session turns unrelated to the PR/issue work. Use the PR/issue title, branch name, changed files, and stated goal as scope; omit earlier/later unrelated tasks even when they are in the same session log.
- Best effort only: PR/issue creation must continue if no safe transcript is found.
- Add the `## Agent Transcript` section only when inserting a real transcript. Never add a placeholder transcript heading or text such as "A sanitized local transcript preview was generated but not included."
- Use a collapsed `<details>` section and update existing markers instead of duplicating sections.

## Helper

```bash
skills/agent-transcript/scripts/agent-transcript --help
```

Find a likely local session:

```bash
skills/agent-transcript/scripts/agent-transcript find \
  --query "$PR_TITLE $BRANCH_OR_PR_URL" \
  --cwd "$PWD" \
  --since-days 14
```

`find` scans the newest 400 matching local JSONL logs by default across Codex, Claude, Pi, and OpenClaw agent sessions. Use `--max-files N` for a wider local search.

In a downstream repo that syncs shared skills under `.agents/skills`, replace
`skills/agent-transcript` with `.agents/skills/agent-transcript`.

Render a PR/issue body section:

```bash
skills/agent-transcript/scripts/agent-transcript render \
  --session "$SESSION_JSONL" \
  --out /tmp/agent-transcript.md
```

Preview one candidate session locally:

```bash
skills/agent-transcript/scripts/agent-transcript preview \
  --session "$SESSION_JSONL" \
  --out /tmp/agent-transcript-preview.html
open /tmp/agent-transcript-preview.html
```

Append/update a body file before `gh pr create --body-file` or connector PR creation:

```bash
skills/agent-transcript/scripts/agent-transcript append-body \
  --body /tmp/pr-body.md \
  --session "$SESSION_JSONL" \
  --out /tmp/pr-body.with-transcript.md
```

## PR/Issue Workflow

Run this workflow only after the user explicitly requests a transcript or preview.

1. Draft the normal PR/issue body first.
2. Run `find` with title, branch, PR URL/number if known, and cwd.
3. If preview was requested, run `preview`, open the HTML, and wait for confirmation.
4. Render or append to a temp body, then automatically trim the `## Agent Transcript` section before showing it to the user or inserting it publicly. Keep only turns that explain this PR/issue's goal, implementation choices, files, tests, proof, blockers, and final outcome.
5. Inspect the trimmed transcript text. If it still includes unrelated earlier/later work, trim again before proceeding.
6. Use the enriched trimmed body file only after the user approves it.
7. If no safe session is found or the user declines, continue without a transcript or placeholder section.

## Review Artifacts

For manual audits across many PR/session candidates, create a local HTML preview from a local JSON file. This is for maintainers only and is not part of the PR/issue workflow:

```bash
skills/agent-transcript/scripts/agent-transcript html \
  --prs /tmp/recent-prs.json \
  --out /tmp/agent-transcript-preview.html
```
