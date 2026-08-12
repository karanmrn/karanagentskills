# op CLI examples (from op help)

## Sign in

- `op signin`
- `op signin --account <shorthand|signin-address|account-id|user-id>`

## Read

- `op read op://app-prod/db/password`
- `op read "op://app-prod/db/one-time password?attribute=otp"`
- `op read "op://app-prod/ssh key/private key?ssh-format=openssh"`
- `op read --out-file ./key.pem op://app-prod/server/ssh/key.pem`

## Run

- `export DB_PASSWORD="op://app-prod/db/password"`
- `op run --no-masking -- printenv DB_PASSWORD`
- `op run --env-file="./.env" -- printenv DB_PASSWORD`

## Inject

- `echo "db_password: {{ op://app-prod/db/password }}" | op inject`
- `op inject -i config.yml.tpl -o config.yml`

## Whoami / accounts

- `op whoami`
- `op account list`

## Peter account routing

- Always run these inside tmux.
- Default path: service account (`OP_SERVICE_ACCOUNT_TOKEN` env + `--vault Molty`). No `--account`, no `op signin` — either forces the desktop-app path and prompts Peter.
- `--account my.1password.com` only in a consented interactive/desktop flow.
- Do not use `my.1password.eu` / Titan unless requested.

## Item create/edit without printing secrets

`op item create` category values may be the human category name. For API tokens, use `"API Credential"`.

Default (service account, Molty, no prompts):

```bash
ITEM_TITLE="Service API Tokens"
FIELD_NAME="api_token"
EXPECTED_PREFIX=""
TOKEN="$(pbpaste)"
if [ -n "$EXPECTED_PREFIX" ]; then
  case "$TOKEN" in "$EXPECTED_PREFIX"*) ;; *) echo "clipboard value does not match expected prefix" >&2; exit 2;; esac
fi
OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op item create --vault Molty --category "API Credential" --title "$ITEM_TITLE" "$FIELD_NAME[password]=$TOKEN" >/dev/null
OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op item get "$ITEM_TITLE" --vault Molty --fields "label=$FIELD_NAME" >/dev/null
```

Personal account (explicit ask only, consented desktop flow):

```bash
ITEM_TITLE="Service API Tokens"
FIELD_NAME="app_token"
EXPECTED_PREFIX=""
TOKEN="$(pbpaste)"
if [ -n "$EXPECTED_PREFIX" ]; then
  case "$TOKEN" in "$EXPECTED_PREFIX"*) ;; *) echo "clipboard value does not match expected prefix" >&2; exit 2;; esac
fi
op item edit "$ITEM_TITLE" --account my.1password.com "$FIELD_NAME[password]=$TOKEN" >/dev/null
op item get "$ITEM_TITLE" --account my.1password.com --fields "label=$FIELD_NAME" >/dev/null
```
