#!/bin/bash

set -u
set -o pipefail

usage() {
  printf 'usage: %s [--live] [--timeout SECONDS]\n' "$0" >&2
}

live=false
timeout_seconds=120
while [[ $# -gt 0 ]]; do
  case "$1" in
    --live)
      live=true
      shift
      ;;
    --timeout)
      [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { usage; exit 2; }
      timeout_seconds="$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

run_bounded() {
  local seconds="$1"
  shift
  /usr/bin/perl -e '$SIG{ALRM}=sub{exit 124}; alarm shift; exec @ARGV' "$seconds" "$@"
}

resolve_tool() {
  local override_name="$1"
  local command_name="$2"
  local override_value="${!override_name:-}"
  if [[ -n "$override_value" ]]; then
    [[ -x "$override_value" ]] || return 1
    printf '%s\n' "$override_value"
    return
  fi
  local resolved
  resolved=$(command -v "$command_name" 2>/dev/null || true)
  if [[ -n "$resolved" ]]; then
    printf '%s\n' "$resolved"
    return
  fi
  local candidate
  for candidate in \
    "$HOME/.local/bin/$command_name" \
    "/opt/homebrew/bin/$command_name" \
    "/usr/local/bin/$command_name"
  do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return
    fi
  done
  return 1
}

failures=0
codex_ready=false
claude_ready=false
codex_bin=$(resolve_tool AGENT_CLI_CODEX_BIN codex || true)
claude_bin=$(resolve_tool AGENT_CLI_CLAUDE_BIN claude || true)

check_tool() {
  local name="$1"
  local binary="$2"
  shift 2
  if [[ -z "$binary" ]]; then
    printf 'agent-cli: drift tool=%s state=missing\n' "$name" >&2
    failures=$((failures + 1))
    return
  fi

  local version_output
  version_output=$(run_bounded 15 "$binary" --version </dev/null 2>&1)
  local exit_code=$?
  if [[ "$exit_code" -ne 0 ]]; then
    printf 'agent-cli: drift tool=%s state=version-failed exit=%s path=%s\n' \
      "$name" "$exit_code" "$binary" >&2
    failures=$((failures + 1))
    return
  fi
  version_output=${version_output//$'\n'/ }

  run_bounded 20 "$binary" "$@" </dev/null >/dev/null 2>&1
  exit_code=$?
  if [[ "$exit_code" -ne 0 ]]; then
    printf 'agent-cli: drift tool=%s state=unauthenticated exit=%s path=%s version=%s\n' \
      "$name" "$exit_code" "$binary" "$version_output" >&2
    failures=$((failures + 1))
    return
  fi

  printf 'agent-cli: current tool=%s path=%s version=%s auth=ok\n' \
    "$name" "$binary" "$version_output"
  printf -v "${name}_ready" '%s' true
}

check_tool codex "$codex_bin" login status
check_tool claude "$claude_bin" auth status

if [[ "$live" == true ]]; then
  scratch=$(mktemp -d "${TMPDIR:-/tmp}/agent-cli-audit.XXXXXX")
  cleanup() {
    local cleanup_exit_code=$?
    trap - EXIT
    case "$scratch" in
      "${TMPDIR:-/tmp}"/agent-cli-audit.*) rm -rf "$scratch" ;;
      *) printf 'agent-cli: refusing unexpected temporary path: %s\n' "$scratch" >&2 ;;
    esac
    exit "$cleanup_exit_code"
  }
  trap cleanup EXIT

  codex_output="$scratch/codex.txt"
  if [[ "$codex_ready" == true ]]; then
    if run_bounded "$timeout_seconds" "$codex_bin" exec \
      --ephemeral \
      --skip-git-repo-check \
      --ignore-rules \
      --sandbox read-only \
      --color never \
      -C "$scratch" \
      --output-last-message "$codex_output" \
      'Reply with exactly FLEET_OK.' </dev/null >/dev/null 2>&1 \
      && grep -qx 'FLEET_OK' "$codex_output"
    then
      printf 'agent-cli-live: current tool=codex result=ok\n'
    else
      exit_code=$?
      printf 'agent-cli-live: drift tool=codex result=failed exit=%s\n' "$exit_code" >&2
      failures=$((failures + 1))
    fi
  else
    printf 'agent-cli-live: skipped tool=codex reason=prerequisite-failed\n' >&2
  fi

  claude_output="$scratch/claude.json"
  if [[ "$claude_ready" == true ]]; then
    if run_bounded "$timeout_seconds" "$claude_bin" \
      --print \
      --safe-mode \
      --setting-sources user \
      --strict-mcp-config \
      --mcp-config '{"mcpServers":{}}' \
      --tools '' \
      --no-session-persistence \
      --max-turns 1 \
      --output-format text \
      'Reply with exactly FLEET_OK.' </dev/null >"$claude_output" 2>/dev/null \
      && grep -qx 'FLEET_OK' "$claude_output"
    then
      printf 'agent-cli-live: current tool=claude result=ok\n'
    else
      exit_code=$?
      printf 'agent-cli-live: drift tool=claude result=failed exit=%s\n' "$exit_code" >&2
      failures=$((failures + 1))
    fi
  else
    printf 'agent-cli-live: skipped tool=claude reason=prerequisite-failed\n' >&2
  fi
fi

if [[ "$failures" -gt 0 ]]; then
  printf 'agent-cli-summary: drift failures=%s\n' "$failures" >&2
  exit 1
fi
printf 'agent-cli-summary: current failures=0\n'
