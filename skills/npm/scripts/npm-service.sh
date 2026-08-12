#!/usr/bin/env bash
set -euo pipefail
set +x
umask 077

usage() {
  cat <<'USAGE'
Usage:
  npm-service.sh [--vault VAULT] [--item ITEM] [--account ACCOUNT] -- <npm args...>

Runs one authenticated npm registry command with credentials from 1Password.
Commands run from an isolated temporary directory so caller-local npm config
cannot override auth. Use publish-package.sh for publishing a local package.
Defaults to the Molty service-account item. --account opts into an interactive
desktop-vault fallback.

Defaults:
  vault:    Molty
  item:     npm Registry - steipete - Release Automation
  registry: https://registry.npmjs.org/
USAGE
}

VAULT="${NPM_OP_VAULT:-Molty}"
ITEM="${NPM_OP_ITEM:-npm Registry - steipete - Release Automation}"
ITEM_EXPLICIT=0
if [ -n "${NPM_OP_ITEM:-}" ]; then
  ITEM_EXPLICIT=1
fi
ACCOUNT=""
REGISTRY="${NPM_REGISTRY:-https://registry.npmjs.org/}"
ARGS=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --vault)
      VAULT="${2:?missing vault}"
      shift 2
      ;;
    --item)
      ITEM="${2:?missing item}"
      ITEM_EXPLICIT=1
      shift 2
      ;;
    --account)
      ACCOUNT="${2:?missing account}"
      shift 2
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    --)
      shift
      ARGS=("$@")
      break
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

# Desktop fallback keeps the legacy item name unless one was named explicitly.
if [ -n "$ACCOUNT" ] && [ "$ITEM_EXPLICIT" -eq 0 ]; then
  ITEM="npmjs"
fi

if [ "${#ARGS[@]}" -eq 0 ]; then
  usage >&2
  exit 2
fi
if [ -z "${TMUX:-}" ]; then
  echo "refusing to run: 1Password commands require a persistent tmux session" >&2
  exit 2
fi
for bin in op jq node npm; do
  command -v "$bin" >/dev/null 2>&1 || {
    echo "missing required binary: $bin" >&2
    exit 2
  }
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d /tmp/npm-service.XXXXXX)"
NPMRC="$WORK/npmrc"
cleanup() {
  rm -rf "$WORK"
  unset ITEM_JSON NPM_OTP COMMAND_OTP
}
trap cleanup EXIT

# shellcheck source=npm-auth.sh
source "$SCRIPT_DIR/npm-auth.sh"

resolve_op_item
ensure_npm_auth
unset ITEM_JSON

who="$(npm_auth_whoami 2>"$WORK/npm-whoami.log" || true)"
if [ -z "$who" ]; then
  echo "npm auth check failed" >&2
  redact <"$WORK/npm-whoami.log" >&2
  exit 4
fi
echo "npm auth ok as $who"

COMMAND_OTP="$(fresh_command_otp)"
if [[ "$COMMAND_OTP" =~ ^[0-9]{6}$ ]]; then
  NPM_CONFIG_OTP="$COMMAND_OTP" npm_authenticated "${ARGS[@]}"
elif [ "$LOGIN_USED_OTP" -eq 1 ]; then
  echo "could not obtain a fresh npm OTP after registry login" >&2
  exit 5
else
  npm_authenticated "${ARGS[@]}"
fi
