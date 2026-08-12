# E2E Triage CI

Triage E2E test failures with **re-run verification**. Analyzes artifacts and re-runs failing tests locally to distinguish flaky from real bugs. Produces a findings report with classifications -- does NOT apply fixes. Does deep analysis of the code.

---

## Step L1: Parse User Input

The user provides one or more of:
- **Test name(s)** -- e.g., `TestInteractiveMultiStep`
- **`--agent <agent>`** -- optional, defaults to all agents that previously failed
- **A local artifact path** -- skip straight to analysis of existing artifacts
- **CI run reference** -- triggers artifact download instead of local re-runs:
  - `latest CI run` / `latest` -- most recent failed E2E run on main
  - A GitHub Actions run ID (numeric, e.g., `12345678`)
  - A GitHub Actions run URL

**CI artifact download:** When a CI run reference is provided, download artifacts using:

```bash
scripts/download-e2e-artifacts.sh <latest | RUN_ID | RUN_URL>
```

The script outputs the absolute artifact path as its **last line of stdout** -- capture that and use it as the artifact path for analysis. After downloading, **skip Steps L2-L5** (local re-runs) and go straight to **Shared Analysis** (Step 1), since we're analyzing CI artifacts, not running tests locally.

**Cost warning:** Real E2E tests consume API tokens. Before running, confirm with the user unless they provided specific test names (implying intent to run).

## Step L2: First Run

```bash
mise run test:e2e --agent <agent> <TestName>
```

Capture the artifact directory from the `artifacts: <path>` output line.

## Step L3: Re-run on Failure

If the test **passes** on first run: report as passing, done for this test.

If the test **fails**: run a **second time** with the same parameters.

## Step L4: Tiebreaker (if needed)

If results are **split** (1 pass, 1 fail): run a **third time** as tiebreaker.

## Step L5: Collect Results

For each test+agent pair, record: `(test, agent, run_1_result, run_2_result, [run_3_result])`

Proceed to **Shared Analysis** (Step 1 below).

---

## Shared Analysis & Classification

### Step 1: Analyze Each Failure

For each failure, follow the **Debugging Workflow** in `.claude/skills/e2e/debug.md` (steps 2-5: console.log -> test source -> entire.log -> deep dive). Collect:
- What the agent actually did (from console.log)
- What was expected (from test source)
- CLI-level errors or anomalies (from entire.log)
- Repo/checkpoint state (from git-log.txt, git-tree.txt, checkpoint-metadata/)

### Step 2: Classify Each Failure

Use **re-run results as the primary signal**, supplemented by artifact analysis.

#### Re-run signals (strongest):

| Original | Re-run 1 | Re-run 2 | Classification |
|----------|----------|----------|----------------|
| FAIL | FAIL (same error) | FAIL (same error) | **real-bug** OR **flaky (test-bug)** -- see below |
| FAIL | PASS | PASS | **flaky** |
| FAIL | PASS | FAIL | **flaky** (non-deterministic) |
| FAIL | FAIL | PASS | **flaky** (non-deterministic) |
| FAIL | FAIL (different error) | FAIL (different error) | **needs deeper analysis** -- examine artifacts |

**Important: Consistent failures can still be `flaky` (test-bug).** When all re-runs fail, check *where* the root cause is:
- Root cause in `cmd/entire/cli/` -> **real-bug** (product code is broken)
- Root cause in `e2e/` (test infra, test helpers, tmux setup, env propagation) -> **flaky (test-bug)** -- the CLI works fine, the test is broken

#### Strong `real-bug` signals (root cause must be in `cmd/entire/cli/`, not `e2e/`):

- `entire.log` contains `"level":"ERROR"` or panic/stack traces from CLI code
- Checkpoint metadata structurally corrupt (malformed JSON, missing `checkpoint_id`/`strategy`)
- Session state file missing or malformed when expected
- Hooks did not fire at all (no `hook invoked` log entries)
- Shadow/metadata branch has wrong tree structure
- Same test fails across 3+ agents with same non-timeout symptom
- Error references CLI code (panic in `cmd/entire/cli/`)

**Key question:** Is the bug in `cmd/entire/cli/` (product code) or in `e2e/` (test code)? Only the former is a `real-bug`.

#### Strong `flaky` signals (unless overridden by real-bug):

**Agent behavior (non-deterministic):**
- `signal: killed` (timeout)
- `context deadline exceeded` or `WaitForCheckpoint.*exceeded deadline`
- Agent asked for confirmation instead of acting
- Agent created file at wrong path / wrong name
- Agent produced no output
- Agent committed when it shouldn't have (or vice versa)
- Duration near timeout limit

**Test-bug (consistent failure, but root cause is in `e2e/` not `cmd/entire/cli/`):**
- Agent "Not logged in" / auth errors -> test env setup doesn't propagate auth credentials
- Env vars not propagated to agent session -> tmux/test harness bug
- Error references test code (`e2e/`) not CLI code (`cmd/entire/cli/`)
- Test helper logic errors (wrong assertions, bad globs, incorrect expected values)
- Consistent failure BUT root cause traced to `e2e/` code, not `cmd/entire/cli/`
- Test setup/teardown issues (missing git config, temp dir cleanup, port conflicts)

#### Ambiguous cases:

Read `entire.log` carefully:
- If hooks fired correctly and metadata is valid -> lean **flaky**
- If hooks fired but produced wrong results -> lean **real-bug**

### Step 3: Cross-Agent Correlation

Before reporting, check correlations using re-run data:
- Same test fails for 3+ agents, all re-runs also fail -> strong **real-bug**
- Same test fails for multiple agents, but re-runs pass -> **flaky** (shared prompt issue)
- One agent fails consistently, others pass -> agent-specific issue (still **real-bug** if re-runs confirm)

### Step 4: Present Findings Report

For each test+agent pair, print a findings block:

```
## <TestName> (<agent>) -- <classification>

**Re-run results:** original=FAIL, rerun1=PASS, rerun2=PASS
**Evidence:**
- <1-2 sentence summary of what went wrong>
- <key artifact evidence: entire.log excerpt, console.log excerpt, etc.>
```

For `flaky` failures, include proposed fix description:

```
**Proposed fix:** <description>
  - File: <path to test file or e2e infrastructure file>
  - Change: <what will be modified>
```

Common flaky fixes:
- Agent asked for confirmation -> append "Do not ask for confirmation" to prompt
- Agent wrote to wrong path -> be more explicit about paths in prompt
- Agent committed when shouldn't -> add "Do not commit" to prompt
- Checkpoint wait timeout -> increase timeout argument
- Agent timeout (signal: killed) -> increase per-test timeout, simplify prompt
- Auth/env not propagated -> fix test harness env setup in `e2e/` code
- Test helper bug (wrong assertion, bad glob) -> fix test helper in `e2e/`
- tmux session setup issue -> fix `NewTmuxSession` or session config in `e2e/`

For `real-bug` failures, include root cause analysis:

```
**Root cause analysis:**
  - Component: <hooks | session | checkpoint | strategy | agent>
  - Suspected location: <file:function>
  - Description: <what's wrong and why>
  - Proposed fix: <what code change would address it>
```

### Step 5: Summary

Print a summary table (classification only, no "Action Taken"):
```
| Test | Agent(s) | Re-runs | Classification |
|------|----------|---------|----------------|
| TestFoo | claude-code | FAIL/PASS/PASS | flaky |
| TestBar | all agents | FAIL/FAIL/FAIL | real-bug |
| TestBaz | opencode | FAIL/PASS/FAIL | flaky (non-deterministic) |
```
