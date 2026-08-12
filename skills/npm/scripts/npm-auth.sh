# npm-auth.sh: sourced 1Password -> npm auth helpers shared by the npm skill
# scripts. Desktop fallback is explicit-only (--account); the default path is
# the Molty service-account item and requires OP_SERVICE_ACCOUNT_TOKEN.
# Never prints secret values.

# Callers set: VAULT ITEM ACCOUNT REGISTRY WORK NPMRC SCRIPT_DIR.

redact() {
  sed -E 's/(npm_[A-Za-z0-9_]+)/npm_REDACTED/g; s/[0-9]{6}/OTP_REDACTED/g'
}

current_otp() {
  op_item_get --otp 2>/dev/null | tr -d '[:space:]' || true
}

# Run registry operations away from caller-local npm config. The token stays in
# the temporary npmrc instead of entering argv or the lifecycle environment.
npm_authenticated() {
  (cd "$WORK" && NPM_CONFIG_USERCONFIG="$NPMRC" npm --registry "$REGISTRY" "$@")
}

npm_auth_whoami() {
  npm_authenticated whoami
}

# Reads the item JSON exactly once and defines op_item_get for OTP refreshes.
# env -u keeps the service token out of desktop op calls.
resolve_op_item() {
  if [ -n "$ACCOUNT" ]; then
    env -u OP_SERVICE_ACCOUNT_TOKEN op signin --account "$ACCOUNT" >/dev/null
    ITEM_JSON="$(env -u OP_SERVICE_ACCOUNT_TOKEN op item get "$ITEM" --account "$ACCOUNT" --format json)"
    op_item_get() {
      env -u OP_SERVICE_ACCOUNT_TOKEN op item get "$ITEM" --account "$ACCOUNT" "$@"
    }
    op_item_edit_json() {
      env -u OP_SERVICE_ACCOUNT_TOKEN op item edit "$ITEM" --account "$ACCOUNT" >/dev/null
    }
    echo "1Password access: desktop ($ACCOUNT)"
  else
    if [ -z "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]; then
      echo "OP_SERVICE_ACCOUNT_TOKEN is required; pass --account for the desktop fallback" >&2
      return 2
    fi
    ITEM_JSON="$(op item get "$ITEM" --vault "$VAULT" --format json)"
    op_item_get() {
      op item get "$ITEM" --vault "$VAULT" "$@"
    }
    op_item_edit_json() {
      op item edit "$ITEM" --vault "$VAULT" >/dev/null
    }
    echo "1Password access: service account"
  fi
  echo "op auth ok; reading npm item once: $ITEM"
}

# Persist a newly created registry session through an all-JSON pipeline. The
# token stays out of argv, logs, and extra files; a failed cache write does not
# invalidate the already-authenticated command.
persist_registry_token() {
  if ! printf '%s' "$ITEM_JSON" |
    node "$SCRIPT_DIR/npm-auth-cache.mjs" update "$NPMRC" "$REGISTRY" |
    op_item_edit_json; then
    echo "warning: npm auth works, but registry session cache update failed" >&2
    return 1
  fi
  if ! op_item_get --format json |
    node "$SCRIPT_DIR/npm-auth-cache.mjs" verify "$NPMRC" "$REGISTRY"; then
    echo "warning: npm auth works, but registry session cache verification failed" >&2
    return 1
  fi
  echo "npm auth: cached registry session in 1Password"
}

# Writes an authenticated NPMRC. Reuses the stored registry_token session when
# it still passes whoami; otherwise runs npm-auth-login.mjs (hardened field
# selection) with a fresh six-digit OTP. Sets NPM_OTP and LOGIN_USED_OTP so
# callers know whether the current TOTP window was consumed by login.
ensure_npm_auth() {
  local token login_log="$WORK/npm-login.log"
  LOGIN_USED_OTP=0
  NPM_OTP=""
  token="$(printf '%s' "$ITEM_JSON" | jq -r '[.fields[]? | select((.label // "") == "registry_token") | .value // empty][0] // empty')"
  if [ -n "$token" ]; then
    local auth_host="${REGISTRY#*://}"
    auth_host="${auth_host%%/*}"
    printf '//%s/:_authToken=%s\n' "$auth_host" "$token" >"$NPMRC"
    if npm_auth_whoami >/dev/null 2>&1; then
      echo "npm auth: reused stored registry session"
      return 0
    fi
  fi
  NPM_OTP="$(current_otp)"
  case "$NPM_OTP" in
    [0-9][0-9][0-9][0-9][0-9][0-9]) ;;
    *)
      echo "$ITEM has no usable six-digit OTP field" >&2
      return 3
      ;;
  esac
  printf '%s' "$ITEM_JSON" |
    NPM_OTP="$NPM_OTP" NPMRC="$NPMRC" REGISTRY="$REGISTRY" \
    node "$SCRIPT_DIR/npm-auth-login.mjs" >"$login_log" 2>&1 || {
    echo "npm registry login failed" >&2
    redact <"$login_log" >&2
    return 3
  }
  redact <"$login_log"
  LOGIN_USED_OTP=1
  persist_registry_token || true
}

# npm publish rejects the TOTP already consumed by loginCouch; wait out the
# window when login just used it, then return a code usable for NPM_CONFIG_OTP.
fresh_command_otp() {
  local otp
  otp="$(current_otp)"
  if [ "$LOGIN_USED_OTP" -eq 1 ] && [ "$otp" = "$NPM_OTP" ]; then
    local attempt
    for ((attempt = 0; attempt < 20; attempt++)); do
      sleep 2
      otp="$(current_otp)"
      if [ "$otp" != "$NPM_OTP" ]; then
        break
      fi
    done
  fi
  printf '%s' "$otp"
}
