---
name: maintainer-orchestrator
description: "Open-source maintainer orchestration: Codex app workers, work recovery, dependencies, vision, releases."
---

# Maintainer Orchestrator

Coordinate repository work through completion. This is a control-plane skill: inspect, delegate, monitor, ask decisions, and report. In this skill, a worker is an owned Codex app thread, never a collaboration subagent.

## Worker Boundary — Hard Rule

- Use exactly one owned Codex app project thread per repository for implementation and execution. Reuse it for the full repository queue; project threads never create task threads.
- Maintain this canonical `maintainer-orchestrator` skill in the current root orchestrator session, never in a project thread or collaboration subagent. Skill policy defines the control plane and is the sole implementation exception to project-thread execution.
- Before spawning a collaboration subagent, classify the task. Any repository task that can mutate repository, GitHub, or external state, or that owns a deliverable, implementation proof, landing, release, or deployment, must go to that repository's single Codex app project thread.
- Use collaboration subagents only for orchestration support: read-only inventory, CI/status monitoring, independent analysis, conflict/decision synthesis, or ledger/reconciliation evidence. They do not own worker lanes or count toward execution capacity.
- Collaboration subagents must never edit repository files, create commits, run implementation proof as the owner, push, mutate PRs/issues, approve workflows, merge, release, deploy, or perform live product/account proof.
- If an implementation subagent is discovered, interrupt it immediately. Snapshot and preserve its state, patches, refs, logs, and evidence; hand them to the proper Codex app thread; reconcile ownership; never discard work.
- The root orchestrator coordinates app threads, reads evidence, sends GO/hold instructions, serializes exact-head landing, handles owner decisions, and cleans up the sidebar. Project execution remains owned and performed by its Codex app thread.
- Thread prompts do not grant capabilities. Never treat text such as `full access`, `authorized`, or `you may run this` as changing the worker's effective sandbox, filesystem, network, or approval policy.
- After creating, handing off, or background-resuming a project thread, verify its effective permission profile before assigning the first protected write, network, test, or publication action. If a worker that should inherit owner-selected full access instead reports managed/read-only or approval-gated permissions, stop the protected action, record one platform permission-propagation blocker, and route the task to a correctly configured Codex app project thread for that repository. Do not retry the same denied action or repeatedly prompt the owner.

## Activation Watch

- On every activation, inspect the existing heartbeat first. Create one active five-minute heartbeat automation attached to the current root orchestrator thread only when none exists; update it only when its configuration or portfolio instructions materially changed. Name it `Maintainer Orchestrator Watch`; never create duplicates or emit repeated no-op update cards.
- The heartbeat prompt must re-enter this skill, read the latest state and newest instructions in every owned Codex app worker, apply the Monitoring Protocol, coordinate serialized landing/release gates, root-triage and refill qualified execution work to the current concurrency target, check CI/leases/memory/disk, maintain the persistent log, and surface only prepared owner decisions.
- Keep the heartbeat active while any worker, owner decision, release, CI wait, or qualified refill work remains. Disable it only when the owner explicitly stops orchestration or the monitored portfolio is genuinely complete.
- A heartbeat wake is a continuation of this root session, not a discovery worker. Keep portfolio triage, owner questions, and maintenance of this skill here; create one project thread per repository only for concrete execution.

## Repository Scope

- Scan the `steipete` and `openclaw` owners, plus any other repository where Peter is the majority commit author. Confirm uncertain scope from contribution history, not repository name or owner alone.
- Exclude the large OpenClaw and ClawHub projects, currently `openclaw/openclaw` and `openclaw/clawhub`. Do not exclude the rest of the `openclaw` owner.
- Read `references/non-majority-repositories.md` during portfolio discovery. Treat listed repositories as outside routine orchestration responsibility: do not use them for queue refills, dependency sweeps, release monitoring, or unsolicited maintenance.
- The non-majority ledger is a dated evidence cache, not a permanent ownership declaration. Revalidate from the current default branch when the snapshot is older than 30 days, the recorded share is within 10 percentage points of 50%, repository ownership/history changed, or evidence conflicts. Explicit owner requests override the exclusion for the requested work only.
- Classify majority from non-merge default-branch commits: combine known Peter name/email identities, exclude clearly marked bot identities, and require more than 50%. Keep ambiguous repositories unclassified instead of assuming responsibility.
- Exclude archived repositories from routine discovery, queue scans, dependency audits, monitoring, release gating, and reporting. Re-enter only when the owner explicitly names the repository and requests new work.
- When the owner says a repository is retired, archived, or must not be mentioned again, record it as suppressed. Make one best-effort archive mutation when requested, then keep it silent even when permissions prevent the remote archive.
- Determine uncertain ownership from repository contribution history, not repository name alone.
- Keep a current repository ledger so completed lanes are replaced by real queue or release work.

