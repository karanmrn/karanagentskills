# Preparing the target repo (full detail)

The engine worktrees **`Path.cwd()`** (`run_phase.py` exposes no `--repo-dir`), so
the implementer commits into a worktree of whatever repo is the current directory
of the phase job. You therefore launch every phase job **from a clone of the
issue's repo** (`$TGT`), while importing scripts + configs from the installed
skill (`$SKILL_DIR`).

1. **Inspect and record issue/fix metadata.** Prefer a recent issue with a known
   fixing PR/commit. Record the issue creation date, fixing PR URL, fix commit,
   and pre-fix base commit in `run_state.json`:
   ```bash
   gh issue view <n> --repo <owner>/<repo> --json createdAt,title,url
   gh pr view <pr> --repo <owner>/<repo> --json url,mergeCommit
   ```
2. **Clone at the pre-fix base.** base = first parent of the fixing PR's merge:
   ```bash
   gh api repos/<owner>/<repo>/commits/<merge_sha> -q '.parents[0].sha'
   git clone https://github.com/<owner>/<repo>.git "$TGT"
   git -C "$TGT" checkout <base_sha>
   ```
3. **Enable worktree config on the clone (REQUIRED — else every implement job dies
   instantly)** with `git config --worktree core.hooksPath` failing:
   ```bash
   git -C "$TGT" config extensions.worktreeConfig true
   ```
   Fresh clones never have this on.
4. **Launch jobs with cwd = the clone, scripts from the skill, artifacts in the
   chosen run dir** — absolute paths everywhere. Pattern for every phase job:
   ```bash
   cd "$TGT" && uv run "$SKILL_DIR/scripts/run_phase.py" \
     --run-dir "$RUNS/$TS" --out-dir "$RUNS/$TS/..." --issue '<issue url>' ...
   ```
   Configs default to the skill's bundled `config/*.yaml`; pass
   `--models-config/--conditions-config` only when running a per-run customized
   copy.
5. The `--issue` is the issue's URL; planner/implementer use `gh` against the
   clone's origin to read it. `local_commit` mode blocks push and strips upstream.

Verified working on `pallets/flask#4041` (base `d8c37f43`).

## Failure signature

All implement jobs erroring instantly with

```
git config --worktree ... fatal: --worktree cannot be used with multiple
working trees unless extensions.worktreeConfig is enabled
```

means step 3 was skipped. Fix the clone, delete each failed unit's `result.json`
and `worktree/` dir, run `git -C "$TGT" worktree prune`, and relaunch implement.
