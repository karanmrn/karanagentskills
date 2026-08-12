#!/bin/bash

set -euo pipefail

repair=false
if [[ "${1:-}" == "--repair" ]]; then
  repair=true
  shift
fi
if [[ $# -ne 0 ]]; then
  printf 'usage: %s [--repair]\n' "$0" >&2
  exit 2
fi

server="https://octopool.openclaw.ai"
begin="# BEGIN Codex-managed Octopool login shim"
end="# END Codex-managed Octopool login shim"
zprofile="${ZDOTDIR:-$HOME}/.zprofile"
octopool="${OCTOPOOL_AUDIT_OCTOPOOL_BIN:-$(command -v octopool 2>/dev/null || true)}"
zsh_bin="${OCTOPOOL_AUDIT_ZSH_BIN:-$(command -v zsh 2>/dev/null || true)}"
jq_bin=$(command -v jq 2>/dev/null || true)
for candidate in /opt/homebrew/bin/octopool /usr/local/bin/octopool; do
  [[ -n "$octopool" ]] || [[ ! -x "$candidate" ]] || octopool="$candidate"
done
for candidate in /opt/homebrew/bin/jq /usr/local/bin/jq; do
  [[ -n "$jq_bin" ]] || [[ ! -x "$candidate" ]] || jq_bin="$candidate"
done

if [[ -z "$octopool" || ! -x "$octopool" || -z "$jq_bin" ]]; then
  printf 'octopool: drift binary=missing\n' >&2
  exit 1
fi

probe_gh() {
  [[ -n "$zsh_bin" ]] || return 1
  "$zsh_bin" "$1" 'command -v gh' </dev/null 2>/dev/null | awk 'NF { print; exit }'
}

is_octopool() {
  [[ -n "${1:-}" && -e "$1" && "$1" -ef "$octopool" ]]
}

audit() {
  local failures=0 zsh_c=stock-gh zsh_lc=stock-gh whoami=invalid health=degraded
  local path json counts

  path=$(probe_gh -c || true)
  is_octopool "$path" && zsh_c=current || failures=$((failures + 1))
  path=$(probe_gh -lc || true)
  is_octopool "$path" && zsh_lc=current || failures=$((failures + 1))

  json=$("$octopool" whoami --json 2>/dev/null || true)
  if "$jq_bin" -e 'type == "object" and ([.server, .pool, .login, .client] | all(.[]; type == "string" and test("\\S")))' \
    >/dev/null 2>&1 <<<"$json"
  then
    whoami=current
  else
    failures=$((failures + 1))
  fi

  json=$("$octopool" health 2>/dev/null || true)
  if "$jq_bin" -e 'type == "object" and (.identities_total | type == "number") and
      (.identities_healthy | type == "number") and .identities_total > 0 and
      .identities_healthy == .identities_total' >/dev/null 2>&1 <<<"$json"
  then
    counts=$("$jq_bin" -r '"\(.identities_healthy)/\(.identities_total)"' <<<"$json")
    health="current-$counts"
  else
    failures=$((failures + 1))
  fi

  if [[ $failures -eq 0 ]]; then
    printf 'octopool: current binary=current zsh-c=%s zsh-lc=%s whoami=%s health=%s\n' \
      "$zsh_c" "$zsh_lc" "$whoami" "$health"
    return
  fi
  printf 'octopool: drift binary=current zsh-c=%s zsh-lc=%s whoami=%s health=%s failures=%s\n' \
    "$zsh_c" "$zsh_lc" "$whoami" "$health" "$failures" >&2
  return 1
}

markers_valid() {
  [[ ! -f "$zprofile" ]] && return 0
  awk -v begin="$begin" -v end="$end" '
    index($0, "BEGIN Codex-managed Octopool login shim") {
      begins++; if ($0 != begin || inside || ends) bad=1; inside=1
    }
    index($0, "END Codex-managed Octopool login shim") {
      ends++; if ($0 != end || !inside) bad=1; inside=0
    }
    END { exit bad || inside || begins != ends || begins > 1 }
  ' "$zprofile"
}

write_login_block() {
  local shim_dir="$1" tmp mode=644
  tmp=$(mktemp "${zprofile}.octopool.XXXXXX")
  if [[ -f "$zprofile" ]]; then
    mode=$(stat -f '%Lp' "$zprofile")
    awk -v begin="$begin" -v end="$end" '
      $0 == begin { inside=1; next }
      $0 == end { inside=0; next }
      !inside { print }
    ' "$zprofile" >"$tmp"
  fi
  [[ ! -s "$tmp" ]] || printf '\n' >>"$tmp"
  {
    printf '%s\n' "$begin"
    printf '%s\n' '# macOS path_helper runs after .zshenv; this block owns final Octopool PATH precedence.'
    printf "export PATH=%q:\"\$PATH\"\n" "$shim_dir"
    printf '%s\n' "$end"
  } >>"$tmp"
  chmod "$mode" "$tmp"
  mv "$tmp" "$zprofile"
}

find_real_gh() {
  local candidate
  for candidate in \
    "${OCTOPOOL_AUDIT_GH_PATH:-}" \
    "${OCTOPOOL_GH_PATH:-}" \
    /opt/homebrew/opt/gh/bin/gh \
    /usr/local/opt/gh/bin/gh
  do
    [[ "$candidate" = /* && -x "$candidate" ]] || continue
    is_octopool "$candidate" && continue
    if /usr/bin/env -u GH_TOKEN -u GITHUB_TOKEN "$candidate" auth token </dev/null >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return
    fi
  done
  return 1
}

if [[ "$repair" == false ]]; then
  audit
  exit $?
fi

if ! markers_valid; then
  printf 'octopool: refusing malformed or duplicate managed block in %s\n' "$zprofile" >&2
  exit 2
fi

real_gh=$(find_real_gh || true)
if [[ -z "$real_gh" ]]; then
  printf 'octopool: authenticated real gh was not found at a stable path\n' >&2
  exit 2
fi

if ! /usr/bin/env -u GH_TOKEN -u GITHUB_TOKEN \
  "$octopool" login "$server" --gh-path "$real_gh" </dev/null >/dev/null
then
  printf 'octopool: login failed for %s using %s\n' "$server" "$real_gh" >&2
  exit 1
fi

install_exit=0
OCTOPOOL_GH_PATH="$real_gh" "$octopool" install-shim --shell zsh </dev/null >/dev/null || install_exit=$?
zsh_c=$(probe_gh -c || true)
zsh_lc=$(probe_gh -lc || true)

if is_octopool "$zsh_c" && ! is_octopool "$zsh_lc"; then
  write_login_block "$(dirname "$zsh_c")"
  OCTOPOOL_GH_PATH="$real_gh" "$octopool" install-shim --shell zsh </dev/null >/dev/null
elif ! is_octopool "$zsh_c" || ! is_octopool "$zsh_lc" || [[ $install_exit -ne 0 ]]; then
  printf 'octopool: install-shim failed without the macOS login PATH ordering signature\n' >&2
  exit 1
fi

audit