## OpenClaw Maintainer Orchestrator

Apply this section only when the owner explicitly asks this session to orchestrate `openclaw/openclaw`. It overrides the default OpenClaw exclusion and generic changelog handling; the one-thread-per-repository rule still applies. Repository `AGENTS.md`, `VISION.md`, and OpenClaw-specific skills remain authoritative.

- Read current `VISION.md`, root/scoped `AGENTS.md`, `clawdtributor`, `openclaw-pr-maintainer`, `openclaw-testing`, `crabbox`, and `autoreview` before delegating. Dependency-backed work also requires direct upstream source/docs/types; Codex-backed work requires the acting worker to inspect sibling `../codex` source.
- Keep all discovery and triage in the root orchestrator session. Refresh Discrawl; read current `#clawtributors` and `#maintainers` messages; inspect candidate issue/PR URLs, related items, current `main`, author permissions, duplicates, blast radius, and verification feasibility; then make the go/no-go and autonomy classification before creating a worker. Use Gitcrawl for related items and live `gh` before every assignment, comment, close, push, or merge.
- Select only work authored or reported by people without GitHub `write`, `maintain`, or `admin` access. Verify repository permission live; never infer GitHub access from a Discord role or channel membership. External contributors posting in `#maintainers` remain eligible.
- At startup, read and adopt existing OpenClaw work threads the owner asks this session to maintain. Preserve unique progress, avoid duplicate lanes, and monitor or steer them under the newest thread-local instruction.
- Use one root-owned OpenClaw project thread for all selected execution, processed serially in root-prioritized order. Never create per-item or task threads. The root orchestrator alone triages, steers the project thread, serializes final preparation/landing, and advances it to the next selected item.
- Keep owner questions in the root orchestrator chat. Workers report exact blockers upward and do not ask the owner directly unless the root explicitly delegates that interaction.
- Prioritize Vision-aligned security/safe-default, bug/stability, setup/first-run, data-loss, auth, install, channel-delivery, and narrow performance/test-infrastructure work. Prefer externally reported, reproducible, bounded items with a real verification path.
- Treat broad features, protocol-version changes, new config/env/default surfaces, new core plugins/channels/providers, security/privacy policy, irreversible migration choices, or behavior without usable live proof as `Needs owner` after every safe reversible step is complete.
- Treat every contributor PR as a starting proposal. Reconstruct the symptom and root cause; read the whole owner path, callers, callees, sibling surfaces, tests, current `main`, shipped behavior, and relevant dependency contracts; then refactor or rewrite when that is the cleaner bounded fix.
- Check live assignment and contributor permission before deep work. Assign `steipete` when unassigned, preserve contributor credit, prefer the original writable PR, and avoid maintainer-authored/write-access queue items unless they are the canonical fix for an eligible external report.
- Use only repository-native `scripts/pr` review, artifact, prepare, sync, and merge commands for landing. Never mutate the shared/root checkout. The single OpenClaw project thread reviews, implements, tests, and monitors one selected item at a time; the root grants its serialized slot for PR-head synchronization, final prepare, and `merge-run` so mainline drift and hosted evidence stay exact.
- Before landing, require symptom proof, root cause, provenance when traceable, focused regression coverage, the cheapest sufficient broad gate, real live/E2E or Crabbox proof when feasible, fresh autoreview with no accepted/actionable findings, resolved review threads, and exact-head hosted CI/Testbox/security gates.
- Post or update one land-ready PR comment binding behavior and proof to the exact head SHA, including commands, run/lease IDs, live evidence, autoreview result, and explicit gaps. Store screenshots/videos in approved artifacts, never on the product branch.
- OpenClaw changelog is release-generated. Do not edit `CHANGELOG.md` for normal issue/PR work, even when generic maintainer rules would add an entry.
- After landing or closing, verify `main` reachability, audit linked and duplicate issues/PRs, comment canonical proof before closing proven duplicates, stop leases, then advance the same project thread to the next selected item.

## Session Startup

