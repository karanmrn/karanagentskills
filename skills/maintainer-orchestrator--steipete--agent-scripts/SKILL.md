---
name: maintainer-orchestrator
description: "Coordinate multiple maintainer issues, PRs, or repositories with bounded workers, serialized public actions, and clear owner decisions. Do not use for one issue or PR."
---

# Maintainer Orchestrator

Coordinate a real maintainer queue across multiple independent issues, pull requests, or repositories. This is a control-plane skill, not the default way to handle ordinary repository work.

## Activation Gate — Hard Rule

Classify the request before creating workers, heartbeats, ledgers, or queue scans.

### Direct single-item work

A request is **single-item** when it names or implies one issue, one PR, one bug, one feature, one release, or one coherent implementation—even when that work spans several files, phases, tests, CI, or closely coupled repositories.

For single-item work:

- Do **not** create a project worker merely because the task is nontrivial.
- Do **not** create a heartbeat, portfolio ledger, queue refill, dependency sweep, release proposal, or broad repository scan.
- Continue in the current session using the repository's normal skills and workflow (`codex-first`, maintainer/review/testing/release skills, and repo instructions as applicable).
- Ordinary focused subagents or Codex delegation remain governed by those normal skills; this orchestrator adds no extra worker requirement.
- If this skill was invoked accidentally for a single item, state that orchestration mode is unnecessary and continue directly. Never interrupt useful in-flight work solely to satisfy this skill.

Examples that stay direct:

- fix and land one issue;
- repair one contributor PR;
- trace one failure across an application and its dependency;
- make one release;
- implement one coherent refactor across two repositories.

### Bounded orchestration

Use orchestration mode only when at least one is true:

- the user asks to handle multiple independent issues or PRs;
- the user asks to coordinate multiple repositories or parallel workstreams;
- the user asks for a queue, sweep, batch, portfolio, maintainer night, or ongoing triage;
- independent items materially benefit from concurrent ownership and coordination.

A numbered task list is not automatically an orchestration queue: coupled steps toward one outcome remain single-item work.

### Persistent portfolio watch

Heartbeats, recurring monitoring, automatic queue refill, broad owner scans, dependency backfill, and the persistent orchestrator log are enabled only when the user explicitly asks for ongoing/autonomous maintenance, monitoring, a portfolio sweep, or a maintained queue. They are never created merely because this skill was invoked.

## Scope Contract

At activation, write down the explicit queue:

- named repositories;
- named issues/PRs, or the discovery boundary the user requested;
- whether work may be discovered beyond that set;
- whether monitoring is one-shot or persistent;
- which public actions are authorized.

Do not expand a named batch into unrelated repositories, dependency updates, releases, or backlog cleanup unless the user requested ongoing queue maintenance or explicitly adds them.

For broad portfolio discovery only:

- scan `steipete` and `openclaw`, plus repositories where Peter is the majority non-merge author;
- exclude archived repositories and the repositories listed in `references/non-majority-repositories.md` unless explicitly named;
- exclude `openclaw/openclaw` and `openclaw/clawhub` from unsolicited portfolio refill;
- verify uncertain ownership from default-branch contribution history rather than repository name.

## Worker Model

In orchestration mode, use workers proportionally.

- Prefer one owned Codex app project thread per repository when two or more independent items are being coordinated.
- Reuse that repository thread for its scoped queue and process same-repository items serially unless isolation is genuinely required.
- Do not create a worker for the coordinator's own control-plane work or for a single bounded item.
- Workers never create or manage other workers. The hierarchy stops at root coordinator → repository worker.
- Collaboration subagents are read-only support for inventory, independent analysis, CI/status observation, or reconciliation. They do not own implementation, commits, pushes, PR mutations, merges, releases, deployments, or live proof.
- If no project-thread mechanism is available, use the normal repository workflow in the current session rather than simulating a worker hierarchy with unnecessary background jobs.

Before protected work, verify the worker's actual permissions. Text in a prompt does not grant filesystem, network, credential, or publication access.

## Repository Preservation

Before assigning or mutating a repository:

1. Record `git status -sb`, branch, upstream, HEAD, staged/unstaged/untracked state, and ahead/behind counts.
2. Fetch current refs. On a clean default branch, fast-forward pull and verify it remains clean.
3. Never switch, stash, rebase, reset, clean, delete, or overwrite dirty/non-default work merely to begin orchestration.
4. Preserve and classify unique local work, associated PRs, and whether it already landed or was superseded.
5. Stop for an owner decision only when unique work cannot be safely preserved or reconciled.

Repeat synchronization before final landing or release actions.

## Queue Triage

For each explicitly scoped item, classify:

