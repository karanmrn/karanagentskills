---
name: scan-new-specs
description: Scan warpdotdev/warp and warp-server for recently merged PRODUCT.md specs that don't yet have a corresponding docs PR in warpdotdev/docs. When a complete spec is found, auto-generates a full docs draft PR and tags the engineer. When a spec is too thin to draft from, pings the engineer directly. Designed to run as a scheduled Oz ambient agent (e.g., every 2-3 days). Use when setting up the automated docs trigger or running a manual docs coverage sweep.
---

# scan-new-specs

Scan `warpdotdev/warp` and `warp-server` for recently merged product or tech specs that lack a corresponding docs draft. For each gap:

- **If the spec is complete** — automatically run `write-feature-docs` in ambient mode to generate a full draft PR in `warpdotdev/docs`, then ping the engineer to review it
- **If the spec is thin** — ping the engineer directly to either flesh out the spec or kick off the docs workflow manually

In both cases, post a summary to `#growth-docs`.

## Configuration

Before running, confirm these values (or accept the defaults):

| Setting | Default | Description |
|---|---|---|
| `LOOKBACK_DAYS` | `3` | How many days back to scan for merged spec PRs |
| `SLACK_CHANNEL` | `#growth-docs` | Slack channel for engineer pings and summaries |
| `SLACK_BOT_TOKEN` | From `buzz` environment | Slack bot token for posting via API (already available in the `buzz` Oz environment) |

This skill uses the Slack API (`chat.postMessage`) rather than an incoming webhook, which enables real user pings. The `buzz` Oz environment already has the required `SLACK_BOT_TOKEN`. No new secrets setup is needed.

If `SLACK_BOT_TOKEN` is not set, print all messages to stdout instead.

## Step 1: Find recently merged specs

List merged PRs from both repos since the lookback date, then filter by changed files. Do not use `--search "in:files"` (GitHub does not support file-path filtering in PR search) and use a portable date command that works on both Linux and macOS:

```bash
# Portable date calculation (GNU/Linux and BSD/macOS compatible)
SINCE=$(date -d "-${LOOKBACK_DAYS} days" +%Y-%m-%d 2>/dev/null \
        || date -v-${LOOKBACK_DAYS}d +%Y-%m-%d)

# List all recently merged PRs (no file-path filter -- we check files next)
gh pr list \
  --repo warpdotdev/warp \
  --state merged \
  --search "merged:>${SINCE}" \
  --json number,title,author,mergedAt,url \
  --limit 100

# Repeat for warp-server
gh pr list \
  --repo warpdotdev/warp-server \
  --state merged \
  --search "merged:>${SINCE}" \
  --json number,title,author,mergedAt,url \
  --limit 100
```

For each PR returned, check whether it actually contains a new `specs/*/PRODUCT.md` by inspecting the changed files (this is the correct filter step):

```bash
gh pr view <number> --repo warpdotdev/<repo> --json files -q '.files[].path' \
  | grep -E '^specs/.+/PRODUCT\.md$'
```

Collect the list of: spec ID (the directory name under `specs/`), spec PR number and URL, PR author GitHub username, repo (`warp` or `warp-server`), and merge date.

For each PR author's GitHub username, resolve their Slack identity:

```bash
# Get the engineer's name and email from GitHub
ENG_NAME=$(gh api users/<github-username> -q '.name // .login')
ENG_EMAIL=$(gh api users/<github-username> -q '.email // empty')

# Look up their Slack user ID by email (real ping, not just a name mention)
if [ -n "$ENG_EMAIL" ]; then
  SLACK_USER_ID=$(curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
    "https://slack.com/api/users.lookupByEmail?email=${ENG_EMAIL}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['user']['id'] if d.get('ok') else '')")
fi

# Use <@USER_ID> for a real ping if lookup succeeded; fall back to @name if not
if [ -n "$SLACK_USER_ID" ]; then
  ENG_MENTION="<@${SLACK_USER_ID}>"
else
  ENG_MENTION="@${ENG_NAME} _(Slack ID not found — verify this is the right person)_"
fi
```

Store `ENG_MENTION`, `ENG_NAME`, and `ENG_GITHUB` for use in Slack messages.

## Step 2: Check for existing docs coverage

For each spec found, check `warpdotdev/docs` for an open/draft or merged PR that mentions the spec ID. Run two separate queries to avoid counting closed-unmerged PRs as coverage:

```bash
# Check for open or draft PRs
gh pr list \
  --repo warpdotdev/docs \
  --state open \
  --search "<spec-id>" \
  --json number,title,state,url \
  --limit 5

# Check for merged PRs
gh pr list \
  --repo warpdotdev/docs \
  --state merged \
  --search "<spec-id>" \
  --json number,title,state,url \
  --limit 5
```

A spec is considered **covered** if either query returns results (open, draft, or merged PR exists). Skip covered specs.

