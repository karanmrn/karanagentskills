---
name: "github-project-triage"
description: "GitHub issue/PR triage: queues, CI, blockers, risk, proof, next actions."
---

# GitHub Project Triage

Always use this skill when the user types `triage`, unless the request explicitly targets a non-GitHub domain. From inside a repo, use the current GitHub project by default. Triage means maintainer-facing item cards: URL, what each issue/PR is about, why it matters, author trust, fit, risk, proof/test state, blockers, and next action. Never return only queue numbers or opaque refs.

Output is URL-first: every surfaced issue/PR/repo item must include its GitHub URL in the first line or first sentence for that item. If giving a shortlist, print one URL per item.

Use RepoBar as the first pass only for broad queue discovery across relevant owners/orgs. RepoBar is faster and more profile-aware than hand-rolling `gh repo list` loops, and it already understands repo activity, issue counts, PR counts, local projects, auth, cache, and filters.

## Setup

Prefer a real `repobar` binary when installed. In this workspace it may only exist as a SwiftPM product in `~/Projects/RepoBar`.

```bash
repobar_cmd() {
  if command -v repobar >/dev/null 2>&1; then
    repobar "$@"
  elif [ -x "$HOME/Projects/RepoBar/.build/debug/repobarcli" ]; then
    "$HOME/Projects/RepoBar/.build/debug/repobarcli" "$@"
  else
    swift run --package-path "$HOME/Projects/RepoBar" repobarcli "$@"
  fi
}

repobar_cmd status --json
```

Default owners for broad triage: `steipete`, `openclaw`. For broad/default queue triage, include a detail pass for `openclaw/openclaw` even if it is not the first repo by count, because it is the main ClawdBot/OpenClaw queue. Do not include `amantus-ai` or other owners unless the user names them, the current repo is already under that owner, or the task explicitly asks for all/everything. For an exact owner-specific task, do not broaden beyond the named owner.

## Local Repo Gate

Before starting work inside any local project, verify the checkout is ready:

```bash
git status --short --branch
git branch --show-current
git pull --ff-only
git status --short --branch
```

Proceed only when the branch is `main`, the pull succeeds, and the worktree is clean. If the branch is not `main`, the pull fails, or `git status --short` shows changes, stop and ask Peter what to do. Do not switch branches, stash, commit, reset, restore, or clean without explicit direction.

## Scope Rule

If the user says `triage` and the current working directory is a Git repo with a GitHub remote, triage only that project. Do not broaden to all Peter/org queues unless the user says `broad`, `all`, `everything`, names multiple owners/orgs, or asks for cross-repo triage.

If the repo has `VISION.md`, read it before judging what can be handled autonomously. Use it as the product-fit source of truth, then apply this skill's risk/testability rules. If no `VISION.md` exists, use the autonomous-fit rules below.

Find the current project:

```bash
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || true)
if [ -z "$repo" ]; then
  url=$(git remote get-url origin 2>/dev/null || true)
  repo=$(printf '%s\n' "$url" |
    sed -E 's#^git@github.com:##; s#^https://github.com/##; s#\\.git$##')
fi
printf '%s\n' "$repo"
```

Current-project triage starts with:

```bash
gh issue list --repo "$repo" --state open --limit 50 \
  --json number,title,author,labels,createdAt,updatedAt,url
gh pr list --repo "$repo" --state open --limit 50 \
  --json number,title,author,isDraft,reviewDecision,mergeStateStatus,createdAt,updatedAt,url
```

Before acting on any issue or PR, read all comments and treat Peter/owner comments as authoritative routing instructions. If Peter says it looks good, needs changes, is superseded, is product-approved, or is not wanted, that overrides bot labels and ordinary triage judgment. If there is no Peter/owner comment, use maintainer judgment and say that the call is yours.

Then inspect enough detail to explain every surfaced item. For small queues (about 10 open items or fewer), inspect all items. For larger queues, inspect the top priority slice and say what was not expanded.

```bash
gh issue view <n> --repo "$repo" \
  --json number,title,author,body,comments,labels,createdAt,updatedAt,url
gh pr view <n> --repo "$repo" \
  --json number,title,author,body,comments,files,commits,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup,createdAt,updatedAt,url
gh pr diff <n> --repo "$repo" --patch
```

Only comment, close, merge, rerun, or patch with strong evidence.

## Triage Output

When the user says `triage`, always scan open issues and open PRs for the current repo. Return:

- `Autonomous candidates`: items that appear fixable/landable without more product input, with URL, why it qualifies, required verification, and confidence. This is a selection for review, not permission to start work unless the user also asks for autonomous execution.
- `Needs Peter`: items blocked on Peter/owner decision, product direction, missing credentials/access, live-provider proof that cannot be obtained, security/privacy judgment, or an authoritative Peter comment requesting changes.
- `Defer/close/supersede`: stale, duplicate, lower-quality, or overlapping items where the likely action is not new code.