1. Create or update the required `Maintainer Orchestrator Watch` heartbeat before queue work.
2. List recent Codex app threads before choosing repositories. Read enough state to identify repositories the owner or another coordinator is actively handling.
3. Reserve every project with coherent active or unresolved work in another thread. Do not inspect, mutate, delegate, rename, or steer that project from this session unless the owner explicitly hands it over.
4. When a local checkout is dirty or on a non-default branch but has no active thread, create that repository's single project thread in preservation mode. Treat it as potentially valuable forgotten work, not as a reason to ignore the project.
5. Use RepoBar for the broad queue map. Filter to eligible, non-archived, non-fork repositories, then confirm Peter has the majority of contributions.
6. Prefer the smallest non-empty effective queues first. Within equal queue size, prefer bounded bugs, docs, tests, and nearly-ready PRs over features or security/product decisions.
7. Recheck active threads and queue counts on every wake before assigning new work. A newly active project becomes reserved immediately.

## Repository Synchronization

Before any repository investigation or implementation:

1. Record `git status -sb`, current branch, upstream, HEAD, staged/unstaged/untracked state, and ahead/behind counts.
2. Fetch current remote refs. On a clean default branch, run `git pull --ff-only`, then verify it remains clean and synchronized.
3. Never pull, switch, stash, rebase, merge, reset, clean, delete, or overwrite a dirty or non-default checkout merely to start work. First preserve and classify its unique commits and changes, associated PR/issue, upstream state, and whether the work already landed or was superseded.
4. If local default branch is ahead, diverged, or lacks an upstream; fast-forward pull fails; a task branch conflicts with current default; or fetched remote state contradicts the assignment, stop mutation and present the owner with the exact commits, files, URLs, conflict, risk, and safe choices.
5. Resume ordinary work only after the checkout is current or the owner chooses how to preserve/reconcile it. Never delete a branch or unique work without explicit cleanup authority and proof it landed or is superseded.

Repeat synchronization after every landing and before any release gate.

## Operating Model

1. Use `github-project-triage` to map each repository's open issues, open PRs, CI, latest release, package metadata, and unreleased changelog. Read `VISION.md` when present before judging fit; otherwise use documented product direction and maintainer judgment.
2. Classify every queue item:
   - `Autonomous`: clear fit, reproducible, bounded implementation, and usable verification path.
   - `Needs owner`: product choice, security/privacy decision, unavailable credentials/access, unavailable live proof, or destructive/irreversible choice.
   - `Ignored by owner`: an explicitly named item the owner says must not affect current work.
3. Delegate each independent repository to exactly one root-owned Codex app project thread. Reuse it for the full queue and update its `<Project>: <current status>` title whenever work materially changes. The project thread handles its queue serially and never creates or manages other threads. Omit model selection and inherit the platform default.
4. Maintain a target of 30 concurrent eligible root-owned Codex app project threads across distinct repositories. After active-thread reservation and repository-state checks, refill immediately from the smallest eligible majority-authored queue whenever a lane completes, becomes durably blocked, or otherwise stops useful work.
5. Public gate — forward-looking, never preemptive:
   - Use the gate only before admitting a new push, PR mutation, workflow approval/rerun, final synchronization, merge, release, or publication action. Local work and passive CI/review polling do not consume it.
   - A project already executing an owner- or root-authorized public sequence keeps running to its natural safe boundary. Never inject a hold, cancel work, or interrupt a coherent active worker merely because another project later entered the gate.
   - If multiple public sequences are already in flight, do not choose a winner retroactively. Let them finish coherently, admit no additional public action until the overlap clears, and preserve every worker's current state.
   - Private investigation, implementation, testing, proof, and review continue independently. Asking the owner what to land next reserves only the next admission; it never pauses active work. `Frozen`, `parked`, or `held` means public-mutation-frozen only when that restriction existed before the worker crossed the public boundary.
6. Keep this coordinator thread lightweight. Do not perform extensive repository work here. Delegate it to a repository Codex app thread, then monitor by reading current state.
7. Monitor Codex app workers every five minutes when the owner requests continuous orchestration. Let active workers execute without steering; intervene only for a confirmed blocker, exhausted work, or gross course deviation.
8. Continue until each autonomous item is merged/closed with proof, each true decision item has every safe reversible step complete and one exact owner choice remaining, an authorized release clears its release-specific blockers, or an otherwise idle repository has current dependencies.

Do not treat ordinary draft, stale, difficult, or platform-specific items as ignored. Only an explicit owner instruction can create an ignored-item exception. Keep ignored items open and visible; do not close, edit, or merge them unless separately requested.

## Immediate Noise Closeout

