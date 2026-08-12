# E2E Implement Fixes

Apply fixes for E2E test failures, verify with scoped E2E tests.

> **Before implementing any fixes, enter plan mode by invoking /plan.**
> Analyze the findings (Steps 1-2 below), produce a complete fix plan with
> specific file paths and code changes, and get user approval before executing.

> **IMPORTANT: Running real E2E tests is a HARD REQUIREMENT of this procedure.**
> Every fix MUST be verified with real E2E tests before the summary step.
> Canary tests use the Vogon fake agent and cannot catch agent-specific issues.
> Do NOT skip E2E verification unless the user explicitly declines due to cost.

## Inputs

This procedure accepts findings from one of:
- **`/e2e:triage-ci` output** -- findings report already in conversation context
- **`/e2e:debug` output** -- root cause analysis already in conversation context
- **Standalone description** -- user describes known failure and desired fix

## Step 1: Identify Fixes

From the findings in context, identify actionable fixes:

### For `flaky` failures: describe the proposed fix

For agent-behavior flaky issues, fixes typically modify test prompts. For test-bug flaky issues, fixes target `e2e/` infrastructure code (harness setup, helpers, env propagation).

```
**Proposed fix:** <description>
  - File: <path to test file or e2e infrastructure file>
  - Change: <what will be modified -- e.g., append "Do not ask for confirmation" to prompt, or fix env propagation in NewTmuxSession>
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

### For `real-bug` failures: describe root cause analysis

```
**Root cause analysis:**
  - Component: <hooks | session | checkpoint | strategy | agent>
  - Suspected location: <file:function>
  - Description: <what's wrong and why>
  - Proposed fix: <what code change would address it>
```

## Step 2: Ask the User

Prompt the user:

> **Should I fix these?**
> - [list of tests with classifications and proposed fixes]
> - You can select all, specific tests, or skip.

Wait for user response before proceeding.

## Step 3: Apply Fixes

For **flaky** fixes the user approved:
1. Apply fixes directly in the working tree (no branch creation)
2. Run static checks:
   ```bash
   mise run fmt && mise run lint
   mise run test:e2e:canary   # Must pass
   ```
3. **Run real E2E tests to verify the fix.** Scope depends on what was changed:
   - **Agent-specific fix** (e.g., `e2e/agents/cursor_cli.go`, one agent's config/trust/env): run the full suite for that agent only:
     ```bash
     mise run test:e2e --agent <agent>
     ```
   - **Shared test infra fix** (e.g., `e2e/agents/agent.go`, `e2e/testutil/`, `TmuxSession`, test helpers): run the full suite for all agents that failed, since the fix could affect any of them:
     ```bash
     mise run test:e2e --agent <agent1>
     mise run test:e2e --agent <agent2>
     # ... for each agent that had failures
     ```
   - **Test prompt fix** (e.g., changed wording in a specific test): run that test across all agents that failed it:
     ```bash
     mise run test:e2e --agent <agent> <TestName>
     ```
   **This step is MANDATORY** -- canary tests use the Vogon fake agent and cannot verify agent-specific behavior (trust dialogs, env propagation, config directories, etc.).
4. If any step fails, investigate and adjust. Report what happened to the user.

For **real-bug** fixes the user approved:
1. Apply the fix directly in the working tree (no branch creation)
2. Run static checks and unit tests:
   ```bash
   mise run fmt && mise run lint
   mise run test        # Unit tests
   mise run test:e2e:canary  # Canary tests
   ```
3. **Run real E2E tests to verify the fix (MANDATORY).** Same scoping rules as flaky fixes above:
   - **Agent-specific change** -> full suite for that agent
   - **Shared CLI/infra change** -> full suite for all agents that failed
   - **Narrow change** (single test affected) -> just that test across affected agents
4. Report results to the user.

**GATE: Do NOT proceed to the summary until real E2E tests have been run and results reported for every fix applied above.** If E2E tests were not run, go back and run them now.

## Step 4: Summary

Print a summary table:
```
| Test | Agent(s) | Classification | Action Taken |
|------|----------|----------------|--------------|
| TestFoo | claude-code | flaky | Fixed in working tree |
| TestBar | all agents | real-bug | Fix applied, tests passing |
| TestBaz | opencode | flaky | Skipped (user declined) |
```
