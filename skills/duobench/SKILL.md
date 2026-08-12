---
name: duobench
description: >-
  Benchmark planner×implementer LLM pairings on a real GitHub issue and chart
  quality-per-dollar. Use when the user says things like "benchmark <models> on
  duobench", "run a duobench eval", "add <planner>/<implementer> to the eval",
  "produce plots about the duobench results", or "re-plot the last duobench run".
  You orchestrate plan→implement→judge phase jobs in tmux, aggregate results.json,
  then write seaborn plots from results.json/trial.json.
---

# duobench

duobench measures which **planner LLM × implementer LLM** duo produces the best
**quality-per-dollar** on a real GitHub issue. A planner writes a handoff plan; an
implementer makes ONE local commit fixing the issue (no push, no PR); a panel of
judge LLMs scores each commit on 4 dimensions; cost comes from token usage.

You are the orchestrator. There is no monolithic CLI. You launch thin phase jobs
(one Pi RPC instance each) across tmux sessions, gate each phase on completion,
aggregate, and plot.

**Path model.** This skill is installed standalone (e.g. via `npx skills add`) and
is fully self-contained:

```bash
SKILL_DIR=<absolute path to the directory containing this SKILL.md>
```

Everything you launch lives under it: `$SKILL_DIR/scripts/` (phase runner,
aggregator, plotters — each carries PEP 723 inline deps, so `uv run <script>`
works with no project setup), `$SKILL_DIR/src/duobench/` (engine),
`$SKILL_DIR/config/` (model registry + judges), `$SKILL_DIR/prompts/`. The
engine resolves prompts/configs relative to the skill dir, never the cwd.

The **cwd of a phase job is the repo being benchmarked** (the engine worktrees
`Path.cwd()`). That is usually NOT the directory the user is sitting in — see §1.5.

**Be pedagogical.** The user may be running this for the first time. Before each
phase, explain in one or two sentences what it does, why it comes now, and what
artifact it will produce. Surface costs, defaults, and where things are written
*before* spending, not after.

## §0 Operating contract (read first)

- **Strict order:** plan → implement → judge → aggregate → plot. Never start a
  phase until **every** job of the previous phase has written its `result.json`.
- **One tmux job = one Pi instance = one unit of work.** Money phases (plan,
  implement, judge) run in tmux. Short pure steps (aggregate, plotting) run with
  a plain background `Bash`.
- **Never push or open PRs.** Always pass `--submission-mode local_commit` (the
  default). The engine installs git/gh safety wrappers outside the solution
  worktree; do not fight them.
- **Announce the output directory up front.** Default `./duobench-runs/<TS>`
  (relative to where the user invoked you); state it at the start of the
  conversation and invite the user to change it. `RUNS=<chosen dir>` below.
- **Confirm before spending.** Show the issue, the resolved condition list, the
  judge panel, trials, the output directory, and the estimated job count. Wait
  for a go-ahead.
- **Default to `--trials 1`.**
- **`$RUNS/<TS>/run_state.json` is the source of truth**, not your memory. After
  any uncertainty or context loss, reconstruct state from disk + `tmux ls` —
  never guess which jobs ran.

## §0.5 Setup & preflight (run before the first benchmark)

Check the toolchain; offer to install anything missing and explain what each
piece is for:

```bash
command -v uv tmux git gh jq        # uv runs the scripts; tmux hosts phase jobs
command -v pi && pi --version       # Pi: the RPC harness that drives each model
gh auth status                      # planner/implementer read the issue via gh
```

- Missing `uv` → `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Missing `tmux` → `brew install tmux` (macOS) / distro package manager
- Missing `pi` → point the user at Pi's install docs; you cannot benchmark without it.

**Verify the requested models are actually available in Pi** before launching
money jobs: every model key must resolve in `$SKILL_DIR/config/models.yaml`, and
its `provider/model_id` must be registered + authenticated in the user's Pi
install. The engine fails fast with a clear message when Pi rejects `set_model`,
but it's cheaper to catch this in preflight — check Pi's configured providers
(its models/auth listing) and tell the user which providers still need auth
before any spend. Also tell the user which models the bundled registry knows
out of the box.

## §1 Elicit the issue + models

- If the user named models but no issue, **ask for the GitHub issue URL** (accept
  `owner/repo#123` or a full URL). Real runs cannot proceed without it.
- **If the user asks you to pick an issue**, choose one that is: from a public
  repo, **recent** (ideally opened within the last few weeks), **single-commit-
  fixable**, self-contained, medium-hard, and — crucially — has a **known fixing
  PR/commit** so you can check out the pre-fix base (§1.5). Pure-Python repos
  (Flask, requests, marshmallow…) judge cleanly. Avoid sprawling features (hard
  to score on one commit). Confirm the pick before spending. A recent issue
  reduces pretraining-contamination risk; it does not eliminate it because agents
  still inspect public runtime evidence such as issues, comments, and linked PRs.
