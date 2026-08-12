# Saga directory & spec templates

A saga is a *tree* of spec files plus a progress log, stored in its own directory outside the repo so it survives across orchestrator sessions and can be resumed. Each level carries its own validation criteria. Vagueness here becomes defects later — prefer concrete, checkable language over aspirational prose.

## Directory layout

```
~/.sagas/<saga-name>/
├── SAGA.md                      # overview, environment, saga-level exit criteria, milestone index
├── PROGRESS.md                  # live, continuously-updated execution log and current state
└── milestones/
    ├── 01-<slug>/
    │   ├── MILESTONE.md          # milestone spec + milestone-level validation criteria
    │   └── tasks/
    │       ├── 01-<slug>.md      # task spec + task-level validation criteria
    │       └── 02-<slug>.md
    └── 02-<slug>/
        ├── MILESTONE.md
        └── tasks/ ...
```

- `<saga-name>` must be **unique and stable** — a feature slug plus a timestamp, e.g. `dark-mode-20260609-0028`. It is how a fresh orchestrator finds and resumes the saga.
- Number milestone/task directories and files (`01-`, `02-`, …) so order is obvious and dependency references are stable. Refer to tasks as `M<milestone>.<task>` (e.g. `1.2`).
- Keep `SAGA.md` small; push detail down into `MILESTONE.md` and task specs so the orchestrator reads only what the current step needs.

## `SAGA.md`

```markdown
# Saga: <feature name>
- Saga directory: ~/.sagas/<saga-name>
- Repo: <path> @ <base branch>
- Status: planning | in-progress | final-validation | complete

## Problem statement
<1–2 paragraphs: what we are building and why. The user-facing outcome.>

## Scope & non-goals
- In scope: <bullets>
- Out of scope / non-goals: <bullets — explicit, so workers don't gold-plate>
- Decisions delegated to agent discretion: <only those the user explicitly allowed; otherwise "none">

## Environment & capabilities
- Program type: <web app | native GUI | TUI | CLI/library | backend service | ...>
- Run/launch command: <how to start it for manual/interactive verification>
- Test command(s): <unit / integration runner commands, confirmed working>
- Build / lint / typecheck command(s): <commands>
- Computer use available: <yes (local) | yes (remote only) | no>
- Default validation method for this saga: <derived from the above; see validation-strategies.md>

## Saga exit criteria
<Concrete, checkable conditions that mean the entire feature is done and correct.
Each is verifiable, not a feeling. Validated in Phase 3.>
1. <criterion>
2. <criterion>

## Milestone index
<Ordered list with one line each + dependency notes. The detail lives in each MILESTONE.md.>
1. 01-<slug> — <one line>; depends on: none
2. 02-<slug> — <one line>; depends on: 01-<slug>
```

## `MILESTONE.md`

```markdown
# Milestone <n>: <name>
- Saga: <saga-name>
- Depends on: <milestone ids, or "none">

## Goal
<What this milestone delivers and why it sits here in the order.>

## Milestone validation criteria
<Checkable conditions that mean the whole milestone is done and integrates correctly.
Run these after integrating the milestone's tasks.>
1. <criterion>
2. <criterion>

## Tasks
<Index of this milestone's task specs + intra-milestone dependencies.>
- 01-<slug> — <one line>; depends on: none
- 02-<slug> — <one line>; depends on: 01-<slug>
```

## Task spec (`tasks/NN-<slug>.md`)

```markdown
# Task <m>.<n>: <name>
- Milestone: <m>
- Depends on: <task ids, or "none">

## Scope
<What this single worker does; small enough for one focused effort.>

## Owned files/surfaces
<Paths/modules this task may touch. Two parallel tasks must not own the same files.>

## Interfaces produced/consumed
<Exact API, schema, or function signatures other tasks rely on, if any.>

## Validation method
<computer use | interactive CLI | unit tests | integration tests | combination>

## Validation criteria (the contract)
<Explicit, checkable. Satisfying all of these should leave little-to-no possibility
the task was done incorrectly. Cover unhappy paths and "must not change" cases.>
1. <criterion>
2. <criterion>

## Evidence required
<What the worker must return to prove completion: named test output, screenshots,
CLI transcript, sample command output, etc.>
```

## `PROGRESS.md`

The source of truth for execution state. Keep it current as work happens — a fresh orchestrator resumes entirely from this file plus the specs.

```markdown
# Saga progress: <feature name>
- Saga directory: ~/.sagas/<saga-name>
- Repo: <path> @ <base branch>
- Phase: 2 (implementation) | 3 (final validation)
- Current milestone: <n>

## Task status
<One line per task: status, branch, evidence pointer.
Branch naming convention: saga/<saga-name>/m<M>t<T>-<task-slug> (prepend a team/user branch prefix if your repo requires one)>
- 1.1 <name>: done — branch saga/<saga-name>/m1t1-<slug>, commit <hash>, evidence: <pointer / test names / screenshot path>
- 1.2 <name>: in progress — worker <name>, worker_run_id <agent/run id>, branch saga/<saga-name>/m1t2-<slug>, worktree ../saga-<saga-name>-m1t2
- 1.3 <name>: blocked — <reason / decision needed>
- 2.1 <name>: pending

## Integration notes
<Per milestone: merge order, conflicts resolved, milestone-level validation results.>

## Decisions & deviations
<Any spec changes made mid-flight and why; keep the specs themselves updated too.>

## Open questions for user
<Only if a blocker truly requires escalation.>

## Log
<Reverse-chronological short entries: timestamp — what happened.>
- 2026-06-09T00:40Z — Milestone 1 integrated; all milestone criteria pass.
```

## Rules

- **Saga exit criteria / milestone criteria / task criteria** form nested contracts. Each must be checkable by a concrete method; if you can't say how you'd verify one, it isn't a criterion yet.
- **Milestones** are ordered by dependency and independently meaningful. Tasks *within* a milestone should be as independent (parallelizable) as the feature allows.
- **Tasks** must be sized for a single worker in one focused effort. If a task needs multiple distinct deliverables or spans many unrelated files, split it.
- **Owned files/surfaces** prevent collisions between parallel workers.
- Keep `PROGRESS.md` and the specs in sync with reality; they are the only state a resuming orchestrator has.