For every plausible autonomous candidate, use available high-reasoning subagents, oracle, or independent agent review to check feasibility before presenting it when tool support exists. Give the subagent only task-local evidence and ask whether the item can be completed autonomously, what verification is required, and what could make it unsafe. If subagents are unavailable, do the same depth yourself and say so.

## Autonomous Work Mode

When the user says `do work autonomously`, `work you can do autonomously`, `keep going`, or similar, do not stop after a queue summary or one local patch. Treat it as permission to process the eligible issue/PR queue sequentially until no safe autonomous item remains, each item is landed/closed/deferred with proof, or a blocker requires Peter.

Never work multiple tickets at once. For each item:

1. Read the issue/PR, related code, docs, CI, and `VISION.md` if present; Google/use official docs when facts may be stale or unclear.
2. Decide if it is autonomous:
   - Go: performance improvements unless complexity rises too much; bugfixes with repro/root cause and verification path; small UI/UX tweaks; docs fixes; narrow test/internal fixes; low-risk dependency/CI cleanup with green proof.
   - Ask first: new features, product/vision choices, broad behavior changes, risky dependencies, security-sensitive changes without strong proof, live-provider work without usable credentials, anything that cannot be end-to-end tested.
   - Refactor preference: choose a clean bounded refactor when it is the better fix for an autonomous item; do not use "small patch" as the default if it leaves worse design.
3. Implement or fix the PR in the best maintainable way. Prefer updating the contributor PR when writable; otherwise recreate locally with credit.
4. Verify locally and live end-to-end when possible. For UI behavior, use the repo's expected live UI proof path, such as Peekaboo, browser-use, screenshots, or VM proof. For API/provider behavior, use a real usable key/account through the expected secret workflow when available. If access is missing, stop before pretending the item is done and ask Peter for help.
5. Run Codex Auto Review before commit/land unless trivial/docs-only or explicitly skipped; address accepted/actionable findings.
6. Ensure CI is green, PR description/changelog are good, land/close/comment with evidence, then return to `main`, pull `--ff-only`, and verify a clean worktree before selecting the next autonomous item.
7. After every landed PR, post a PR comment with exactly how it was tested: local commands, live/UI/API proof, CI run/check state, landed commit, and any caveats. If verification images apply, upload/post them with `gh image` when available; if the uploader is unavailable, say so and include the screenshot path or alternate GitHub attachment proof instead of silently omitting images.

Do not end autonomous mode with dirty files or an unpushed local fix unless blocked. If blocked, state the exact blocker, current branch/status, proof already gathered, and the next decision needed.

Autonomous work is still bounded by scope: current repo by default; broad/all queues only when the user asked for broad/all/everything or named owners/orgs.

## Trust Signals

Include author/opener trust for every non-maintainer item you recommend acting on. For low-risk Dependabot/internal items, a terse bot/internal trust line is enough.

Prefer the bundled helper:

```bash
skills/github-project-triage/scripts/github-activity.sh --repo <owner/repo> --global <login>
```

Fallback if this skill checkout lacks the helper:

```bash
~/Projects/clawdbot/.agents/skills/openclaw-pr-maintainer/scripts/github-activity.sh --repo <owner/repo> --global <login>
```

Also use `github-author-context` when a PR needs deeper trust judgment, especially for OpenClaw, security-sensitive changes, broad PRs, new accounts, or unusual author behavior. Prefer existing contributor notes first:

```bash
~/Projects/maintainers/scripts/clawtributors find github <login>
```

Trust output must stay factual:

```text
Trust: @login; acct 2021-04-03; repo 2 PRs/1 issue/0 commits in 12mo; GitHub 9 PRs/3 issues/12 reviews; signal: known contributor / new drive-by / bot / unknown.
```

Do not treat trust as proof. It changes review depth, not correctness.

## Item Evaluation

Classify each item:

- `bug`: require repro/log/failing test/current-main proof when feasible; identify root cause before recommending fix/merge.
- `feature`: require end-to-end test plan. If live validation needs a provider key, account, device, service, model access, or paid API, say exactly what credential/access is missing before work can be considered complete.
- `dependency`: explain package group, major/minor risk, failing checks, runtime/engine changes, and whether to split.
- `security`: raise priority, require careful code-path proof, tests, and trust/context; do not merge on rationale alone.
- `docs/internal`: lower risk, but still explain user-visible relevance and stale/generated churn risk.

Judge:

- `Fit`: good / mixed / poor, with one reason.
- `Risk`: low / medium / high, with blast radius.
- `Proof`: current CI, local repro, failing test, live E2E, or missing proof.
- `Blocker`: first-time contributor CI approval, failing check, missing key, unclear product direction, stale branch, untrusted/broad diff, no repro, conflicts.
- `Next`: approve CI, run test, request repro, split PR, patch locally, merge after green, close with proof, or defer.

## Fast Queue Map

Use this only when the scope is broad. Start with repo-level queue maps. This finds repos with open issues and/or PRs and gives counts.