- Resolve model names to registry keys in `$SKILL_DIR/config/models.yaml`:
  `opus → claude-opus-4.8`, `kimi → kimi-k2.6`, `gpt → gpt-5.5`. If a name is not
  in the registry, warn that it's passed to Pi as a raw `provider/model_id` spec
  with no pricing (`cost_source` becomes `unknown`, so quality-per-dollar is
  unreliable) and confirm. To change pricing/judges, copy the bundled config into
  the run dir, edit the copy, and pass `--models-config <copy>` to every job of
  that run — don't edit the installed skill in place.
- Confirm the **judge panel**. Default to the `judges:` list in the registry.
  Offer to add the competing models as judges — multiple judges are averaged per
  build (aggregate auto-discovers every `results/judge-*.json`), and having each
  competitor judge its rivals is what makes the **self-bias chart** meaningful.
  Keep the judge panel/config **identical across runs** you intend to compare, so
  quality is measured by the same instrument.

## §1.5 Prepare the target repo (where the phase jobs run)

The engine worktrees **`Path.cwd()`**, so every phase job must be launched with
cwd = a checkout of the issue's repo. Even when the issue belongs to the repo
the user is sitting in, prefer a **dedicated clone at the pre-fix base commit**
— it keeps benchmark worktrees out of their working copy and pins exactly what
the models see. Short version (`TGT=<absolute target clone path>`):

```bash
gh api repos/<owner>/<repo>/commits/<fix_merge_sha> -q '.parents[0].sha'   # pre-fix base
git clone https://github.com/<owner>/<repo>.git "$TGT"
git -C "$TGT" checkout <base_sha>
git -C "$TGT" config extensions.worktreeConfig true   # REQUIRED — implement jobs die without it
```

