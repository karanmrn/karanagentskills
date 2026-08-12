#!/bin/bash

set -euo pipefail

script_dir=$(cd "$(dirname "$0")" && pwd -P)
profile="$script_dir/fleet-profile.mjs"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/fleet-profile-test.XXXXXX")
cleanup() {
  local cleanup_exit_code=$?
  trap - EXIT
  case "$scratch" in
    "${TMPDIR:-/tmp}"/fleet-profile-test.*) rm -rf "$scratch" ;;
    *) printf 'refusing unexpected temporary path: %s\n' "$scratch" >&2 ;;
  esac
  exit "$cleanup_exit_code"
}
trap cleanup EXIT

cat >"$scratch/valid.json" <<'JSON'
{
  "profiles": {
    "full": {
      "requirements": {
        "claude_attribution": "none",
        "agent_clis": "authenticated",
        "github_cache": "octopool",
        "window_title_icons": true,
        "xcode_simulator_hygiene": "no-outdated"
      }
    },
    "worker": {
      "requirements": {
        "claude_attribution": "none",
        "agent_clis": "authenticated",
        "github_cache": "octopool",
        "window_title_icons": true,
        "xcode_simulator_hygiene": "no-outdated"
      }
    }
  },
  "hosts": {}
}
JSON

node "$profile" validate --fleet "$scratch/valid.json" >"$scratch/output.json"
grep -q '"valid": true' "$scratch/output.json"

node -e '
  const fs = require("node:fs");
  const source = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
  delete source.profiles.full.requirements.github_cache;
  source.profiles.worker.requirements.github_cache = "direct";
  fs.writeFileSync(process.argv[2], JSON.stringify(source));
' "$scratch/valid.json" "$scratch/invalid.json"

if node "$profile" validate --fleet "$scratch/invalid.json" >"$scratch/output.json"; then
  printf 'expected invalid GitHub cache requirements to fail validation\n' >&2
  exit 1
fi
grep -q 'full: github_cache must be octopool' "$scratch/output.json"
grep -q 'worker: github_cache must be octopool' "$scratch/output.json"

printf 'fleet-profile tests: ok\n'
