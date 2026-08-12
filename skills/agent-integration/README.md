# Agent Integration Skill

A multi-phase toolkit for taking a new AI coding agent from unknown to fully integrated with the Entire CLI.

## Structure

This skill is split between an orchestrator skill and a plugin with individual commands:

### Orchestrator (skill)

- `.claude/skills/agent-integration/SKILL.md` — Runs all 3 phases sequentially as `/agent-integration`

### Individual Commands (plugin)

- `.claude/plugins/agent-integration/commands/research.md` — `/agent-integration:research`
- `.claude/plugins/agent-integration/commands/write-tests.md` — `/agent-integration:write-tests`
- `.claude/plugins/agent-integration/commands/implement.md` — `/agent-integration:implement`

## Loading the Plugin

The individual `:` subcommands require the plugin to be loaded. Options:

```bash
# Option 1: Load via --plugin-dir flag
claude --plugin-dir .claude/plugins/agent-integration/

# Option 2: Shell alias (add to ~/.zshrc)
alias claude-dev='claude --plugin-dir .claude/plugins/agent-integration/'
```

## Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/agent-integration` | Run all 3 phases | Full integration |
| `/agent-integration:research` | Assess compatibility | Compatibility report + test script |
| `/agent-integration:write-tests` | Write E2E test suite | AgentRunner + test scenarios |
| `/agent-integration:implement` | Build agent via TDD | Go package under `cmd/entire/cli/agent/` |

## Typical Workflow

```
# Full pipeline (single session)
/agent-integration

# Or individual phases
/agent-integration:research       # 1. Can this agent integrate?
/agent-integration:write-tests    # 2. What should the tests look like?
/agent-integration:implement      # 3. Build it with TDD
```

## Parameters

Collected once and reused across commands:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `AGENT_NAME` | "Windsurf" | Human-readable name |
| `AGENT_SLUG` | "windsurf" | Lowercase slug |
| `AGENT_BIN` | "windsurf" | CLI binary name |
| `LIVE_COMMAND` | "windsurf --project ." | Launch command |
| `EVENTS_OR_UNKNOWN` | "unknown" | Known hook events or "unknown" |

## Architecture References

- Agent interface: `cmd/entire/cli/agent/agent.go`
- Event types: `cmd/entire/cli/agent/event.go`
- Implementation guide: `docs/architecture/agent-guide.md`
- Integration checklist: `docs/architecture/agent-integration-checklist.md`
- E2E test infrastructure: `e2e/`
- Existing agents: Discover via `Glob("cmd/entire/cli/agent/*/")`