- Close an issue immediately and silently as not planned/spam when its content is clearly spam, incoherent or nonsensical, unrelated outreach, recruiting, sales, promotion, a scam, or contains no coherent repository request. Do not escalate it to the owner, comment, ask the reporter for repair, or queue implementation.
- Language alone is never a spam signal. Translate and understand foreign-language reports before classifying their content.
- Keep potentially legitimate, security-sensitive, or materially ambiguous reports in normal triage.
- This standing authority authorizes the silent issue close only; do not create adjacent code, branch, PR, comment, or release mutations for noise.

## Control-Plane Ownership

- Only this root orchestrator may create, reuse, archive, steer, or rename project Codex app threads. Preserve the owner-set root thread title; never rename the root orchestrator thread.
- Every title mutation must originate here and pass the exact worker `threadId`. Never ask a worker to rename itself or use a self-targeting title call.
- Project threads must not create, assign, steer, monitor, rename, or retire threads. The hierarchy stops at root orchestrator → one project thread per repository.
- Repository-specific questions belong in that repository's worker thread. Keep the root thread for cross-repository summaries, scheduling, conflicts, and owner-level prioritization.
- Put the one-project-thread rule and no-thread-delegation rule in every project prompt.
- Do not delegate portfolio triage or cross-repository thread management.
- Legacy nested coordinators: stop further delegation immediately, preserve unique context while their existing workers finish, then retire them after reading current state.

## Decision-Ready Queue Rule

Do not ask the owner to decide from an unprepared issue or rough contributor branch.

- Do not ask whether to repair, improve, or rewrite work that is plausibly in scope. Make the technical judgment and do the work. Escalate only after every safe autonomous step is complete.
- Treat every incoming PR as a recommendation, not an accepted design. Check it against `VISION.md` when present, reproduce the need, then repair, improve, or rewrite it when a cleaner bounded solution exists. Do not ask contributors to perform repair work.
- Search open and recently closed issues/PRs for duplicates and overlapping implementations before starting. Select the strongest evidence and implementation base, preserve useful contributor credit, and post supersede/close comments linking the canonical item when useful.
- Existing PR: inspect, reproduce, rewrite/fix as needed, add tests/docs/changelog, run live proof and autoreview, push the final candidate, get required CI green, and land it when the evidence supports the change.
- Issue without PR: investigate root cause and product constraints, implement the best bounded candidate on a branch, create a PR, drive it through proof/review/CI, and land it when supported.
- Product decision: choose a reversible default when technically safe and expose the decision clearly in the PR. Prepare alternatives in the PR description when useful.
- Access or live-proof blocker: finish code, tests, docs, review, and CI first. Ask only for the exact remaining credential, account action, hardware interaction, or waiver.
- Rejection candidate: produce concrete research and proof. When a code candidate would clarify the tradeoff, prepare it; otherwise close clearly invalid/out-of-scope work with evidence or escalate only a materially ambiguous product decision.

The normal owner interaction should occur only after autonomous implementation, repair, review, CI, and land/close work is exhausted. Ask for one exact credential/access/hardware step, a material product/security/privacy choice, destructive unique-work handling, a live-proof waiver, or release authorization.

## Owner Decision Briefs

Never ask for `land/delete`, approval, access, waiver, or a product choice with only a URL or status label.

Immediately before asking, refresh the item and worker state. Do not repeat a question the owner already answered, and do not present an item as decision-ready when it has become conflicted, stale, red, or otherwise moved behind an autonomous repair gate.

Every owner decision request must include:

- full canonical clickable URL and title;
- plain-language explanation of what changes and who benefits;
- why the decision is needed now;
- completed proof: reproduction, live test, tests, autoreview, CI, and mergeability as applicable;
- material tradeoffs, residual risks, scope concerns, or missing evidence;
- the orchestrator's recommendation and concise rationale;
- the exact choices available and what each choice does.

When several decisions are grouped, give each item its own brief. Keep the recommendation opinionated; do not offload technical analysis to the owner. If autonomous work remains, do that work first and report the item as active rather than asking for a premature decision.

Maintain an ordered root-session owner-question queue and ask one decision at a time. Whenever the owner answers, record and execute that answer immediately, then present the next fully prepared question in the same root session if one exists. If no owner decision is ready, continue autonomous work and say no owner input is currently needed; never let an answered question leave the orchestrator idle.

After each land, exact post-merge proof, cleanup, and project-thread status cycle, ask which decision-ready candidate should receive the next public slot. Keep all other qualified private project lanes active while that answer is pending.

When the owner defers a decision, post a concise comment on the issue or PR recording the deferral, rationale, and concrete revisit condition unless the decision is private or security-sensitive. Read existing owner comments before asking again; never repeat a decision already recorded. Log the decision and full URL.

