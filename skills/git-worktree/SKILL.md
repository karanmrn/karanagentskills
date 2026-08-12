---
name: git-worktree
description: Use git worktrees to run multiple coding agents in parallel on one repo without collisions. Use when starting a task in a shared repo, when the user says "worktree", "parallel agents", "one worktree per task", or when agents keep overwriting each other's changes. Covers creating worktrees, making them as complete as the main checkout (.env files, dependencies, databases, ports), merging back, and cleanup.
disable-model-invocation: true
---

# Git Worktrees for Parallel Agents

## Start here (before any task work)

Detect where you are:

```bash
[ "$(git rev-parse --path-format=absolute --git-dir)" = "$(git rev-parse --path-format=absolute --git-common-dir)" ] \
  && echo "primary checkout" || echo "worktree"
```

- **Primary checkout** → do NOT start editing here. Create a worktree named after the task, bootstrap it (see "Making the worktree complete"), `cd` into it, and do ALL task work there.
- **Worktree** (e.g. Cursor already started you in one) → proceed with the task.

## What a worktree is

One repo, multiple folders. `git worktree add` creates an extra checkout of the same repository in a separate directory, on its own branch. All worktrees share one `.git` history, but each has its own files. Two agents in two worktrees physically cannot overwrite each other's work.

## The working model

- **One task = one worktree = one agent session.** Never let two agents share a working directory.
- **The primary checkout is the integration point.** It stays on the main branch and is used only to review, merge, and push. It is not a scratchpad.
- **Nothing auto-merges.** The human reviews each worktree's diff, then merges it into main (or discards it), then deletes the worktree.
- **Worktree branches are local and short-lived.** Never push them unless the user explicitly asks. Only main gets pushed.
- Merge one worktree at a time. Rebase a stale worktree onto main before merging if main moved.

## Creating and removing

```bash
git worktree add ../myrepo-task-x          # new worktree + branch "myrepo-task-x"
git worktree add ../fix-y -b fix-y main    # explicit branch off main
git worktree list                          # see all worktrees
git worktree remove ../myrepo-task-x       # delete when merged/abandoned
git worktree prune                         # clean up stale registrations
```

Note: a branch can only be checked out in ONE worktree at a time (including main).

In Cursor: start agents in worktrees via the Agents Window, or `/worktree <task>` in a chat. `/apply-worktree` merges the result into your main checkout; `/delete-worktree` discards; `/best-of-n model1,model2 <task>` runs the same task in parallel worktrees, one per model. Cursor auto-deletes older worktrees (default cap 25 per machine), so merge or push results promptly.

## Making the worktree complete

A fresh worktree contains ONLY tracked files. Everything gitignored is missing. An agent dropped into a bare worktree will fail confusingly, so replicate:

1. **Env/secret files** — copy `.env`, `.env.local`, and similar from the primary checkout. Copy, never symlink (an agent editing a symlinked env file would corrupt the original).
2. **Dependencies** — run the install (`npm ci`, `pnpm install`, `uv sync`, `bundle install`). Never symlink `node_modules`; it breaks builds in both checkouts.
3. **Local databases and services** — decide per service:
   - Shared server (e.g. one Postgres container): pin the identity so worktrees don't spawn duplicates fighting over the same port. For Docker Compose, set a top-level `name:` in the compose file — otherwise the project name comes from the folder name and every worktree starts its own container on the same port.
   - Per-worktree state (e.g. SQLite files): copy or re-seed it.
4. **Ports** — dev servers, test servers, and debuggers bind fixed ports. Either run one at a time across all worktrees, or make the port configurable per worktree.
5. **Generated files and caches** — rebuild in the worktree (`npm run build`, codegen); build output is gitignored and won't be there.
6. **Git hooks** — `core.hooksPath` and `.git/config` are shared across worktrees automatically; verify hook scripts don't assume the primary checkout's path.

## Automate the setup

Codify the checklist so every worktree bootstraps itself. In Cursor, `.cursor/worktrees.json` runs on worktree creation (`$ROOT_WORKTREE_PATH` = the primary checkout):

```json
{
  "setup-worktree": [
    "npm ci",
    "cp $ROOT_WORKTREE_PATH/.env.local .env.local"
  ]
}
```

Without Cursor, keep a `scripts/setup-worktree.sh` in the repo and run it as the first command in any new worktree. Inside a worktree, the primary checkout's path is:

```bash
dirname "$(git rev-parse --path-format=absolute --git-common-dir)"
```

## Merging back

```bash
# from the primary checkout, after reviewing the worktree's diff:
git merge --no-ff task-branch     # or: git merge --squash task-branch
git worktree remove ../myrepo-task-x
git branch -d task-branch
```

Or in Cursor, simply `/apply-worktree` from the agent's chat, review, commit.

## Gotchas

- Gitignored files silently missing is the #1 failure — always bootstrap before the agent starts.
- Disk: each worktree duplicates the working files plus its own `node_modules`. Delete merged worktrees; don't hoard them.
- Long-lived worktrees rot. If a task stalls for days, rebase onto main or restart it.
- Uncommitted work in a deleted worktree is gone. Commit in the worktree early and often; the commits live in the shared repo even after the folder is removed.
- One shared stash list, one shared config, one shared refs namespace — worktrees isolate files, not git state.