Full detail (issue/fix metadata capture, failure signatures, the verified
flask#4041 walkthrough): read **`references/external-repo.md`** in this skill.

## §2 Expand the planner×implementer matrix

- A square ask ("benchmark opus and kimi") means both models are planners AND
  implementers → N×N conditions. opus,kimi → 4 conditions.
- **Condition id = `<planner>-solo` if planner==implementer, else
  `<planner>-x-<implementer>`**, each part passed through the safe-name rule
  (alnum + `-_.` kept, everything else → `-`). These ids are the directory names
  and the join key everywhere — compute them exactly. You can confirm them with:

  ```bash
  uv run python -c "import sys; sys.path.insert(0, '$SKILL_DIR/src'); from duobench.engine import condition_id_for as c; print(c('claude-opus-4.8','kimi-k2.6'))"
  ```

- **Unique planners** (one plan job each) = the deduped planner column.

Example (opus + kimi): conditions `claude-opus-4.8-solo`, `kimi-k2.6-solo`,
`claude-opus-4.8-x-kimi-k2.6`, `kimi-k2.6-x-claude-opus-4.8`; unique planners
`claude-opus-4.8`, `kimi-k2.6`.

## §3 Create the run dir + state

```bash
TS=$(date -u +%Y-%m-%dT%H-%M-%S)
mkdir -p "$RUNS/$TS"
```

Write `$RUNS/$TS/run_state.json` **before launching anything**:

```json
{
  "run_ts": "<TS>", "issue": "<url>", "submission_mode": "local_commit",
  "issue_created_at": "<ISO timestamp if known>",
  "issue_selected_at": "<ISO timestamp when picked>",
  "target_repo": "<owner/repo>",
  "target_repo_dir": "<absolute target clone path>",
  "base_commit_sha": "<pre-fix base commit if known>",
  "fix_commit_sha": "<known merged fixing commit if known>",
  "fix_pr_url": "<known fixing PR URL if known>",
  "trials": 1, "concurrency_cap": 2, "phase": "plan",
  "judges": ["kimi-k2.6", "gpt-5.5"],
  "unique_planners": ["claude-opus-4.8", "kimi-k2.6"],
  "conditions": [
    {"id": "claude-opus-4.8-solo", "planner": "claude-opus-4.8", "implementer": "claude-opus-4.8"},
    {"id": "kimi-k2.6-x-claude-opus-4.8", "planner": "kimi-k2.6", "implementer": "claude-opus-4.8"}
  ],
  "jobs": {}
}
```

Update `phase` and the per-unit `jobs` map (`{session, out_dir, result_path, status}`)
as you go, so a fresh agent can resume.

## §4 Phase ordering & gates

For each phase: launch all its jobs (respecting the concurrency cap), then **block
until every expected `result.json` exists** before the next phase.

1. **Plan** — one job per unique planner × trial →
   `$RUNS/$TS/shared-plans/<planner-safe>/trial-<n>/`.
2. **Implement** — one job per condition × trial →
   `$RUNS/$TS/conditions/<cond_id>/trial-<n>/`. Each `--plan-path` points at its
   planner's `plan.md`.
3. **Judge** — only after all impls are terminal: one job per condition × judge ×
   trial, writing `results/judge-<judge>.json` into the trial dir.
4. **Aggregate** — `uv run "$SKILL_DIR/scripts/aggregate.py" "$RUNS/$TS"`.
5. **Plot** — `uv run "$SKILL_DIR/scripts/plots_example.py" "$RUNS/$TS"` (see §7).

## §6 tmux recipe

Session name: `duobench__<TS>__<phase>__<unit>` (plan: `<planner>__t<n>`;
implement: `<cond>__t<n>`; judge: `<cond>__<judge>__t<n>`).

Every job: **cwd = the target clone (`$TGT`), script + configs from `$SKILL_DIR`,
artifacts into `$RUNS/$TS`** — use absolute paths for all three.

**Launch a plan job:**
```bash
JOB="duobench__${TS}__plan__claude-opus-4.8__t0"
OUT="$RUNS/$TS/shared-plans/claude-opus-4.8/trial-0"
mkdir -p "$OUT"
tmux new-session -d -s "$JOB" \
  "cd $TGT && PYTHONUNBUFFERED=1 uv run $SKILL_DIR/scripts/run_phase.py \
     --phase plan --run-dir $RUNS/$TS --out-dir $OUT \
     --issue '$ISSUE' --planner claude-opus-4.8 --trial 0 \
     > $OUT/job.log 2>&1; echo __DUOBENCH_EXIT=\$? >> $OUT/job.log"
```

**Launch an implement job** (`--plan-path` = that planner's plan.md):
```bash
COND="kimi-k2.6-x-claude-opus-4.8"; OUT="$RUNS/$TS/conditions/$COND/trial-0"
mkdir -p "$OUT"
tmux new-session -d -s "duobench__${TS}__implement__${COND}__t0" \
  "cd $TGT && PYTHONUNBUFFERED=1 uv run $SKILL_DIR/scripts/run_phase.py \
     --phase implement --run-dir $RUNS/$TS --out-dir $OUT --condition $COND \
     --issue '$ISSUE' --planner kimi-k2.6 --implementer claude-opus-4.8 \
     --plan-path $RUNS/$TS/shared-plans/kimi-k2.6/trial-0/plan.md --trial 0 \
     --submission-mode local_commit \
     > $OUT/job.log 2>&1; echo __DUOBENCH_EXIT=\$? >> $OUT/job.log"
```

**Launch a judge job** (`--build-dir` = the trial's worktree; `--commit-sha` from
the implement job's `result.json` `artifact.commit_sha`):
```bash
OUT="$RUNS/$TS/conditions/$COND/trial-0"
tmux new-session -d -s "duobench__${TS}__judge__${COND}__gpt-5.5__t0" \
  "cd $TGT && PYTHONUNBUFFERED=1 uv run $SKILL_DIR/scripts/run_phase.py \
     --phase judge --run-dir $RUNS/$TS --out-dir $OUT \
     --condition $COND --issue '$ISSUE' --judge-key gpt-5.5 \
     --build-dir $OUT/worktree --commit-sha $SHA --trial 0 \
     > $OUT/job.log 2>&1; echo __DUOBENCH_EXIT=\$? >> $OUT/job.log"
```

(If you customized the registry for this run, add
`--models-config <copy> --conditions-config <copy>` to every call.)

**Concurrency cap:** default **2** money-jobs at once. Launch up to the cap, then
wait for a free slot. If the user says "run them all in parallel", lift the cap
and warn about cost/rate-limits.

**tmux gotchas (learned the hard way):**
- tmux rewrites `.` → `_` in session names (`claude-opus-4.8` shows as
  `claude-opus-4_8`). **Gate on `result.json`, not session names.** If you must
  grep `tmux ls`, match `"$TS"` then the phase substring — don't assume dots.
- If you write a cap-loop helper in bash, target **macOS bash 3.2**: no `mapfile`
  (use `arr=(); for d in dir/*/; do arr+=("$(basename "$d")"); done`).

**Completion detection / phase gate:** the job's last action is an atomic write of
its `result.json`. Poll roughly every 10s:
- if the expected `result.json` exists → job done; read `.status`.
- if it's missing AND `tmux has-session -t <JOB>` reports the session is gone →
  hard crash; read the tail of `job.log`.
Only advance to the next phase when every expected `result.json` is present.

**Let the user watch:** `tmux attach -t <JOB>` (detach with **Ctrl-b then d**),
`tmux ls` to list duobench jobs, `tail -f <out>/job.log`.

**After the run, point the human at the actual fixes.** In the final response,
list each condition's worktree and commit SHA so the user can inspect the real
patches, for example:

```bash
jq -r '.conditions | to_entries[] | "\(.key)"' "$RUNS/$TS/results.json"
jq -r '.meta | [.commit_sha, .build_dir] | @tsv' "$RUNS/$TS/conditions/<cond>/trial-0/trial.json"
git -C "$RUNS/$TS/conditions/<cond>/trial-0/worktree" show --stat --oneline HEAD
```

The plots are a decision aid; human inspection of the candidate patches is the
last step before trusting a model pairing on a real project.

## §7 Plotting

```bash
uv run "$SKILL_DIR/scripts/plots_example.py" "$RUNS/$TS"   # run in place — no copy needed
```

This writes `$RUNS/$TS/results/*.png` (+ `.csv`), all styled consistently:
**leaderboard**, **cost-vs-quality** (iso-efficiency guide lines + legend),
**dimensions**, **self-bias** (own-vs-other judge bars), **cost-breakdown**.
Show the user the resulting PNGs. For customization ("correctness vs cost only",
"facet by planner", "only opus conditions") read **`references/plotting.md`**
in this skill.

## §5 Resume / add a condition to an existing run

Trigger: "add <planner>/<implementer> to the eval".
1. Find the target run dir (most recent under `$RUNS/`, or the one named). Read
   its `run_state.json` and `results.json`.
2. Compute the **new** condition id(s) and set-difference against existing
   `conditions/*` dirs. e.g. "add gpt planner and kimi implementer" →
   `gpt-5.5-x-kimi-k2.6`.
3. **Plan reuse:** if `shared-plans/<new-planner>/trial-<n>/plan.md` exists, reuse
   it (run no plan job). Before reusing, sanity-check the planner spec recorded in
   that dir's `shared-plan.json` matches the requested model. If absent, run one
   plan job for the new planner.
4. Run the new condition's implement + judge jobs (same tmux recipe, same target
   clone from `run_state.json`'s `target_repo_dir`).
5. Re-aggregate the whole run dir (`aggregate.py` rescans all trials, merging old
   + new) and re-plot. The new condition appears in every chart with its stable
   per-model color.

## Failure & partial runs

- **All implement jobs error instantly** with `git config --worktree ... fatal:
  --worktree cannot be used with multiple working trees unless extensions.
  worktreeConfig is enabled` → the clone lacks worktree config. Fix:
  `git -C <clone> config extensions.worktreeConfig true`, then delete the failed
  `result.json` + `worktree/` dirs, `git -C <clone> worktree prune`, and relaunch
  implement. (See §1.5.)
- **Plan job fails** → block the implement jobs that depend on that plan; run the
  others; offer to retry just that plan job.
- **Implement `timeout`/`stalled`/`stopped`** → a valid data point (flows to
  `impl_status` → leaderboard). Still judge it; annotate non-complete conditions
  when you report.
- **Judge error** → aggregation drops error judges from the mean; proceed on a
  partial panel. If ALL judges errored for a build, report no score and offer to
  re-run those judge jobs.
- **Idempotency** → before launching a unit, skip it if its out_dir already has a
  `result.json` with `status:"complete"` (this is how resume reuses work). For an
  explicit retry, delete that unit's `result.json` (and its `worktree/`, plus
  `git worktree prune`) and relaunch only that session.

## Guardrails

- Always confirm the **job estimate** before launching:
  `unique_planners + len(conditions) + len(conditions)×len(judges)`, all × trials.
  (opus+kimi, 2 judges, 1 trial = 2 + 4 + 8 = 14 model-calling jobs.)
- Default 1 trial. Note that trials multiply every count above.
- Local-commit only; never push/PR. Judges run read-only.
- Report `cost_source` per condition; warn loudly when any model is off-registry
  (its dollar figure and efficiency are unreliable).
- **Cost accuracy / cache pricing (important for $/quality).** Only models whose
  provider returns billed cost show `cost_source: pi_reported`; the rest are
  `configured` (computed from the registry's rates). An agentic implement loop is
  ~90% **cache-read** tokens, and if a `configured` model has no `cache_read`
  rate, `cost.py` charges cache hits at the **full input price** — inflating cost
  several-fold (Kimi looked ~4× too expensive until we set `cache_read: 0.16`).
  So: every `configured` model in the registry should have a `cache_read` (and,
  if known, `cache_write`) rate. If you can't get a real rate, say so — don't
  compare a `pi_reported` model against a `configured`-at-full-cache model and
  call it fair. (Already set: `kimi-k2.6 cache_read: 0.16`. `gpt-5.5` unset.)
  With rates in place, cost is correct at run time and no post-hoc recompute is
  needed.

## §8 Many issues / trials

A single issue is an anecdote. When the user asks to "make it scientific", "run
on multiple issues", or "average over runs", read **`references/scaling.md`** in
this skill — it is opt-in and expensive; never default to it.