A spec is **uncovered** if neither query returns results. Closed-unmerged PRs do **not** count as coverage — a closed PR signals abandoned work that needs re-triggering.

## Step 3: Assess spec completeness

For each uncovered spec, read `specs/<id>/PRODUCT.md` and assess whether it has enough content to auto-draft from:

**Complete** (proceed to auto-draft) if ALL of the following are true:
- File is at least 40 lines long
- Contains a `## Behavior` section (or equivalent) with numbered invariants or user-facing steps
- Describes at least one concrete user action (not just a summary paragraph)

**Thin** (ping engineer instead) if the spec is a stub — only a Summary section, fewer than 40 lines, or no behavior detail.

## Step 4: Act based on spec completeness

### Path A: Complete spec → auto-draft

1. Run `write-feature-docs` in **ambient mode** (see `write-feature-docs` skill for details) — this skips the interactive outline confirmation and instead embeds the outline as a checklist in the PR description
2. The PR is opened in `warpdotdev/docs` with the draft and a checklist of items needing engineer verification
3. Request review from the engineer (`@<github-username>`) and from `@rachaelrenk` and `@hongyi-chen`
4. Post this Slack message to `SLACK_CHANNEL`:

```
📄 *Docs draft auto-generated*

Feature: *<spec-id>* (from `<repo>`)
Spec PR: <spec-pr-url>
<@USER_ID> (GitHub: <github-username>)

I’ve opened a draft docs PR for review: <docs-pr-url>
Please check the items marked *[UNVERIFIED]* and *[TODO]* in the PR — those are the only things that need your input.
```

### Path B: Thin spec → ping engineer

Post this Slack message to `SLACK_CHANNEL`:

```
📋 *New spec needs docs — not enough detail to auto-draft*

Feature: *<spec-id>* (from `<repo>`)
Spec PR: <spec-pr-url>
<@USER_ID> (GitHub: <github-username>)

The spec doesn’t have enough behavior detail for me to auto-generate docs yet. Please either:
• Add more detail to `specs/<spec-id>/PRODUCT.md` (a Behavior section with user-facing steps), OR
• Ping the docs team in this channel and we’ll draft it manually
```

If there are no uncovered specs, post:

```
✅ *Docs coverage scan complete* — all recently merged specs have docs coverage.
```

## Step 5: Post to Slack

Post each message using the Slack API. Build the JSON payload with `jq` to safely handle newlines, quotes, and backslashes in `$MESSAGE`:

```bash
jq -n \
  --arg channel "$SLACK_CHANNEL" \
  --arg text "$MESSAGE" \
  '{channel: $channel, text: $text}' \
| curl -s -X POST https://slack.com/api/chat.postMessage \
    -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
    -H 'Content-type: application/json' \
    -d @-
```

If `SLACK_BOT_TOKEN` is not set, print the message to stdout instead.

## Step 6: Print a summary

Always print a run summary to stdout:

```
scan-new-specs run summary
  Repos scanned:         warpdotdev/warp, warp-server
  Lookback window:       <N> days (since <date>)
  Specs found:           <N>
  Already covered:       <N>
  Auto-drafted:          <N>   (complete spec → draft PR opened)
  Pinged (thin spec):    <N>   (incomplete spec → engineer notified)
  Slack channel:         <channel>
```

## Scheduling

This skill is designed to run as a **scheduled Oz ambient agent** every 2–3 days. A suggested prompt for the Oz agent configuration:

> "Run scan-new-specs to check warpdotdev/warp and warp-server for newly merged PRODUCT.md specs that don't have a corresponding docs PR in warpdotdev/docs. For complete specs, auto-generate a draft docs PR and tag the engineer. For thin specs, ping the engineer in Slack. Post a summary to #growth-docs. Use the last 3 days as the lookback window."

Suggested schedule: every Monday, Wednesday, and Friday at 9am PT — frequent enough to catch specs quickly, but not noisy.

## Deduplication note

This skill does not maintain persistent state between runs. Deduplication relies entirely on whether a docs PR exists in `warpdotdev/docs` — if a PR is open or merged for a spec, it won't be flagged again. This means a spec will continue to generate nudges until someone opens a docs PR for it (even a draft).

**Edge case:** if a docs draft PR was opened and then *closed* (not merged), the spec will be re-flagged on the next run since closed PRs are not counted as coverage. This is intentional — a closed PR means docs work was abandoned and needs re-triggering.

## Slack mention note

This skill uses the Slack API (`chat.postMessage`) with the `SLACK_BOT_TOKEN` from the `buzz` Oz environment. This supports real `<@USER_ID>` mentions — engineers will receive a direct notification when their spec is detected.

The user ID is resolved by looking up the engineer's GitHub email against the Slack `users.lookupByEmail` API. If the engineer has a private GitHub email, the lookup will fail and the message will fall back to a plain-text name with a note to verify manually.

## Related skills

- `write-feature-docs` — the skill engineers run to generate the docs draft after being nudged