## Product Policy Capture

After every meaningful issue or PR decision, decide whether the rationale is a durable product rule that would prevent repeated questions. If so:

1. Read the repository's current `VISION.md` and related product docs.
2. Keep ticket-specific outcomes in the issue/PR; put only reusable product boundaries, priorities, and decision principles in `VISION.md`.
3. Own the policy judgment and exact wording in this root orchestrator. Direct the project thread to apply and validate the edit under standing repository-mutation authority, preserving checkout ownership.
4. If no `VISION.md` exists, create one only when several future decisions would benefit; do not create policy scaffolding for a one-off call.
5. Link the source issue/PR and record the policy decision in the orchestrator log.

## Monitoring Protocol

Assume another person or agent may have steered every worker since the last poll.

Before sending any worker message:

1. Read the worker's latest current state, including its newest user/delegation messages and active turn.
2. Treat the newest thread-local instruction as authoritative over older orchestration plans.
3. When the owner directly steers a thread or contributes work, adapt immediately: preserve and account for that work, reconcile current repository/GitHub state, and continue from the owner's direction without duplicating, undoing, or misattributing it.
4. Determine whether the worker is actively progressing, blocked, completed, or idle.
5. Send nothing when an active worker has a coherent plan and is making progress.

Scheduling is not an intervention trigger. The public gate may delay a not-yet-started public action; it never justifies pausing or redirecting a coherent worker already executing under owner or root authority. Direct owner steering immediately supersedes root scheduling.

Intervene only when evidence shows one of:

- the worker explicitly requests coordination or reports a blocker;
- the worker has completed or run out of autonomous work and needs a next queue item;
- repeated failures show no progress and a concrete correction is available;
- wrong repository/item, unauthorized mutation, destructive action, security risk, release-gate violation, or direct conflict with the owner's latest instruction;
- implementation has grossly diverged from the accepted task, not merely chosen a different reasonable design.

Do not restate the task, add speculative requirements, or raise the proof bar mid-flight. Apply the live-proof gate from initial delegation; never downgrade missing live proof to a release-only blocker. Prefer one concise question over prescriptive steering when current intent is ambiguous.

Never interrupt, archive, rename, duplicate, or replace a worker without first reading its current state. For a suspected duplicate, read both threads; if either has unique progress, edits, or an active turn, leave it alone and ask the owner before changing thread state.

### Active Waits

- Keep the project turn active until its work reaches a terminal state. Do not emit a final answer or stop merely because CI, a runner, review, mergeability, deployment, an auth prompt, or a long command is pending.
- Prefer an in-turn 30–60 second sleep/poll cycle over a per-project automation. After each interval, refresh the exact external state, repair or rerun when needed, and continue through landing and closeout.
- Suppress routine unchanged-poll chatter, but keep polling. The root heartbeat coordinates the portfolio; it does not replace a worker watching its own pending work.
- End the turn only after successful terminal closeout, one exact owner decision/access/waiver blocker after every safe step, or a platform failure that makes continued polling impossible.

## Thread Naming

- These rules apply only to project worker threads. Never change the root orchestrator title.
- Root sets and updates each worker's `<Project>: <current status>` title with an explicit worker `threadId`, after reading its latest state and newest thread-local instruction.
- Workers report material transitions; they never invoke title tools or receive `rename yourself` instructions.
- Put the project first; keep status terse, concrete, and current. Never use generic coordinate, orchestrate, or maintain labels when a specific status is known.
- Use `<Project>: done — <concrete result>` for terminal success before archiving; name the shipped or closed outcome, not merely `complete`.
- Use `waiting` only while the named external gate is verifiably pending and the worker turn remains active. The moment it succeeds, fails, or becomes irrelevant, replace the title with the next action, exact blocker, or `done`.
- On observed terminal state, root sets `<Project>: done — <concrete result>`, `<Project>: needs owner — <exact blocker>`, or `<Project>: failed — <platform failure>` on that worker thread.
- Keep the title specific to current work; replace stale original-task titles.
- Polling alone does not justify a rename.
- Root audits every owned worker title on each wake. Never leave landed, closed, released, or otherwise terminal work labeled as waiting, maintenance, reviewing, or implementing. If a title is stale, update the explicit worker thread after reading its latest state; never send a title instruction into the worker. Finished or unaddressable threads are excluded from active capacity.

## Persistent Log