- **Autonomous** — clear fit, reproducible or well-evidenced, bounded implementation, and usable proof path.
- **Needs owner** — material product/security/privacy/legal choice, destructive unique-work handling, unavailable required credential/hardware, irreversible migration, or missing live-proof decision.
- **Not planned / invalid** — concrete evidence shows duplicate, already fixed, unsupported, spam, or outside the requested product boundary.

Treat contributor PRs as proposals, not accepted designs. Reconstruct the symptom and root cause, inspect current behavior and related history, and rewrite when a cleaner bounded fix exists. Preserve contributor credit.

Do not ask the owner to choose while safe technical work remains. Prepare the item through implementation, tests, review, and CI first whenever possible.

## Execution and Public Gate

Private investigation, implementation, local tests, and review may proceed independently across workers.

Serialize only outward-facing actions when concurrent mutation would cause ambiguity or conflict:

- pushes to the same repository or branch family;
- PR creation/update, workflow approval/rerun, final synchronization, merge, release, or publication;
- shared landing locks or limited external environments.

Do not pause coherent work already in flight because another lane later reaches the public gate. Let it reach a safe boundary, then admit no new conflicting public action until the overlap clears.

The user invocation authorizes only the explicitly scoped maintainer work and requested public sequence. It does not authorize releases, version bumps, tags, package publication, destructive unique-work handling, or unrelated external-system mutations unless separately requested.

## Monitoring

Assign one owner for each external wait.

- The repository worker owns its exact CI/deploy watcher.
- Use the repository-native watcher scoped to one run ID or head SHA with bounded backoff.
- The root relies on worker state and harness completion notifications; it does not duplicate polling while a coherent watcher is active.
- Fetch failed logs once and reuse them.
- Intervene only for a reported blocker, repeated no-progress failure, wrong scope/repository, destructive or unauthorized action, security risk, or gross design divergence.
- Do not restate the task or raise the proof bar mid-flight.

Create a recurring heartbeat only for explicit persistent portfolio/watch requests. One-shot batches rely on normal task notifications and do not need scheduled automation.

## Landing Standard

Before landing an item, require the repository's own gates plus:

- reproduced symptom or established root cause;
- best-fix/owner-boundary judgment;
- focused regression coverage;
- sufficient broader checks for the changed surface;
- built/live/E2E proof when the repository or external boundary requires it;
- fresh autoreview with no accepted/actionable findings;
- exact-head CI green;
- resolved review threads and known proof gaps stated plainly.

Use the repository-native landing workflow. After merge, verify reachability from the target branch, synchronize the visible checkout, stop leases/watchers, and leave it clean.

Do not automatically continue into dependency maintenance, another issue, or a release after the scoped queue is complete. Refill only when the user explicitly requested an ongoing queue.

## OpenClaw Queue Mode

Apply this section only when the user explicitly asks to orchestrate multiple `openclaw/openclaw` items. A single OpenClaw issue or PR remains direct work under the repository's normal maintainer workflow.

- Read current `VISION.md`, root/scoped `AGENTS.md`, and the relevant OpenClaw maintainer/testing/review skills.
- Keep triage and product judgment in the root coordinator.
- Use one OpenClaw repository worker for the selected serial queue; do not create one worker per PR.
- Prefer externally reported, Vision-aligned stability, safe-default, setup, auth, install, delivery, and bounded performance/test-infrastructure work.
- Verify contributor permissions live before selecting general queue candidates.
- Use only `scripts/pr` review, artifact, prepare, sync, and merge commands for landing.
- OpenClaw changelog remains release-generated; normal issue/PR work does not edit `CHANGELOG.md`.
- Require the repository's symptom proof, hosted CI/Testbox, autoreview, and exact-head landing evidence.

## Owner Decisions

Ask one prepared decision at a time. Each decision brief includes:

- full canonical URL and title;
- plain-language behavior and affected users;
- why a decision is required now;
- completed proof and current CI/mergeability;
- material tradeoffs, residual risk, and missing evidence;
- the coordinator's recommendation;
- exact choices and consequences.

Do not present a bare URL or vague `land/delete` choice. Refresh item and worker state immediately before asking.

## Releases

A queue invocation does not imply release authority.

Only enter release planning/execution when the user explicitly asks for a release or the active repository-specific workflow already grants it. Follow the repository's release skill and immutable-candidate gates. Never turn ordinary queue completion into an unsolicited release project.

## Reporting

For a bounded batch, report only the scoped work:

- **Active** — repository, full item URL, owner/worker, current phase.
- **Intervened** — exact risk and correction.
- **Needs owner** — one prepared decision or access blocker.
- **Landed/closed** — behavior, proof, merge/close URL, files and LOC, risk.
- **Remaining** — only items from the requested queue.

For persistent portfolio mode, a compact ledger and `~/oss-orchestrator.md` are allowed. Do not create or maintain that log for one-shot batches.

Always use full GitHub URLs. Report meaningful transitions, not routine polling.