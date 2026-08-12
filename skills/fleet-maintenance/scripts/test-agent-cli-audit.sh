#!/bin/bash

set -euo pipefail

script_dir=$(cd "$(dirname "$0")" && pwd -P)
audit="$script_dir/agent-cli-audit.sh"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/agent-cli-audit-test.XXXXXX")
cleanup() {
  local cleanup_exit_code=$?
  trap - EXIT
  case "$scratch" in
    "${TMPDIR:-/tmp}"/agent-cli-audit-test.*) rm -rf "$scratch" ;;
    *) printf 'refusing unexpected temporary path: %s\n' "$scratch" >&2 ;;
  esac
  exit "$cleanup_exit_code"
}
trap cleanup EXIT

codex_stub="$scratch/codex"
claude_stub="$scratch/claude"

cat >"$codex_stub" <<'STUB'
#!/bin/bash
set -euo pipefail
case "${1:-}" in
  --version) printf 'codex-cli test\n' ;;
  login) [[ "${2:-}" == status ]] ;;
  exec)
    [[ "${AGENT_CLI_TEST_CODEX_LIVE:-ok}" == ok ]] || exit 1
    output=""
    while [[ $# -gt 0 ]]; do
      if [[ "$1" == --output-last-message ]]; then
        output="$2"
        shift 2
      else
        shift
      fi
    done
    [[ -n "$output" ]]
    printf 'FLEET_OK\n' >"$output"
    ;;
  *) exit 2 ;;
esac
STUB

cat >"$claude_stub" <<'STUB'
#!/bin/bash
set -euo pipefail
if [[ "${1:-}" == --version ]]; then
  printf 'Claude Code test\n'
elif [[ "${1:-}" == auth && "${2:-}" == status ]]; then
  [[ "${AGENT_CLI_TEST_CLAUDE_AUTH:-ok}" == ok ]]
elif [[ " $* " == *' --print '* ]]; then
  printf 'FLEET_OK\n'
else
  exit 2
fi
STUB

chmod 755 "$codex_stub" "$claude_stub"

AGENT_CLI_CODEX_BIN="$codex_stub" AGENT_CLI_CLAUDE_BIN="$claude_stub" "$audit" --live --timeout 5

failure_output="$scratch/failure.txt"
if AGENT_CLI_TEST_CLAUDE_AUTH=fail \
  AGENT_CLI_CODEX_BIN="$codex_stub" \
  AGENT_CLI_CLAUDE_BIN="$claude_stub" \
  "$audit" >"$failure_output" 2>&1
then
  printf 'expected unauthenticated Claude audit to fail\n' >&2
  exit 1
fi
grep -q 'tool=claude state=unauthenticated exit=1' "$failure_output"

if AGENT_CLI_TEST_CODEX_LIVE=fail \
  AGENT_CLI_CODEX_BIN="$codex_stub" \
  AGENT_CLI_CLAUDE_BIN="$claude_stub" \
  "$audit" --live --timeout 5 >"$failure_output" 2>&1
then
  printf 'expected failed Codex live turn to fail audit\n' >&2
  exit 1
fi
grep -q 'tool=codex result=failed exit=1' "$failure_output"

printf 'agent-cli-audit tests: ok\n'