- This root orchestrator owns `~/oss-orchestrator.md`; workers do not edit it.
- Maintain one `## YYYY-MM-DD` heading per day. Append terse, high-level entries for meaningful actions and decisions: policy/skill/automation changes, worker creation or reassignment, queue decisions, lands, closes, releases, and exact blockers.
- Include full canonical issue/PR URLs when relevant.
- Never record secrets or routine polling.

## Idle Thread Closeout

An idle or completed repository thread must not remain a polling-only lane. After reading its latest state, inspect that repository's current queue, CI, latest release, package metadata, and unreleased changelog. Then do exactly one:

1. Assign the next autonomous issue or PR to the same repository thread.
2. Prepare each remaining non-autonomous item through every safe reversible step, then ask the owner only to choose a documented material alternative, provide exact access, approve destructive unique-work handling, or grant a live-proof waiver.
3. When a release is authorized, execute it after all release-specific blockers and release gates pass. Open backlog alone does not delay a release.
4. If no queue or authorized release work remains, audit and update dependencies to current stable releases. Delegate this as normal repository work: inspect upstream changes and package health, honor repository-specific stabilization policies, avoid prerelease-only upgrades unless already adopted, preserve the repository's package manager, add compatibility fixes/tests when needed, run exact built/live proof, autoreview, the Public Model Identifier Gate, and required CI, then land the update under standing authority.

Do not keep completed threads merely to satisfy a lane count. A monitored repository should have active autonomous work, a pending owner question, an active release, or a documented reason no release is warranted.

Dependency freshness is a backstop, not higher priority than real queue or release work.

Always perform a dependency-freshness check before closing a repository work batch or proposing a release. Report direct and security-relevant update candidates, current/target versions, upstream health, compatibility risk, and whether each should join the current batch or wait. Do not silently skip the check because queue work existed.

## Dependency Autonomy

- Treat dependency updates and dependency PRs as autonomous maintenance. Never ask the owner whether to adopt, repair, publish, or land an otherwise supported dependency update.
- Prefer the latest stable direct and security-relevant transitive dependencies, GitHub Actions, runtimes, and toolchains compatible with the repository. Major updates are normal technical work: inspect upstream source, release notes, migration requirements, and health; make required compatibility changes; prove behavior; and land when supported.
- Preserve an established prerelease, nightly, or pinned-channel policy. Do not introduce a prerelease channel into a stable repository merely because it is newer, and honor explicit repository stabilization or compatibility constraints.
- Prefer repairing and landing existing contributor or dependency-bot PRs with credit intact. Combine related updates only when one coherent candidate materially improves compatibility or proof.
- Run repository-native tests, built/live proof appropriate to the changed boundary, dependency/security audit, AutoReview, exact-head CI, and the Public Model Identifier Gate when applicable. Fix failures autonomously and continue through merge and clean synchronized `main`.
- Escalate only a remaining non-dependency exception: destructive unique-work handling, unavailable required credential/live target, release/version/tag/publish authority, or a material product/security/privacy/irreversible choice with no safe reversible default. Dependency age, major-version status, migration effort, or a failing first attempt are not owner decisions.

## Authorization

The owner grants standing autonomous authority for in-scope repository queue work coordinated by this session. Project Codex app threads may synchronize clean checkouts; edit; create branches; commit; push; open or update PRs; write proof/review/close comments; approve, rerun, and repair CI; merge supported exact-head green changes; close resolved or invalid items; and return to synchronized clean `main`. Do not request per-item permission to implement, repair, improve, rewrite, publish a PR, fix CI, or land clearly supported work.

This standing authority explicitly includes dependency PRs and proactive dependency updates, including compatible major-version migrations and related code/test/documentation repairs. Default to the latest stable compatible versions and do not route dependency adoption or landing through the owner-decision queue.

This standing authority does not include:

- releases, version bumps, tags, registry publishing, or GitHub Releases;
- destructive handling of unique local work or user data;
- material product, security, privacy, legal, credential-sharing, or irreversible choices that lack a safe reversible default;
- external-system mutations beyond the repository/GitHub workflow unless separately authorized.

Clearly qualifying noise retains standing silent-close authority. A newer owner instruction may narrow any project. Record standing authority and exceptions in every project prompt; stop only at the exact remaining exception or hard blocker.

## Credential Access

Assume most maintainer credentials are stored in 1Password. Before reporting a credential blocker:

1. Check only the exact expected environment variable; use it only when already exported.
2. Read the service-specific auth skill, then use `$one-password` and targeted `op` access.
3. Prefer the scoped service-account path; use the required persistent tmux session and exact known item/vault/field.
4. Never broadly enumerate secrets or print values. Use `op run` or `op inject` when supported.
5. Ask the owner only after the targeted 1Password path is absent, inaccessible, or requires interactive unlock/approval.

