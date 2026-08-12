---
name: review-improver
version: 1.0.0
description: Turn PUBMAXX captain feedback and merged-fix lessons into durable review checks.
---

# Review improvement loop

Use this outer loop after each captain bug report or merged fix that contains a
lesson. The canonical checklist is:

`~/.agents/skills/pubmax-code-review/SKILL.md`

## Update loop

1. Read the report, diff, tests, and final fix. State the failure in one line.
2. Decide whether the lesson is a missing review check, a stale check, or an
   implementation-only detail.
3. Patch the canonical `pubmax-code-review` skill with one focused check when
   the lesson can prevent recurrence.
4. Fold duplicates into the clearest existing check. Remove checks that no
   longer match the product or repository.
5. Keep the review skill under roughly 200 lines. Prefer a precise sentence
   over a new section. Bump its patch version for a check-only change.
6. Copy the updated skill directory to each non-symlink mirror:
   `~/.claude/skills/`, `~/.codex/skills/`, `~/.grok/skills/`, and
   `~/.config/opencode/skills/`.
7. Verify the canonical file and every mirror have identical content.

## What belongs in the checklist

Keep lessons that generalise across PRs: auth races, evidence gaps, silent
failures, reconnect recovery, mobile interaction, privacy, provenance, copy,
and build or test proof. Do not add a ticket-specific selector, one-off fixture,
or historical narrative.

## Closeout

Record the source issue or PR in the commit or review note, not in the checklist
unless it helps a future reviewer find the rule. Re-read the full checklist
after folding. The resulting check must be actionable, testable, and small.
