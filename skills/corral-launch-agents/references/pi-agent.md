# Pi Agent through Corral

## Contents

1. [How Corral launches Pi](#how-corral-launches-pi)
2. [What “specific Pi Agent” can mean](#what-specific-pi-agent-can-mean)
3. [Pi preset examples](#pi-preset-examples)
4. [Pi command options](#pi-command-options)
5. [Pi environment variables](#pi-environment-variables)
6. [Launch examples](#launch-examples)
7. [Verification and failures](#verification-and-failures)

## How Corral launches Pi

A Pi preset must use:

```toml
[presets.pi]
agent = "pi"
command = ["pi"]
default_priority = 3
base = "main"
```

Corral validates that a Pi preset's executable basename is exactly `pi`. It passes every later `command` element as an argument to Herdr:

```text
herdr agent start <generated-name> --kind pi --pane <pane-id> -- <pi-args...>
```

Herdr waits for the interactive Pi TUI to become ready. Corral then sends the combined preset and per-task prompt with `herdr agent prompt`. This sequencing is important: keep task text in `initial_prompt` and launch `--prompt`, not as positional text inside the preset command.

Pi receives the new worktree as its working directory because Herdr starts it in the worktree's root pane.

Run live help before creating a specialized preset:

```bash
pi --version
pi --help
pi --list-models
herdr --session <session> integration status
```

Pi options, providers, extensions, and model IDs evolve. Never invent a model slug from memory. Select it from `pi --list-models` in the same environment used by Herdr.

Herdr's Pi integration improves state and native session identity. Check it before relying on accurate blocked/done state. Installing it changes global agent configuration; do that only when authorized:

```bash
herdr --session <session> integration install pi
```

## What “specific Pi Agent” can mean

### Fresh Pi with a specific model/configuration

Create or select a dedicated Pi preset whose `command` carries provider/model/thinking/tool arguments, then launch it by preset name. This is the normal and safest interpretation.

### Pi using an exact session identity

Pi supports `--session`, `--session-id`, `--continue`, `--resume`, and `--fork`. Put a deterministic option such as `--session-id` in a dedicated preset only when the user explicitly wants that identity.

Be careful: Corral creates a fresh worktree, while an old Pi session may contain paths and assumptions from a different checkout. Verify that the session belongs to the same repository and that resuming into a new worktree is intentional. Interactive `--resume` opens a selector and can block unattended launches; prefer an exact `--session` or `--session-id` when automation is required.

### Existing Herdr pane or workspace

That is not a launch. Use Herdr to inspect/message the existing Pi agent, or use Corral adoption if the user wants it tracked. `--worktree-path` is a destination for a new checkout; it does not target an existing workspace ID.

## Pi preset examples

Ask before changing `presets.toml`. Use distinct preset names rather than repeatedly rewriting one shared preset.

### Basic interactive Pi

```toml
[presets.pi]
agent = "pi"
command = ["pi"]
default_priority = 3
base = "main"
```

### Provider, model, and thinking level

Replace the example provider/model with a value returned by live Pi model discovery:

```toml
[presets.pi-focused]
agent = "pi"
command = [
  "pi",
  "--model", "provider/model-id",
  "--thinking", "high",
  "--approve",
]
default_priority = 2
base = "main"
initial_prompt = """
Read the repository's AGENTS.md and inspect the code before changing anything.
Complete the assigned task, run relevant checks, and report the result.
"""
```

`--approve` trusts project-local Pi resources for that run. It is not a general replacement for system guardrails.

### Exact Pi session ID

```toml
[presets.pi-session]
agent = "pi"
command = ["pi", "--session-id", "<exact-project-session-id>"]
default_priority = 2
base = "main"
```

Use this only when the user explicitly wants that Pi session identity and it is appropriate for the new worktree.

### Restricted/read-only Pi

```toml
[presets.pi-readonly]
agent = "pi"
command = ["pi", "--tools", "read,grep,find,ls"]
default_priority = 3
base = "main"
```

This disables write/bash tools by allowlisting read-only tools. Confirm the user's task is genuinely inspection-only.

### Extra skill or extension

```toml
[presets.pi-specialized]
agent = "pi"
command = [
  "pi",
  "--skill", "<skill-file-or-directory>",
  "--extension", "<extension-file>",
]
default_priority = 3
base = "main"
```

Paths in a preset are interpreted in the agent's launch environment. Prefer stable paths or resources copied into the worktree. Audit third-party skills/extensions before loading them.

### Repository-specific setup and files

```toml
[presets.pi-node]
agent = "pi"
command = ["pi", "--approve"]
default_priority = 2
base = "main"
copy_files = [".env.local", ".mcp.json"]
setup = ["pnpm install --frozen-lockfile"]
setup_timeout_seconds = 1800

[presets.pi-node.env]
APP_ENV = "development"
```

Never assume this setup works for every repository. `copy_files` can contain secrets; copy only explicitly requested files into trusted worktrees.

## Pi command options

These are the core options exposed by Pi's CLI. Confirm them with live `pi --help` before persisting a preset.

### Model and provider

| Option | Meaning / Corral guidance |
| --- | --- |
| `--provider NAME` | Select a provider. Usually combine with `--model`, or use a provider-qualified model. |
| `--model PATTERN_OR_ID` | Select a model, optionally `provider/id` and `:<thinking>`. Discover live; do not hardcode from memory. |
| `--models PATTERNS` | Comma-separated model patterns available for Ctrl+P cycling. Supports globs/fuzzy matches and thinking suffixes. |
| `--thinking LEVEL` | `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, or `max`. Provider/model support varies. |
| `--api-key KEY` | Avoid in presets and process argv. Prefer credential stores/environment. |

### System prompt and initial task

| Option | Meaning / Corral guidance |
| --- | --- |
| `--system-prompt TEXT` | Replace Pi's normal coding system prompt. Use only for intentional specialized agents. |
| `--append-system-prompt TEXT_OR_FILE` | Append text or file contents; repeatable. Stable policy belongs here, while the task belongs in Corral `--prompt`. |
| Positional messages | Pi accepts initial messages, but do not place them in the preset. Let Corral prompt after Herdr detects readiness. |
| `@file` positional input | Pi can attach files to a message, but Corral's post-readiness prompt API sends text. Put file-reading instructions in the task or use stable prompt resources. |

### Session control

| Option | Meaning / risk in a new Corral worktree |
| --- | --- |
| `--continue`, `-c` | Continue the previous session. Nondeterministic for automation; avoid shared presets. |
| `--resume`, `-r` | Open a session selector. Interactive and likely to block an unattended launch. |
| `--session PATH_OR_ID` | Use a specific session file or partial UUID. Verify repository/worktree compatibility. |
| `--session-id ID` | Use/create an exact project session ID. Most deterministic resume option. |
| `--fork PATH_OR_ID` | Fork an existing Pi session. Verify its source repository context. |
| `--session-dir DIR` | Override session storage and lookup location. Ensure Herdr's process can access it. |
| `--no-session` | Disable persistence. Usually avoid because Corral records native session identity for recovery. |
| `--name`, `-n` | Set Pi's own session display name. This is separate from the Corral task/workspace title. |

### Tool permissions

| Option | Meaning |
| --- | --- |
| `--no-tools`, `-nt` | Disable all built-in, extension, and custom tools. |
| `--no-builtin-tools`, `-nbt` | Disable built-ins while retaining extension/custom tools. |
| `--tools`, `-t` | Comma-separated allowlist across built-in, extension, and custom tools. |
| `--exclude-tools`, `-xt` | Comma-separated denylist. |
| `--approve`, `-a` | Trust project-local files/resources for this run. |
| `--no-approve`, `-na` | Ignore project-local files/resources for this run. |

Built-in tool names are `read`, `bash`, `edit`, `write`, `grep`, `find`, and `ls`. The discovery tools `grep`, `find`, and `ls` may be off by default depending on configuration. Extensions may register additional tools.

### Skills, extensions, prompts, and UI resources

| Option | Meaning |
| --- | --- |
| `--extension`, `-e PATH` | Load an extension file; repeatable. |
| `--no-extensions`, `-ne` | Disable extension discovery; explicit `-e` still loads. |
| `--skill PATH` | Load a skill file/directory; repeatable. |
| `--no-skills`, `-ns` | Disable skill discovery/loading. |
| `--prompt-template PATH` | Load a prompt template file/directory; repeatable. |
| `--no-prompt-templates`, `-np` | Disable prompt-template discovery. |
| `--theme PATH` | Load a theme file/directory. |
| `--no-themes` | Disable theme discovery. |
| `--no-context-files`, `-nc` | Disable AGENTS.md and CLAUDE.md discovery. Use only intentionally; repository instructions are normally important. |

Extensions can add flags. Run `pi --help` in the launch environment after installing or updating extensions.

### Modes and one-shot commands to avoid in Corral presets

| Option | Why it is normally incompatible |
| --- | --- |
| `--print`, `-p` | Non-interactive; processes one prompt and exits, so it is not a durable Corral TUI agent. |
| `--mode text|json|rpc` | Changes output/protocol mode. Corral/Herdr's normal agent flow expects interactive Pi. |
| `--export FILE` | Exports a session and exits. It is a maintenance command, not an agent launch. |
| `--list-models [SEARCH]` | Prints models and exits. Run before editing a preset, never inside one. |

Other startup options:

- `--verbose`: force verbose startup.
- `--offline`: disable startup network operations; same behavior as `PI_OFFLINE=1`.
- `--help`, `--version`: print information and exit; never use in a launch preset.

## Pi environment variables

Do not echo, log, or copy secret values. This list is for selecting the correct provider environment, not for credential discovery.

### Provider credentials and endpoints

- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_OAUTH_TOKEN`
- `ANT_LING_API_KEY`
- `OPENAI_API_KEY`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_BASE_URL`
- `AZURE_OPENAI_RESOURCE_NAME`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT_NAME_MAP`
- `DEEPSEEK_API_KEY`
- `NVIDIA_API_KEY`
- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `CEREBRAS_API_KEY`
- `XAI_API_KEY`
- `FIREWORKS_API_KEY`
- `TOGETHER_API_KEY`
- `OPENROUTER_API_KEY`
- `AI_GATEWAY_API_KEY`
- `ZAI_API_KEY`
- `ZAI_CODING_CN_API_KEY`
- `MISTRAL_API_KEY`
- `MINIMAX_API_KEY`
- `MOONSHOT_API_KEY`
- `OPENCODE_API_KEY`
- `KIMI_API_KEY`
- `CLOUDFLARE_API_KEY`
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_GATEWAY_ID`
- `QWEN_TOKEN_PLAN_API_KEY`
- `QWEN_TOKEN_PLAN_CN_API_KEY`
- `XIAOMI_API_KEY`
- `XIAOMI_TOKEN_PLAN_CN_API_KEY`
- `XIAOMI_TOKEN_PLAN_AMS_API_KEY`
- `XIAOMI_TOKEN_PLAN_SGP_API_KEY`
- `AWS_PROFILE`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_BEARER_TOKEN_BEDROCK`
- `AWS_REGION`

### Pi paths and behavior

| Variable | Meaning |
| --- | --- |
| `PI_CODING_AGENT_DIR` | Pi config directory; default is under the user's `.pi/agent` directory. |
| `PI_CODING_AGENT_SESSION_DIR` | Session storage override; superseded by `--session-dir`. |
| `PI_PACKAGE_DIR` | Package directory override, mainly for immutable package stores. |
| `PI_OFFLINE` | Set to `1`, `true`, or `yes` to disable startup network operations. |
| `PI_TELEMETRY` | Explicitly enable or disable installation telemetry. |
| `PI_SHARE_VIEWER_URL` | Base URL used by Pi's share command. |

Agent-pane variables configured under `[presets.NAME.env]` are exported inside the new shell before setup and Pi startup. Credentials may instead come from the Herdr server's inherited environment or Pi's own auth store. Never move secrets into a preset unless the user explicitly understands the persistence risk.

## Launch examples

### Pi in a specific repository

```bash
python3 scripts/corral_agents.py launch \
  --session <session> \
  --repo <repository-checkout> \
  --task "Investigate authentication" \
  --preset pi \
  --priority 2 \
  --prompt "Read AGENTS.md, investigate the authentication failure, and report findings." \
  --no-focus
```

### Pi with an exact new worktree path

```bash
python3 scripts/corral_agents.py launch \
  --session <session> \
  --repo <repository-checkout> \
  --worktree-path <new-worktree-destination> \
  --task "Repair authentication" \
  --preset pi-focused \
  --priority 1 \
  --prompt-file <prompt-file> \
  --no-focus
```

Always dry-run first by adding `--dry-run`.

## Verification and failures

After success:

```bash
python3 scripts/corral_agents.py status \
  --session <session> \
  --task "<exact task title>" \
  --live
```

Confirm:

- persisted status is `running`;
- preset and agent are the intended Pi configuration;
- worktree path is the intended new checkout;
- Herdr workspace/pane IDs exist;
- live Herdr agent status is available;
- Pi received the prompt once.

If Pi fails to start, check the preset command, executable PATH inside Herdr, Pi authentication, project-local trust, exact provider/model availability, and Herdr's Pi integration. Preserve the worktree and failed task. Do not automatically retry with a different model or duplicate the prompt.