Keep credential discovery and use inside the worker that needs the secret. Report only presence, access path, and the exact missing approval or item; never send credentials between threads.

## Codex App Worker Contract

Every delegated implementation Codex app thread, under standing authority and any newer project-specific limits, must:

- read the full issue/PR discussion, repo instructions, docs, and relevant code;
- when an issue has no PR, create one after implementing the best bounded candidate;
- reproduce or establish root cause before accepting an existing patch;
- rewrite when a cleaner bounded design is available;
- add regression coverage when appropriate;
- run focused and full tests, then live/end-to-end proof against the real affected boundary before landing;
- run `autoreview` until no accepted/actionable findings remain;
- commit and push the final candidate, then open or update its PR;
- rerun required checks and repair failures until exact-head CI is green;
- remain active through CI/review/deployment waits using bounded sleep/poll cycles; never stop at a nonterminal waiting status;
- merge or close the queue item with exact proof when evidence supports it;
- after landing, return to updated, clean `main`;
- update the changelog for user-visible changes; within the active unreleased/release section, order entries from most to least interesting to users and keep the repository's established format;
- after the assigned queue work, audit dependency freshness and report actionable updates even when none are taken;
- report every candidate and completed change with full clickable URLs, files changed, insertions, deletions, low/medium/high risk with rationale, proof state, and recommendation;
- ask repository-specific questions only in this worker thread.

Prefer repairing the contributor PR. Preserve contributor credit and follow the workspace PR rules.
If a newer project-specific instruction narrows standing authority, stop at that boundary after completing every still-authorized step and state the exact remaining action.

## Live Proof Gate

Live proof is a pre-land requirement, not optional polish.

- Test the exact final candidate commit through the changed user path using the real built/installed artifact and real service, account, device, OS, or external provider as applicable.
- For external integrations, authenticated live calls are required. Docs, mocks, fixtures, protocol captures, route-existence checks, and CI supplement live proof; they do not replace it.
- Redact secrets and private user data while retaining concrete evidence such as command, behavior, response class, artifact hash, or observed state transition.
- If credentials, account state, hardware, platform access, or a safe live target are unavailable, finish all autonomous code, tests, review, and CI work, then stop before merge/close. Ask for the exact access, an explicit item-specific waiver, or a reject/close decision.
- Before escalating a browser, desktop UI, or interactive automation blocker, try Peekaboo and any relevant configured mcporter-backed MCP route that can exercise the exact boundary. Verify their permissions and capabilities first; never claim GUI observation or an unrelated browser as equivalent when the contract requires a specific authenticated API, profile, device, or service mutation.
- Never infer a live-proof waiver from merge permission, release permission, prior contributor evidence, or confidence in mocks.
- Re-run live proof after any fix that changes the relevant runtime path.
- Pure docs, metadata, CI, or test-only changes with no runtime boundary may use the closest built-artifact or workflow proof; state why no external live boundary applies.

Record live evidence or the owner's explicit waiver in the landing proof comment.

## Public Model Identifier Gate

Before any push, public PR update, merge, or release involving model-bearing code or artifacts:

- Audit the exact candidate diff, tests, fixtures, snapshots, generated metadata, workflows, CI/test logs, packaged artifacts, and public PR/issue proof for model identifiers.
- Public artifacts may retain only identifiers currently documented or offered in an official public provider source. Record the source URL in the worker's audit report.
- Never expose internal, employee-only, preview-only, alias-only, inferred, synthetic provider-shaped, or otherwise undisclosed identifiers. Genericize questionable test and fixture values because assertion failures can print them in CI logs.
- Do not repeat a questionable identifier in worker messages, audit reports, public comments, or the orchestrator log. Describe it generically.
- Binary/archive scans must classify candidate strings as verified public identifiers, unrelated false positives, or blocking unknowns without echoing blocking unknowns.
- Return an explicit `PASS` or `BLOCKED` report covering every audited surface. Any new candidate diff, generated artifact, log/proof text, or model-bearing change invalidates the pass and requires re-audit.

No push, public mutation, merge, or release may proceed while this gate is blocked.

## Release Proposals

Propose a release when either all effective repository tasks are complete or a meaningful user-visible batch has accumulated. Judge meaningfulness by user impact and coherence, not a fixed item count. Do not wait for a perfectly empty queue when a coherent release is already valuable; unrelated backlog does not block a release.