PR queue, primary triage order:

```bash
repobar_cmd repos \
  --scope all \
  --only-with work \
  --owner steipete \
  --owner openclaw \
  --sort prs \
  --json
```

Issue pressure, second pass when issues matter:

```bash
repobar_cmd repos \
  --scope all \
  --only-with work \
  --owner steipete \
  --owner openclaw \
  --sort issues \
  --json
```

Use `--forks` and `--archived` only when the user says "all", "everything", or asks for archaeology. Default triage should omit forks and archived repos unless their queues are specifically relevant.

For a compact terminal view:

```bash
repobar_cmd repos --scope all --only-with work --owner steipete --owner openclaw --sort prs --plain
```

Useful `jq` summary:

```bash
repobar_cmd repos --scope all --only-with work --owner steipete --owner openclaw --sort prs --json |
  jq -r '.[] | [.fullName, .openIssues, .openPulls, .activityTitle, .activityActor] | @tsv'
```

When summarizing a PR-sorted queue, preserve RepoBar's PR-count order. Do not include a lower-PR repo while omitting a higher-PR repo from the same owner scope. Zero-issue repos with open PRs, for example `openclaw/crabbox`, are still triage-relevant.

## Detail Pass

After a broad queue map, inspect only the top repos unless the user explicitly wants exhaustive detail.

```bash
repobar_cmd issues <owner/name> --limit 50 --json
repobar_cmd pulls <owner/name> --limit 50 --json
repobar_cmd ci <owner/name> --limit 20 --json
repobar_cmd activity <owner/name> --limit 20 --json
```

For PRs that look mergeable or suspicious, switch to `gh` for maintainer-grade state:

```bash
gh pr view <n> --repo <owner/name> --json number,title,state,author,isDraft,mergeStateStatus,reviewDecision,statusCheckRollup,updatedAt,url
gh pr diff <n> --repo <owner/name> --patch
gh run list --repo <owner/name> --branch <branch> --limit 10
```

For issues that may already be fixed, switch to `gh issue view`, then inspect current source before commenting or closing.

For OpenClaw/ClawdBot queues, use the OpenClaw maintainer pass when useful:

- search duplicates/related threads with `gitcrawl` if available;
- use the activity helper for opener/author identity;
- suppress top-maintainer noise unless the user asks for maintainer-owned work;
- prefer external/user-reported bugs and PRs with clear proof.

## Local Cross-Check

Use this when the task mentions local project state, dirty repos, or "what do I own here".

```bash
repobar_cmd local --root "$HOME/Projects" --depth 1 --limit 200 --plain
repobar_cmd local --root "$HOME/Projects" --depth 1 --sync --limit 200 --json
```

Do not run destructive local actions (`local reset`, branch deletes, checkout moves) unless the user explicitly asks.

## Triage Heuristics

Prioritize:

- PRs with green or nearly-green CI, recent maintainer activity, or low-risk dependency/docs/test changes.
- Repos with high open PR counts but recent activity, because they often hide obvious cleanup.
- Issues that are reproducible, recently reported, or block releases.
- Security, release, auth, install, CI, and data-loss reports before cosmetic items.
- Bugs with clear current-main reproduction and narrow owner path.
- Features only when live validation is possible or the missing access is explicit.

Deprioritize:

- Archived repos unless the user asked for them.
- Fork-only queues unless the fork is actively maintained by Peter.
- Old broad feature requests with no reproduction or owner signal.
- Repos with missing/removable remotes until local state is clarified.
- Feature/provider PRs that need unavailable API keys or accounts for end-to-end proof.
- Broad generated changes without a clear user problem, test plan, or trusted author signal.

## Output Shape

For current-project triage, answer with:

```text
Repo: owner/name
Source: gh list/view/diff/checks, local source/tests where inspected

Immediate:
- #123 PR: title
  What: one-line summary in plain words.
  Type/Fit/Risk: bug|feature|dependency; good|mixed|poor; low|medium|high because ...
  Trust: @login; acct date; repo/global activity; known/unknown/bot.
  Proof: CI/repro/test/e2e state.
  Blocker: none / missing key / first-time CI approval / failing lint / unclear direction.
  Next: exact maintainer action.

Needs judgment:
- #124 issue: ...

Defer/close:
- #125 issue: ...

Skipped:
- <why>
```

For a broad scan, answer with:

```text
Owners scanned: steipete, openclaw
Source: RepoBar <command summary>, plus gh for selected PRs/issues

Top queues:
- owner/repo: X issues, Y PRs; why it matters; next action

Immediate actions:
- <small obvious merge/fix/comment/rerun, with item summary>

Needs judgment:
- <larger/ambiguous queues, with item summary>

Skipped:
- archived/forks/missing access/etc.
```

When the user asks to act, keep going: inspect the selected PRs/issues with `gh`, rerun/fix CI, comment/close/merge only with evidence, and report exact commands/proof.
