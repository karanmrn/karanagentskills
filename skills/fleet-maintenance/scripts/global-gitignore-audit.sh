#!/bin/bash

set -euo pipefail

usage() {
  printf 'usage: %s --host HOST_ID [--fleet INVENTORY] [--repair]\n' "$0" >&2
}

repair=false
fleet="$HOME/Projects/manager/fleet/inventory.json"
host_id=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repair)
      repair=true
      shift
      ;;
    --fleet)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      fleet="$2"
      shift 2
      ;;
    --host)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      host_id="$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$host_id" ]]; then
  usage
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  printf 'global-gitignore: git is unavailable\n' >&2
  exit 1
fi

node_bin=$(command -v node 2>/dev/null || true)
if [[ -z "$node_bin" ]]; then
  for candidate in /opt/homebrew/bin/node /usr/local/bin/node; do
    if [[ -x "$candidate" ]]; then
      node_bin="$candidate"
      break
    fi
  done
fi

if [[ -z "$node_bin" ]]; then
  printf 'global-gitignore: node is unavailable\n' >&2
  exit 1
fi

# JavaScript template literals below are intentionally protected from shell expansion.
# shellcheck disable=SC2016
patterns_text=$("$node_bin" -e '
  const fs = require("node:fs");
  const [fleetPath, hostId] = process.argv.slice(1);
  const fleet = JSON.parse(fs.readFileSync(fleetPath, "utf8"));
  const host = fleet.hosts?.[hostId];
  if (!host) throw new Error(`unknown fleet host: ${hostId}`);
  const profile = fleet.profiles?.[host.profile];
  if (!profile) throw new Error(`unknown profile for ${hostId}: ${host.profile}`);
  const patterns = profile.requirements?.git_global_ignore;
  if (!Array.isArray(patterns) || patterns.length === 0) {
    throw new Error(`missing git_global_ignore requirement for profile: ${host.profile}`);
  }
  const unique = [];
  for (const pattern of patterns) {
    if (typeof pattern !== "string" || pattern.length === 0 || /[\r\n]/.test(pattern)) {
      throw new Error(`invalid git_global_ignore pattern for profile: ${host.profile}`);
    }
    if (!unique.includes(pattern)) unique.push(pattern);
  }
  process.stdout.write(unique.join("\n"));
' "$fleet" "$host_id")

patterns=()
while IFS= read -r pattern; do
  [[ -n "$pattern" ]] && patterns+=("$pattern")
done <<< "$patterns_text"

canonical="$HOME/.config/git/ignore"
configured=$(git config --global --path --get core.excludesFile 2>/dev/null || true)

if [[ -n "$configured" && "$configured" != "$canonical" ]]; then
  printf 'global-gitignore: alternate excludes file requires review: %s\n' "$configured" >&2
  exit 1
fi

if [[ "$repair" == true ]]; then
  mkdir -p "$(dirname "$canonical")"
  touch "$canonical"

  for pattern in "${patterns[@]}"; do
    if ! grep -Fqx -- "$pattern" "$canonical"; then
      if [[ -s "$canonical" ]] && [[ $(tail -c 1 "$canonical" | wc -l | tr -d ' ') == 0 ]]; then
        printf '\n' >> "$canonical"
      fi
      printf '%s\n' "$pattern" >> "$canonical"
    fi
  done

  git config --global core.excludesFile "$canonical"
  configured=$(git config --global --path --get core.excludesFile)
fi

missing=()
for pattern in "${patterns[@]}"; do
  if [[ ! -f "$canonical" ]] || ! grep -Fqx -- "$pattern" "$canonical"; then
    missing+=("$pattern")
  fi
done

if [[ "$configured" != "$canonical" ]]; then
  printf 'global-gitignore: drift configured=%s expected=%s\n' "${configured:-default}" "$canonical" >&2
  exit 1
fi

if [[ ${#missing[@]} -gt 0 ]]; then
  {
    printf 'global-gitignore: missing'
    printf ' %s' "${missing[@]}"
    printf '\n'
  } >&2
  exit 1
fi

printf 'global-gitignore: current host=%s file=%s patterns=%s\n' "$host_id" "$canonical" "${#patterns[@]}"
