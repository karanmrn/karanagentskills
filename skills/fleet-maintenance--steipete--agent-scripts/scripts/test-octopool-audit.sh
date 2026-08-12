#!/bin/bash

set -euo pipefail

script_dir=$(cd "$(dirname "$0")" && pwd -P)
audit="$script_dir/octopool-audit.sh"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/octopool-audit-test.XXXXXX")
cleanup() {
  local cleanup_exit_code=$?
  trap - EXIT
  case "$scratch" in
    "${TMPDIR:-/tmp}"/octopool-audit-test.*) rm -rf "$scratch" ;;
    *) printf 'refusing unexpected temporary path: %s\n' "$scratch" >&2 ;;
  esac
  exit "$cleanup_exit_code"
}
trap cleanup EXIT

new_case() {
  case_root="$scratch/$1"
  mkdir -p "$case_root/home" "$case_root/bin" "$case_root/shim" "$case_root/state"

  cat >"$case_root/bin/octopool" <<'STUB'
#!/bin/bash
set -euo pipefail
root=${OCTOPOOL_TEST_ROOT:?}
case "${1:-}" in
  whoami)
    [[ -f "$root/state/logged-in" ]] || exit 1
    printf '{"server":"https://octopool.openclaw.ai","pool":"maintainers","login":"tester","client":"test-mac"}\n'
    ;;
  health)
    if [[ -f "$root/state/degraded" ]]; then
      printf '{"pool":"maintainers","identities_total":2,"identities_healthy":1}\n'
    else
      printf '{"pool":"maintainers","identities_total":2,"identities_healthy":2}\n'
    fi
    ;;
  login)
    printf '%s\n' "$*" >>"$root/state/login-calls"
    [[ "${2:-}" == "https://octopool.openclaw.ai" ]]
    [[ "${3:-}" == "--gh-path" && "${4:-}" == "$root/bin/real-gh" ]]
    touch "$root/state/logged-in"
    ;;
  install-shim)
    printf '%s\n' "$*" >>"$root/state/install-calls"
    [[ "${2:-}" == "--shell" && "${3:-}" == "zsh" ]]
    [[ "${4:-}" == "--dry-run" ]] && exit 0
    ln -sfn "$root/bin/octopool" "$root/shim/gh"
    touch "$root/state/shim-installed"
    if [[ -f "$root/state/needs-zprofile" ]] &&
      ! grep -Fqx '# BEGIN Codex-managed Octopool login shim' "$root/home/.zprofile" 2>/dev/null
    then
      exit 1
    fi
    ;;
  *) exit 2 ;;
esac
STUB

  cat >"$case_root/bin/real-gh" <<'STUB'
#!/bin/bash
set -euo pipefail
[[ "${1:-}" == auth && "${2:-}" == token ]]
printf 'test-token\n'
STUB

  cat >"$case_root/bin/zsh-test" <<'STUB'
#!/bin/bash
set -euo pipefail
root=${OCTOPOOL_TEST_ROOT:?}
case "${1:-}" in
  -c)
    if [[ -f "$root/state/force-stock" || ! -f "$root/state/shim-installed" ]]; then
      printf '%s\n' "$root/bin/real-gh"
    else
      printf '%s\n' "$root/shim/gh"
    fi
    ;;
  -lc)
    if [[ -f "$root/state/force-stock" || ! -f "$root/state/shim-installed" ]]; then
      printf '%s\n' "$root/bin/real-gh"
    elif [[ -f "$root/state/needs-zprofile" ]] &&
      ! grep -Fqx '# BEGIN Codex-managed Octopool login shim' "$root/home/.zprofile" 2>/dev/null
    then
      printf '%s\n' "$root/bin/real-gh"
    else
      printf '%s\n' "$root/shim/gh"
    fi
    ;;
  *) exit 2 ;;
esac
STUB

  chmod 755 "$case_root/bin/octopool" "$case_root/bin/real-gh" "$case_root/bin/zsh-test"
}

run_case() {
  HOME="$case_root/home" \
    ZDOTDIR="$case_root/home" \
    OCTOPOOL_TEST_ROOT="$case_root" \
    OCTOPOOL_AUDIT_GH_PATH="$case_root/bin/real-gh" \
    OCTOPOOL_AUDIT_ZSH_BIN="$case_root/bin/zsh-test" \
    PATH="$case_root/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" \
    "$audit" "$@"
}

prepare_healthy() {
  touch "$case_root/state/logged-in" "$case_root/state/shim-installed"
  ln -s "$case_root/bin/octopool" "$case_root/shim/gh"
}

output="$scratch/output.txt"

new_case healthy
prepare_healthy
run_case >"$output"
grep -q 'octopool: current binary=current zsh-c=current zsh-lc=current whoami=current health=current-2/2' "$output"

new_case stock-bypass
prepare_healthy
touch "$case_root/state/force-stock"
if run_case >"$output" 2>&1; then
  printf 'expected stock-gh bypass audit to fail\n' >&2
  exit 1
fi
grep -q 'zsh-c=stock-gh zsh-lc=stock-gh' "$output"

new_case missing-login
touch "$case_root/state/shim-installed"
ln -s "$case_root/bin/octopool" "$case_root/shim/gh"
if run_case >"$output" 2>&1; then
  printf 'expected missing login audit to fail\n' >&2
  exit 1
fi
grep -q 'whoami=invalid' "$output"

new_case degraded-health
prepare_healthy
touch "$case_root/state/degraded"
if run_case >"$output" 2>&1; then
  printf 'expected degraded health audit to fail\n' >&2
  exit 1
fi
grep -q 'health=degraded' "$output"

new_case repair-idempotency
touch "$case_root/state/needs-zprofile"
printf '# unrelated startup content\nexport FLEET_TEST=1\n' >"$case_root/home/.zprofile"
run_case --repair >"$output"
cp "$case_root/home/.zprofile" "$case_root/zprofile-after-first"
run_case --repair >>"$output"
cmp "$case_root/zprofile-after-first" "$case_root/home/.zprofile"
/bin/zsh -n "$case_root/home/.zprofile"
[[ $(grep -Fc '# BEGIN Codex-managed Octopool login shim' "$case_root/home/.zprofile") == 1 ]]
[[ $(grep -Fc '# END Codex-managed Octopool login shim' "$case_root/home/.zprofile") == 1 ]]
grep -q '^# unrelated startup content$' "$case_root/home/.zprofile"
grep -q '^export FLEET_TEST=1$' "$case_root/home/.zprofile"
[[ $(grep -Fc 'login https://octopool.openclaw.ai --gh-path' "$case_root/state/login-calls") == 2 ]]

new_case malformed-block
cat >"$case_root/home/.zprofile" <<'PROFILE'
# BEGIN Codex-managed Octopool login shim
# BEGIN Codex-managed Octopool login shim
# END Codex-managed Octopool login shim
PROFILE
if run_case --repair >"$output" 2>&1; then
  printf 'expected malformed managed block repair to fail\n' >&2
  exit 1
fi
grep -q 'refusing malformed or duplicate managed block' "$output"
[[ ! -e "$case_root/state/login-calls" ]]

printf 'octopool-audit tests: ok\n'
