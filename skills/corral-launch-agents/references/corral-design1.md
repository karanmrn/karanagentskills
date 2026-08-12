# Corral Design 1 programmatic launch reference

## Contents

1. [Mental model](#mental-model)
2. [Launch pipeline](#launch-pipeline)
3. [Helper versus native CLI](#helper-versus-native-cli)
4. [Every native launch option](#every-native-launch-option)
5. [Runtime environment](#runtime-environment)
6. [Preset schema](#preset-schema)
7. [Task and state model](#task-and-state-model)
8. [Other native commands](#other-native-commands)
9. [Concurrency](#concurrency)
10. [Failure modes](#failure-modes)
11. [Safe troubleshooting](#safe-troubleshooting)

## Mental model

Corral Design 1 is an executable Herdr plugin, not a separate process runtime. Herdr owns every PTY, shell, workspace, pane, and agent process. Corral adds the product layer:

- repository, preset, task, priority, and prompt selection;
- one fresh Git worktree and branch per task;
- optional copied files, environment, and setup commands;
- agent startup and initial prompt delivery;
- P1-P4 metadata and attention-first sorting;
- SQLite task persistence and startup rehydration;
- archive and clean-worktree removal controls.

A programmatic launch creates one **Corral task** inside one named **Herdr session**. It does not create another Corral application instance. The durable process is Herdr; the `corral launch` process exits after the new agent is ready.

Terminology:

- **Repository / primary checkout:** the source Git repository. `--repo` may name a linked checkout, but Corral resolves the primary checkout through `git worktree list`.
- **Worktree:** the new isolated checkout created for this task.
- **Workspace:** the Herdr workspace wrapping that worktree.
- **Pane:** the Herdr terminal pane where the shell and agent run.
- **Preset:** persisted TOML describing agent kind, argv, base, setup, copied files, prompt, and environment.
- **Task:** Corral's persisted record tying all of the above together.

Use the separate `herdr` skill to inspect or coordinate agents that already exist. Use this skill to create new Corral-owned tasks.

## Launch pipeline

The native launch function performs this exact sequence:

1. Normalize and validate the task title; it must be 1-80 characters.
2. Resolve the repository's primary checkout and the requested base commit.
3. Read `git status --porcelain=v1` in the primary checkout.
4. Refuse a dirty primary checkout unless `--allow-dirty` was explicit.
5. Allocate a UUID task ID, branch `corral/<task-slug>-<uuid8>`, and internal agent name `corral_<uuid16>`.
6. Acquire one of three global preparation locks.
7. Ask Herdr `worktree create` to create the branch, worktree, workspace, and root pane.
8. Persist a `preparing` task in SQLite and apply pane metadata.
9. Wait for the new pane's shell prompt.
10. Copy each configured `copy_files` entry from the primary checkout.
11. Export preset `[env]` values into the pane shell.
12. Run preset `setup` commands sequentially, each with its configured timeout.
13. Ask Herdr `agent start` to launch the preset's interactive CLI in that pane.
14. If a prompt exists, send it with Herdr `agent prompt` after readiness.
15. Read the native agent session identity, mark the task `running`, refresh metadata, and apply Corral's Agent view.
16. Release the preparation lock and exit.

On any error after task creation, Corral marks the task `failed`, records the error, and intentionally leaves the worktree for inspection.

## Helper versus native CLI

Prefer the bundled helper:

```bash
python3 scripts/corral_agents.py launch --session <session> ...
```

It discovers the linked plugin, config/state directories, socket, database override, Herdr binary, and Pi preset. It invokes the real native launcher without reimplementing the pipeline.

The raw native entry point is the linked Design 1 plugin's `bin/corral` executable:

```bash
<plugin-root>/bin/corral launch \
  --repo <repository> \
  --task "<title>" \
  --preset <preset>
```

The raw entry point is not installed on `PATH` by Corral's installer. Herdr normally injects its required environment only when invoking the plugin. An ordinary terminal must reconstruct that environment; omitting it can create an agent and then fail while applying the Corral view.

## Every native launch option

| Option | Required | Meaning |
| --- | --- | --- |
| `--repo PATH` | yes | Any checkout belonging to the source repository. Corral resolves the primary checkout and uses its committed Git state. |
| `--task TEXT` | yes | Display title, metadata title, and branch-slug source. Whitespace is normalized; maximum 80 characters. |
| `--preset NAME` | yes | Exact `[presets.NAME]` entry from `presets.toml`. Determines the agent and argv. |
| `--priority N` | no | P1-P4. Defaults to the preset's `default_priority`. |
| `--base REF` | no | Branch, tag, or commit to resolve to a commit. Defaults to the preset's `base`. |
| `--prompt TEXT` | no | Per-task prompt appended after the preset's `initial_prompt`, separated by one blank line. |
| `--worktree-path PATH` | no | Exact destination for the **new** worktree. It is not an existing workspace or pane selector. |
| `--allow-dirty` | no | Continue when the primary checkout is dirty. Dirty changes are still excluded. |
| `--focus` | no | Focus the new Herdr workspace. |
| `--no-focus` | no | Keep the current focus. This is the normal automation choice and native default. |
| `--json` | no | Print the final task record as compact JSON after progress messages. |
| `--mock-state STATE` | test only | Replace real agent startup with a fake state. Accepted states are `idle`, `working`, `blocked`, and `unknown`; native code rejects it unless `CORRAL_SMOKE_TEST=1`. |

Important details:

- The interactive `Ctrl+Alt+N` overlay differs from scripted launch: it always uses `main`, clears the preset's `initial_prompt`, and starts an empty agent session.
- Scripted launch honors the preset base and combines preset plus per-task prompts.
- `--allow-dirty` is not a snapshot or copy operation. It simply accepts that uncommitted changes will be absent.
- The branch name is always generated by Corral; there is no native `--branch` override.
- Agent-specific argv cannot be added to one launch call. Put those arguments in a named preset's `command` array.
- Per-launch environment overrides are not supported. Put agent-pane variables under `[presets.NAME.env]`.

## Runtime environment

The helper resolves and exports these values before invoking native Corral:

| Variable | Purpose |
| --- | --- |
| `HERDR_BIN_PATH` | Exact Herdr binary used for all API CLI calls. Use the same build that runs the session. |
| `HERDR_SESSION` | Named session whose server, workspaces, and panes receive the task. |
| `HERDR_SOCKET_PATH` | Unix socket used by Corral's direct `agent.view.set` request. Required for a clean launch. |
| `HERDR_PLUGIN_ROOT` | Design 1 plugin directory containing `corral.py`, manifest, and `bin/corral`. |
| `HERDR_PLUGIN_CONFIG_DIR` | Plugin config directory containing `presets.toml` and normally `corral.sqlite3`. |
| `HERDR_PLUGIN_STATE_DIR` | Plugin state directory containing the saved Agent view and legacy migration files. |
| `CORRAL_CONFIG_DIR` | External-call override for the same plugin config directory. |
| `CORRAL_STATE_DIR` | External-call override for the same plugin state directory. |
| `CORRAL_STORE_PATH` | Optional exact SQLite database override. Without it, Corral uses `<config-dir>/corral.sqlite3`. |

Additional variables recognized by the code or installer:

| Variable | Purpose |
| --- | --- |
| `CORRAL_SESSION` | Helper-only preferred session override. Native Corral reads `HERDR_SESSION`. |
| `CORRAL_BIN` | Helper-only exact path to `plugin/bin/corral`. |
| `HERDR_BIN` | Installer/helper fallback for selecting a Herdr binary. |
| `CORRAL_PYTHON` | Override the Python 3.11+ interpreter selected by `plugin/bin/corral`. |
| `XDG_CONFIG_HOME` | Changes Herdr's config root, plugin registry, config directory, and session sockets. |
| `XDG_STATE_HOME` | Changes Herdr's state root and default plugin state directory. |
| `HERDR_CONFIG_PATH` | Overrides Herdr's config file; the helper uses its parent as the Herdr config root. |
| `CORRAL_SMOKE_TEST` | Enables fake agent states. Never set for a real launch. |
| `HERDR_PLUGIN_CONTEXT_JSON` | Herdr action context used to discover focused pane/workspace targets. Not needed for `launch`. |
| `CORRAL_TARGET_PANE_ID` | Explicit overlay/focused-pane target used by interactive controls. Not needed for `launch`. |
| `HERDR_PANE_ID`, `HERDR_ACTIVE_PANE_ID` | Alternative pane targeting context for interactive actions. |
| `HERDR_WORKSPACE_ID`, `HERDR_ACTIVE_WORKSPACE_ID` | Alternative workspace targeting context for interactive actions. |

Do not export credential variables in diagnostic output. Agent credentials should be available through the normal shell/credential store used by the Herdr server and agent.

For a raw external call, the conceptual environment is:

```bash
CORRAL_SESSION_NAME=<session>
CORRAL_PLUGIN_ROOT=<linked-design1-plugin-directory>
CORRAL_PLUGIN_CONFIG_DIR="$(herdr --session "$CORRAL_SESSION_NAME" plugin config-dir corral.design1)"
CORRAL_PLUGIN_STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/herdr/plugins/corral.design1"
CORRAL_SOCKET_PATH=<socket-path-from-herdr-session-list>

HERDR_BIN_PATH="$(command -v herdr)" \
HERDR_SESSION="$CORRAL_SESSION_NAME" \
HERDR_SOCKET_PATH="$CORRAL_SOCKET_PATH" \
HERDR_PLUGIN_ROOT="$CORRAL_PLUGIN_ROOT" \
HERDR_PLUGIN_CONFIG_DIR="$CORRAL_PLUGIN_CONFIG_DIR" \
HERDR_PLUGIN_STATE_DIR="$CORRAL_PLUGIN_STATE_DIR" \
CORRAL_CONFIG_DIR="$CORRAL_PLUGIN_CONFIG_DIR" \
CORRAL_STATE_DIR="$CORRAL_PLUGIN_STATE_DIR" \
"$CORRAL_PLUGIN_ROOT/bin/corral" launch ...
```

Prefer the helper instead of maintaining this manually.

## Preset schema

Presets live in `presets.toml` under the Corral plugin config directory.

| Field | Required | Validation and behavior |
| --- | --- | --- |
| `agent` | yes | One of `claude`, `codex`, `cursor`, `pi`, or `hermes`. |
| `command` | yes | Non-empty argv array. Executable basename must be canonical: `claude`, `codex`, `cursor-agent`, `pi`, or `hermes`. Only elements after the executable are forwarded to Herdr `agent start`. |
| `default_priority` | no | Integer 1-4; default 3. |
| `base` | no | Non-empty Git ref; default `HEAD`. |
| `setup` | no | Array of shell command strings, executed sequentially in the pane before agent start. |
| `copy_files` | no | Repository-relative paths copied from the primary checkout. Absolute and parent-traversal entries are rejected. Missing entries are skipped with a warning. |
| `initial_prompt` | no | String sent on scripted launches before the per-task prompt. Ignored by the interactive launcher. |
| `setup_timeout_seconds` | no | Positive integer per setup command; default 1800. |
| `[presets.NAME.env]` | no | Scalar values exported into the pane shell before setup and agent startup. |

Corral automatically inserts unattended flags when absent:

- Codex: `--yolo`
- Claude Code: `--dangerously-skip-permissions`
- Cursor: `--yolo` unless `--force` exists, plus `--trust`
- Pi and Hermes: no automatic flags

Preset setup runs inside the three-job preparation limit. A repository-specific setup such as `pnpm install --frozen-lockfile` will fail on repositories that do not use that package manager/lockfile. Prefer separate presets for materially different repository families.

## Task and state model

Design 1 stores state in SQLite using WAL mode, foreign keys, a 30-second busy timeout, and short `BEGIN IMMEDIATE` transactions. Rows are isolated by `HERDR_SESSION`, even when sessions share the same database file.

Each task records approximately:

- task ID and title;
- repository ID/name/path;
- worktree path, branch, base, and base commit SHA;
- Herdr workspace and pane IDs;
- agent kind, generated name, and native session identity;
- preset, priority, and combined initial prompt;
- status, error, creation time, archive time, and cleanup time.

Statuses include `preparing`, `running`, `failed`, `archived`, and `cleaned`.

Pane metadata includes priority rank/label, one colored priority token, task title/ID, repository, branch, and launch status. The Agent view sorts by attention class, then priority, then state-change recency.

At Herdr startup, Corral takes one session snapshot, matches active tasks by metadata or stable worktree path, refreshes workspace/pane IDs, reapplies metadata, and restores the view. Archived and cleaned tasks are skipped.

## Other native commands

These are available through `plugin/bin/corral` but are not all exposed by this helper:

| Command | Key options / purpose |
| --- | --- |
| `startup` | Ensure standard preset/view and rehydrate metadata; invoked by Herdr. |
| `rehydrate` | Reconcile live runtime IDs and reapply metadata/view. |
| `ensure-presets` | Add the default Cursor preset when none exists. |
| `open-overlay ENTRYPOINT` | Open launcher, rename, rename-agent, archive, or cleanup overlay. Requires focused-pane context. |
| `launcher` | Interactive terminal launcher. |
| `adopt [--priority N] [--all]` | Adopt focused or all linked Herdr worktrees without relaunching agents. |
| `launch ...` | Create one new task; fully documented above. |
| `set-priority N [--task ID_OR_TITLE]` | Update priority; focused untracked agents are adopted for priority only. |
| `focus-attention` | Focus the next blocked or done Corral agent. |
| `rename --task TARGET --title TEXT` | Rename the task and Herdr workspace. |
| `close-agent --confirm` | Close only the focused Corral agent pane in the current working tree version. |
| `archive --task TARGET --confirm` | Close the Herdr workspace, preserving worktree and branch. |
| `cleanup --task TARGET --confirm` | Remove a clean Corral-owned worktree, preserving the branch. |
| `state [--json]` | Print persisted state for the current Herdr session. |
| `order [--json]` | Print current Corral agents in attention order. |
| `mock-state ...` | Smoke-test only. |

The exact command surface can change. Run `<plugin-root>/bin/corral --help` and the relevant subcommand `--help` before relying on uncommon options.

## Concurrency

Multiple external `launch` processes are supported. Corral uses:

- UUID task IDs and branch suffixes to avoid name collisions;
- SQLite serialization to prevent lost task updates;
- three cross-process file locks named `setup-slot-0.lock` through `setup-slot-2.lock`;
- one lock held across worktree creation, copy/setup, agent startup, prompt delivery, and final metadata.

Launching more than three tasks is safe: extra processes print that the setup queue is full and wait. Starting more than three helper batch workers normally adds no throughput. Keep the helper's default `--parallel 3` unless there is a measured reason to change it.

## Failure modes

| Symptom | Likely cause | Safe response |
| --- | --- | --- |
| `missing required environment variable: HERDR_SOCKET_PATH` | Raw external invocation omitted the socket. | Use the helper or set the exact named-session socket. Check whether an agent/worktree was already created before retrying. |
| `server_not_running` | Named Herdr server is stopped or wrong session selected. | Ask the user to start/attach the intended session; do not silently start another. |
| `Primary checkout has ... uncommitted changes` | Source checkout is dirty. | Explain that dirty changes will not be copied. Continue only with explicit `--allow-dirty`. |
| `unknown preset` / no Pi preset | Wrong plugin config directory or missing preset. | Run `list-presets`; inspect the resolved config directory. Ask before editing presets. |
| Setup command failed | Preset setup does not fit the repository or timed out. | Preserve the worktree; inspect the task error and pane output. Fix/select a preset, then launch a new task unless the user directs cleanup. |
| Agent executable not found/detected | Herdr pane PATH differs, agent is missing, or preset executable is noncanonical. | Verify executable in the environment used by Herdr and run native help. Do not substitute shell aliases. |
| Prompt not observed | Agent started but prompt delivery failed or task failed after startup. | Inspect persisted state, live agent status, and pane output before retrying; avoid duplicate prompts. |
| Task marked failed but process appears live | Failure happened after `agent start`, commonly metadata/view setup. | Inspect the existing pane/worktree and fix runtime environment; do not blindly relaunch. |
| SQLite busy/locked | Too many external writers or abnormal process exit. | Let the 30-second busy timeout finish; verify no active launcher before intervention. Never delete WAL/lock files casually. |
| Worktree destination exists | `--worktree-path` is not a fresh destination. | Choose a new path or use adoption when appropriate. Do not overwrite it. |

## Safe troubleshooting

1. Run helper `doctor` and record the resolved session and paths.
2. Run helper `list-presets`; do not print environment values or API keys.
3. Run helper `status --task <title-or-id> --live`.
4. Inspect Herdr's pane only if a pane ID exists.
5. Inspect `git status` in both primary checkout and failed worktree.
6. Read the Corral/Herdr logs for the selected session.
7. Fix environment/preset configuration only with authorization.
8. Re-run a dry launch before creating a replacement task.

Never clean, archive, close, or delete a failed task/worktree as part of diagnosis unless the user explicitly asks.
