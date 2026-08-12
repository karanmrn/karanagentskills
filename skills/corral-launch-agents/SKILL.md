---
name: corral-launch-agents
description: Launch new CLI coding agents through Corral Design 1, or correctly reopen existing agent sessions inside a Corral-active Herdr repository. Use when the user asks to launch, spawn, batch-start, reopen, relaunch, or resume agents. New launches create Corral-owned tasks; resumptions reuse existing worktrees and sessions.
---

# Corral Launch Agents

Launch agents through Corral's real `launch` pipeline. Let Corral create the branch, worktree, Herdr workspace, pane, agent process, metadata, and persisted task record. Do not recreate that sequence with raw Git or Herdr commands.

## Resolve the request

Distinguish these targets before acting:

- **Specific repository:** pass its checkout path with `--repo`. Corral resolves the primary checkout and creates a fresh worktree.
- **Specific new worktree location:** also pass `--worktree-path`. The destination is for a new Corral-created checkout; it is not an existing Herdr workspace ID.
- **Existing Corral/Herdr agent or resumable CLI session:** do not launch another Corral task. Use the `herdr` and relevant harness skill instead.
- **Existing external worktree:** use Corral adoption only when the user asks to adopt it. Launching always creates a new task/worktree.

Treat launching as a state-changing action. Execute it only when the user asks to launch; inspection, explanation, or dry-run requests do not authorize a launch.

## Reopen existing Cursor CLI sessions

Corral's launch helper is the wrong tool for resumptions. Load the `herdr` and `cursor-cli` skills, then:

1. Identify the named Herdr session, primary repository checkout, original linked worktree, and exact Cursor chat ID.
2. Select only non-empty chats. Use `meta.json`'s `updatedAtMs` or transcript update time—not directory modification time. Distinguish the parent chat from review subagents.
3. Inspect live panes first. Never resume one chat ID concurrently in two panes; reuse the existing pane.
   If it is open in an incorrectly created top-level workspace, confirm it is idle with no unsent draft, close only that workspace, and never delete the worktree.
4. Reopen the existing linked worktree with repository metadata:

```bash
herdr --session "$SESSION" worktree open \
  --cwd "$PRIMARY_CHECKOUT" \
  --path "$WORKTREE_PATH" \
  --label "$WORKTREE_NAME" \
  --no-focus
```

This opens the existing path; it does not create a Git worktree or Corral task. It is the required Corral-compatible layout because it groups the worktree beneath its repository while preserving the worktree name. If the result says `already_open: true`, reuse that linked workspace. Do not use `workspace create`; it lacks Git worktree metadata and produces a top-level space. Do not use `tab create` under the primary workspace; it shows the repository name instead of a linked worktree entry.

5. Capture `root_pane.pane_id` from the result and resume the exact chat without sending a prompt:

```bash
herdr --session "$SESSION" pane run "$PANE_ID" \
  "cursor-agent --yolo --trust --resume $CHAT_ID"
```

6. Verify the workspace has the expected `checkout_path`, `repo_root`, shared `repo_key`, and `is_linked_worktree: true`. Then verify the history:

```bash
herdr --session "$SESSION" workspace list
herdr --session "$SESSION" agent wait "$PANE_ID" --until idle --timeout 30000
herdr --session "$SESSION" pane read "$PANE_ID" \
  --source recent-unwrapped \
  --lines 200
```

Confirm the terminal title, conversation tail, and `foreground_cwd`. Resuming restores conversation history, not the old process environment.

Corral adoption is separate and normally unnecessary. Use it only when the user explicitly asks to turn an external existing worktree into a persisted Corral task. Do not adopt merely to restore Herdr grouping or resume a CLI chat.

## Use the helper

Resolve the installed skill directory without hardcoding a machine path:

```bash
CORRAL_LAUNCH_SKILL_DIR="${AGENT_SKILLS_DIR:-$HOME/.agents/skills}/corral-launch-agents"
CORRAL_LAUNCH_HELPER="$CORRAL_LAUNCH_SKILL_DIR/scripts/corral_agents.py"
```

Run preflight checks first. Always pass the intended named Herdr session when known:

```bash
python3 "$CORRAL_LAUNCH_HELPER" doctor --session corral
python3 "$CORRAL_LAUNCH_HELPER" list-presets --session corral --agent pi
```

If the session is stopped, report that clearly. Do not silently start, stop, or delete Herdr sessions.

Dry-run the exact launch before creating anything:

```bash
python3 "$CORRAL_LAUNCH_HELPER" launch \
  --session corral \
  --repo <repository-checkout> \
  --task "<task title>" \
  --preset pi \
  --priority 2 \
  --prompt "<task prompt>" \
  --no-focus \
  --dry-run
```

Review the resolved session, preset, repository, worktree destination, base, priority, dirty-checkout policy, and prompt length. Then repeat without `--dry-run` only when the launch is authorized.

To choose an exact new worktree directory, add:

```bash
--worktree-path <new-worktree-path>
```

To launch several agents, use `batch` with a JSON task file. Corral itself permits many launcher processes but caps the preparation pipeline at three concurrent jobs. Read [references/batch-launches.md](references/batch-launches.md) before a batch launch.

## Verify every launch

The helper returns only after Corral has created the worktree and Herdr has detected the interactive agent. Verify persisted and live state:

```bash
python3 "$CORRAL_LAUNCH_HELPER" status \
  --session corral \
  --task "<task title>" \
  --live
```

Report the Corral task ID, title, priority, preset, worktree path, pane ID, persisted launch status, and live Herdr agent status. If launch fails after worktree creation, preserve the failed task/worktree for diagnosis; do not clean it automatically.

## Safety rules

- Never pass `--allow-dirty` without explicit user acceptance. It does **not** copy dirty primary-checkout changes; it merely proceeds without them.
- Never use `--mock-state` outside Corral's smoke test.
- Never insert API keys into command arguments, prompts, output, or preset files. Use the provider's normal credential store or environment.
- Never edit `presets.toml` merely to inspect it. Ask before adding or changing a preset because it affects future launches.
- Do not use Pi's `--print`, RPC mode, export, or model-list commands in a Corral preset. Corral and Herdr expect a long-lived interactive TUI.
- Prefer `--no-focus` for automation so a batch does not steal the user's active pane.
- Use the same Herdr binary/session that runs Corral; a different binary or session can target the wrong runtime.

## Read detailed references

- Read [references/corral-design1.md](references/corral-design1.md) before troubleshooting, changing presets, using the raw Corral CLI, or handling unusual runtime paths. It documents the architecture, every native launch option, preset fields, environment variables, state model, and failures.
- Read [references/pi-agent.md](references/pi-agent.md) before selecting Pi provider/model/thinking/session/tool/skill options or creating a specialized Pi preset.
- Read [references/batch-launches.md](references/batch-launches.md) before launching multiple agents from a file.

For helper options, run:

```bash
python3 "$CORRAL_LAUNCH_HELPER" --help
python3 "$CORRAL_LAUNCH_HELPER" launch --help
```