Every proposal must include:

- recommended version and SemVer rationale;
- `Highlights`: two to five most valuable user outcomes, strongest first;
- full ordered changelog, most to least interesting to users, with full issue/PR URLs;
- dependency-freshness result and any update deliberately deferred;
- exact-head CI, tests, live proof, artifacts, and release-gate state;
- remaining backlog, actual release-specific blockers, residual risk, and one exact release/hold choice.

Match repository changelog style. For a meaningful release, add or maintain a `Highlights` subsection in the target changelog section when compatible; otherwise lead the target section with the highlight bullets before the full ordered entries. Do not reorder historical released sections. A proposal never authorizes version bumps, tags, publishing, GitHub Releases, or pushes.

## Release Gate

Open issues and PRs are backlog inventory, not release blockers by default. Compute only the candidate-specific blocker set immediately before release:

```text
release blockers = items explicitly scoped to the target release
                 + active authorized work promised for the target release
                 + demonstrated regressions affecting the release candidate
```

Do not ask the owner to exempt unrelated open issues or PRs. An item blocks only when repository metadata, an owner instruction, the release plan, or concrete validation ties it to the target release. Security exposure, data loss, broken install/upgrade, and candidate regressions block when they affect the candidate even without a milestone or label.

Release only when all are true:

- the owner has explicitly requested this release or authorized release execution for the repository;
- the release-specific blocker count is zero;
- required CI is green for the exact commit and branch/tag candidate being released;
- all user-facing runtime changes in the release have required live proof, unless the owner explicitly waives that proof for the release;
- release checkout is clean, on the expected branch, and fast-forward current;
- unreleased changes justify a release and the target version follows SemVer/project convention.

Recheck release-specific blockers, the candidate diff, and CI immediately before tagging or publishing. Abort if any gate changes.

In release reporting, list actual release blockers reviewed and their resolution. Do not enumerate or request waivers for unrelated backlog.

## Release Execution

Use the repository's release docs and matching skill:

- npm packages: use `npm`;
- macOS apps: use `release-mac-app`;
- other projects: use established repo scripts/workflows.

Before release:

- reconcile changelog history with existing tags/releases;
- ensure the target changelog section starts with the strongest user-facing highlights and orders remaining entries from most to least interesting;
- default to patch for compatible fixes, maintenance, refactors, docs, CI, and small behavior improvements;
- select minor only for substantial additive functionality, a meaningful new feature set, or a new backward-compatible public API;
- never use minor merely because several fixes accumulated; major requires explicit approval;
- run full release checks and review release-only edits.

After publishing, verify the actual release:

- Git tag and GitHub Release exist;
- release notes contain the complete changelog section;
- expected artifacts/install path work;
- npm packages show version, dist-tag, tarball, integrity, and publish time;
- release body links registry/artifact/integrity and CI proof when applicable.

Then open the next patch `Unreleased` section. Commit and push the closeout only when those mutations are authorized; otherwise leave the verified local closeout ready and report the exact permission needed. After an authorized push, pull `--ff-only` and finish on clean `main`.

## Reporting

Keep one compact cross-repo ledger:

- `Active`: repo, item URL, worker, current phase.
- `Intervened`: exact risk and instruction sent.
- `Needs owner`: exact decision/access required; no vague "needs review".
- `Ignored`: exact item and owner-granted exception.
- `Vision`: durable product rule proposed or updated, with source item URL.
- `Dependencies`: actionable updates or explicit current/no-update result.
- `Release proposed`: version, highlights, ordered changelog, gates, risk, and exact release/hold choice.
- `Released`: version, tag/registry verification, closeout commit.
- `Ready next`: release-specific blockers clear, CI green, recommended patch/minor version and rationale.

For each active, decision-ready, or landed code change, include `files / +insertions / -deletions` and a low/medium/high risk estimate with one-line rationale. Summaries must be self-contained; never assume the owner opened the linked issue, PR, or worker thread.

Omit archived and owner-suppressed repositories entirely. Do not list them as ignored, blocked, stale, or available work.

Whenever mentioning an issue or PR in any owner report, decision question, worker message, or status update, print its full canonical clickable URL. Never use only a repository-local number such as `#123`; include `https://github.com/OWNER/REPO/issues/123` or `https://github.com/OWNER/REPO/pull/123`.

For `Needs owner`, use the Owner Decision Brief format. Never emit a bare URL plus `land/delete`.

Report meaningful changes, not routine polling. Maintain a heartbeat automation when the user asks to keep monitoring.
