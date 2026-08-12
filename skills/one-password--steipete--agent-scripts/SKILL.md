---
name: one-password
description: "REQUIRED before ANY `op` command or whenever a task needs an API key, token, password, credential, or secret (OPENAI_API_KEY, ANTHROPIC_API_KEY, deploy tokens, live-test keys). Prompt-free 1Password service-account reads; wrong invocations spam macOS dialogs."
metadata: {"clawdbot":{"emoji":"🔐","requires":{"bins":["op","tmux"]}}}
---

# 1Password CLI

## Install (stable path only — never brew)

`op` lives at `~/bin/op` on all of Peter's Macs, with a compat symlink `/opt/homebrew/bin/op -> ~/bin/op`. Do NOT install/upgrade via the Homebrew cask: its versioned Caskroom path gives `op` a new macOS TCC identity on every upgrade, which re-fires the App Data Protection dialog at Peter. To update: download the official signed pkg from https://app-updates.agilebits.com/product_history/CLI2, `pkgutil --check-signature` (AgileBits 2BUA8C4S2C) + `pkgutil --expand-full`, then `install -m 755 <payload>/op ~/bin/op`. The stable path prevents path/version identity churn; it does not make the macOS grant durable across `op` processes.

Follow the official CLI get-started steps for anything else. Don't guess install commands.

## References

- Official docs: https://developer.1password.com/docs/cli/get-started/
- Official app-integration toggle: https://developer.1password.com/docs/cli/app-integration/
- Apple `SystemPolicyAppData`: https://developer.apple.com/documentation/xcode/resetting-access-to-protected-resources-in-macos
- Known repeated-dialog bug: https://github.com/1Password/shell-plugins/issues/586
- `references/get-started.md` (install + app integration + sign-in flow)
- `references/cli-examples.md` (real `op` examples, including safe item create/edit patterns)

## Access paths (strict order)

**1. Service account — default, zero prompts.** `OP_SERVICE_ACCOUNT_TOKEN` is exported from `~/.profile` (Codex-managed block), scoped to the `Molty` vault (read+write). Every service-account command must set both `OP_LOAD_DESKTOP_APP_SETTINGS=false` and `OP_BIOMETRIC_UNLOCK_ENABLED=false`. The first prevents the settings-file read; the second is 1Password's official app-integration override.

- Required command shape: `OP_LOAD_DESKTOP_APP_SETTINGS=false OP_BIOMETRIC_UNLOCK_ENABLED=false OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op item get "<item>" --vault Molty ...`.
- `--vault Molty` is required; omitting it fails even with a valid token.
- NEVER `op signin` and NEVER `--account` on this path. Either one routes through the desktop app and throws an Authorize prompt at Peter. `--account` + token = interactive path, always wrong.
- Older alias `MOLTY_OP_SERVICE_ACCOUNT_TOKEN` = fallback only; may be stale.
- Token missing/expired or item read fails: report the exact error and ask. Do NOT silently fall back to the desktop app.

**2. Desktop app — explicit consent only.** For items genuinely outside Molty (personal `Private` vault, `OpenClaw-Core`). No automatic fallback.

- STOP and ask in chat first: item name + why needed. Wait for yes.
- On a non-primary, VM, or headless host, route this flow to the active physical workstation in the matching personal or work-managed environment; see "Remote routing - desktop path only".
- After consent: one task window in the shared `op-work` session (see below). Inside that window, first `unset OP_SERVICE_ACCOUNT_TOKEN MOLTY_OP_SERVICE_ACCOUNT_TOKEN`; an exported service token overrides `--account my.1password.com` and silently confines reads to Molty. Then run `op signin --account my.1password.com` once, and batch every interactive read of the whole task into that same window and one `op run`/`op inject` invocation when practical. TTY reuse limits 1Password's Authorize prompts; it does not make the separate macOS App Data grant persist across new `op` PIDs.
- No nameplate/sag pre-alerts. Audible page (`sag`) only if Peter approved the unlock in chat and the 1Password prompt then sits unanswered.

## Known Molty items (skip discovery)

Exact titles; go straight to the service-account read. No enumeration needed.

| Purpose | Item title | Field |
|---|---|---|
| OpenAI (OpenClaw/i18n jobs) | `AI API Key - OpenAI - OPENAI_API_KEY - OpenClaw` | `OPENAI_API_KEY` |
| OpenAI (serviceable access) | `AI API Key - OpenAI - OPENAI_API_KEY - Serviceable Access` | `OPENAI_API_KEY` |
| Anthropic (live tests) | `AI API Key - Anthropic - ANTHROPIC_API_KEY - OpenClaw Live Tests` | `ANTHROPIC_API_KEY` |
| Anthropic (clawdbot) | `AI API Key - Anthropic - ANTHROPIC_API_KEY - Clawdbot` | `ANTHROPIC_API_KEY` |
| Gemini | `AI API Key - Google Gemini - GEMINI_API_KEY - steipete-m5` | `GEMINI_API_KEY` |
| App Store Connect release | `API Key - App Store Connect - Personal - Release` | `private_key_p8`, `key_id`, `issuer_id` |
| npm release automation | `npm Registry - steipete - Release Automation` | see `$npm` |
| Cloudflare (OpenClaw services) | `OpenClaw Services Cloudflare API Token` | `credential` |
| Sparkle signing | `Nameplate Sparkle EdDSA` | `private key` |
| Octopool | `Octopool Proxy Secret`, `Octopool Admin Token (OpenClaw account)` | `credential` |
| Crabyard deploy | `Cloudflare OpenClaw Crabyard Deploy Token` | `credential` |
| Hetzner (crabyard) | `API Key - Hetzner Cloud - OpenClaw - crabyard-ssh-gateway` | `credential` |
| Anthropic (Peekaboo) | `Anthropic API Key - Peekaboo Live Test` | `credential` |
| ClickClack deploy | `Cloudflare ClickClack deploy token`, `Cloudflare ClickClack R2 uploads` | `credential` |
| Barnacle | `GitHub Token Barnacle` | `credential` |
| macOS Developer ID signing (OpenClaw Foundation) | `Release - macOS Developer ID p12 - OpenClaw Foundation` | `p12_base64`, `p12_password` |
| macOS Developer ID signing (personal) | `Release - macOS Developer ID p12 - Peter Steinberger` | attached `DeveloperID-p12` file, `certificate_password` |
| Release-tag SSH signing key | `Release - Git tag SSH signing key - all repos` | `private_key`, `public_key` (fp `SHA256:WmI9lVtd…`) |
| Homebrew tap dispatch token | `Release - Homebrew tap dispatch token - openclaw/homebrew-tap` | `token` |
| Apple notarization (Apple ID fallback) | `Release - Apple ID app-specific password - notarization` | `apple_id`, `team_id`, `app_specific_password` |

ClickClack/Barnacle Molty items are agent copies; canonical items live in the shared `OpenClaw` vault — on rotation update both.

## Release credentials: one tag finds them all

Every signing/notarization/tap credential is tagged `release-credential` and
named `Release - <what> - <scope>` (unified 2026-08-09). Do not hunt by guessing
titles — list them:

```bash
op item list --vault Molty --tags release-credential
```

Start with `Release - 00 INDEX (read me first)`: its note maps each GitHub
Actions secret name to the exact item and field, and records the repair recipe.
Keep that index current when adding or rotating a release credential.

## Release credentials: GitHub secrets are PER-REPO, not org-level

Verified 2026-08-09: the `openclaw` org has 21 org-level secrets and **none** of
them are the release/signing ones. `MACOS_SIGNING_P12`,
`MACOS_SIGNING_P12_PASSWORD`, `ASC_KEY_ID`, `ASC_ISSUER_ID`,
`ASC_PRIVATE_KEY_P8`, and `HOMEBREW_TAP_TOKEN` are set **per repository**. A
release failing at signing or the Homebrew handoff is therefore usually a
missing/misnamed secret on that one repo, not a broken org secret.

Known trap: `openclaw/gogcli` carried legacy names
(`MACOS_SIGNING_CERT_BASE64`, `MACOS_SIGNING_CERT_PASSWORD`,
`MACOS_CODESIGN_IDENTITY`) while the shared `openclaw/release-workflows`
reusable workflow reads the `MACOS_SIGNING_P12*` / `ASC_*` names, so the signer
import silently received empty values. Compare a broken repo's secret names
against a known-good one (`openclaw/wacrawl`) before debugging anything else.

The values for all of these live in Molty (table above), so a repo can be
repaired non-interactively: read the field, `gh secret set <NAME> --repo <r>
--body -`, never printing the value.

Read those fields via the JSON + exact-label method in "Exact field reads"
below — NOT `--fields label=<f>`. Measured 2026-08-09 on the Foundation p12
item: `--fields label=p12_base64` returned 65 characters while the correct
value is 4432. Items with several concealed fields silently resolve the wrong
one, which would push a truncated secret into CI.

Outside Molty by design (desktop path, consent first): `OpenClaw Developer ID Release Keychain` (`OpenClaw-Core` vault), npm interactive login+OTP (`Private/Npmjs`), personal SSH/signing keys. Twilio has no API credential stored anywhere — only a console login (Private); minting one needs the console.

## Remote routing - desktop path only

Applies to path 2 (interactive/desktop) flows only; path 1 service-account reads always run locally, no routing.

- Identify the current host first (`hostname; id -un`), then load the remote-Mac skill matching that environment. Keep personal and work-managed Mac topologies separate; never infer identity from a stale IP or a generic "Mac Studio" name.
- If the current host is Peter's active physical workstation with a usable 1Password GUI session, keep the entire consented desktop flow local. In the personal environment, the default active workstation is `steipete-studio-sf`; use `steipete-mbp` only when Peter says he is using it or live context confirms it is the active approval surface. In the work-managed environment, default to its verified Studio; use its matching MacBook only when Peter identifies it as the active approval surface or live context confirms it.
- On a VM, headless host, or other non-active workstation, check the matching topology skill's documented Tailscale command and select only an active Studio or MacBook from that same environment. Verify the configured SSH alias with `ssh -o ConnectTimeout=5 -o RequestTTY=no -o RemoteCommand=none <workstation-alias> 'hostname; id -un'` before routing the whole interactive flow into that workstation's OWN shared `op-work` tmux session.
- Consent rule unchanged: still ask in chat first (item + why). Routing changes WHERE the prompt appears, not whether to ask.
- Only the needed field values cross the SSH channel; same no-print, shape-check-only rules apply on both ends. Kill the remote task window at task end.
- If the selected workstation is offline or SSH times out, use another same-environment physical workstation only when Peter or live context confirms it is the active approval surface. Local fallback requires a usable GUI session and explicit verification that the current same-environment host is Peter's active workstation; otherwise, including on any VM/headless host, report what was tried and STOP.

## Workflow

1. Check OS + shell.
2. Verify CLI present inside tmux: `op --version`.
3. REQUIRED: use the shared `op-work` session; open exactly one task window in it for the whole secret task; kill that window when the task is done.
4. Known/expected Molty item → service-account read directly (path 1). Verify with `OP_LOAD_DESKTOP_APP_SETTINGS=false OP_BIOMETRIC_UNLOCK_ENABLED=false OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op whoami </dev/null >/dev/null 2>&1; echo op_rc:$?` if unsure the token works.
5. Item unknown → check the table above → vault-scoped metadata search in Molty (service account, safe) → only then the desktop consent ask (path 2).
6. If a command fails, reuse the same window with `tmux send-keys`; do not open a second window or session just to retry.
7. Before a personal interactive flow, unset `OP_SERVICE_ACCOUNT_TOKEN` and `MOLTY_OP_SERVICE_ACCOUNT_TOKEN` inside the task window. Then use `--account my.1password.com` by default; never `my.1password.eu` / Titan unless explicitly asked.

## Shared Op Tmux Session — one session, one window per task

ALL `op` work on this machine — every skill, every agent, every task — shares ONE tmux server (`clawdbot-op.sock`) and ONE session (`op-work`). Never mint another socket name, tmux server, or session for secret work: every extra session fires an alert at Peter and rots into a zombie holding secrets in its shell env. Sibling skills (`$npm`, `$release-mac-app`, ad-hoc flows) use this same session and differ only in window name.

Per task: create ONE window in `op-work`, named after the task; target it by window id; kill it when the task ends.

```bash
SOCKET_DIR="${CLAWDBOT_TMUX_SOCKET_DIR:-${TMPDIR:-/tmp}/clawdbot-tmux-sockets}"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/clawdbot-op.sock"
SESSION="op-work"

# 'shell' is a permanent keeper window: never send work to it, never kill it.
tmux -S "$SOCKET" has-session -t "$SESSION" 2>/dev/null ||
  tmux -S "$SOCKET" new -d -s "$SESSION" -n shell
WIN="$(tmux -S "$SOCKET" new-window -d -t "$SESSION" -n "<task-slug>" -P -F '#{window_id}')"
tmux -S "$SOCKET" send-keys -t "$WIN" -- 'OP_LOAD_DESKTOP_APP_SETTINGS=false OP_BIOMETRIC_UNLOCK_ENABLED=false OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op whoami </dev/null >/dev/null 2>&1; echo op_rc:$?' Enter
tmux -S "$SOCKET" capture-pane -p -J -t "$WIN" -S -200
```

Service-account `op` has three required defenses: skip loading desktop settings with `OP_LOAD_DESKTOP_APP_SETTINGS=false`, force app integration off with `OP_BIOMETRIC_UNLOCK_ENABLED=false`, and keep stdin/output off the pane TTY by redirecting or capturing it. The biometric override alone is insufficient in `op` 2.35: its enforced-policy startup still reads the 1Password app's group-container settings. macOS then fires the App Data Protection dialog ("op would like to access data from other apps") and blocks in `open()` until answered. Only a consented desktop flow (path 2) may omit these overrides and run `op` directly on the TTY. `OP_LOAD_DESKTOP_APP_SETTINGS` is recognized by the signed 2.35 binary but absent from public environment-variable docs; after an `op` update, repeat the prompt-free `whoami` plus TCC-log proof.

### Repeated macOS App Data dialogs

Observed on macOS 26 with `op` 2.35: TCC records `SystemPolicyAppData` approval as session/PID-scoped (`auth_value=5` plus the approving PID). A later `op` PID can prompt again despite clicking Allow. Each executable path (`~/bin/op`, a Homebrew Caskroom version, a temporary copy) is also a separate TCC client. Stable path reduces identities; it cannot cure PID-scoped approval.

Live proof on 2026-07-16: service-token `op whoami` with only `OP_BIOMETRIC_UNLOCK_ENABLED=false` still prompted and hung; adding `OP_LOAD_DESKTOP_APP_SETTINGS=false` returned success with zero new `SystemPolicyAppData` prompts.

Repeated sheets usually mean concurrent/retrying `op` commands or stale `op daemon` processes. Stop the retry loop; inspect `pgrep -x op` plus the shared socket's panes without printing process arguments. Re-run service-account work with the required override. For desktop work, keep one consented task window and minimize new `op` processes. Do not keep clicking Allow expecting a permanent grant.

- Reuse `$WIN` for every command, retry, and follow-up of the task. A quoting, item-name, or command failure means send a corrected command into the same window, never a new window or session.
- Task end (success or failure): `tmux -S "$SOCKET" kill-window -t "$WIN"` — exported secrets die with the window's shell. The keeper window keeps `op-work` alive for the next task.
- No `op signin` in bootstrap. Sign-in belongs only to a consented desktop flow (path 2), inside the task window.
- Stale task windows from crashed agents may be killed when their pane shows an idle prompt; never kill a window with a running command, and never kill `shell`.

## Service-Specific Workflows

- Keep service-specific auth details in the owning skill.
- For npm registry/package work, use `$npm`; it documents the Molty service-account item, non-interactive auth wrapper, and package reservation helper.
- This skill owns only the generic 1Password rules: tmux-only `op`, targeted reads, the shared `op-work` session with per-task windows, no broad enumeration, no secret output.

## Known working secret-write pattern

New secrets default to the `Molty` vault via the service account (no prompts). Personal-account writes only on explicit ask. Use your task window in the shared `op-work` session (bootstrap above); write the exact secret task to a temp script, send it into the window; do not create a second window or session for retries.

```bash
cat > /tmp/op-store-secret.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
set +x
export OP_LOAD_DESKTOP_APP_SETTINGS=false
export OP_BIOMETRIC_UNLOCK_ENABLED=false
exec </dev/null 2>/dev/null
VAULT="Molty"
ITEM_TITLE="Service API Tokens"
FIELD_NAME="api_token"
EXPECTED_PREFIX=""
NOTES="Created via tmux-safe op workflow"
TOKEN="$(pbpaste)"
if [ -n "$EXPECTED_PREFIX" ]; then
  case "$TOKEN" in "$EXPECTED_PREFIX"*) ;; *) echo "clipboard value does not match expected prefix" >&2; exit 2;; esac
fi
OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op item create --vault "$VAULT" --category "API Credential" --title "$ITEM_TITLE" "$FIELD_NAME[password]=$TOKEN" "notesPlain=$NOTES" >/dev/null
OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op item get "$ITEM_TITLE" --vault "$VAULT" --fields "label=$FIELD_NAME" >/dev/null
echo "stored and verified secret field without printing it"
SCRIPT
chmod 700 /tmp/op-store-secret.sh
tmux -S "$SOCKET" send-keys -t "$WIN" -- "bash /tmp/op-store-secret.sh; rm -f /tmp/op-store-secret.sh" C-m
```

The `op` category string is human-readable and case-sensitive in this CLI build; use `"API Credential"`, not `api_credential`.

## Exact field reads

For a known item, verify the field shape before using it live: length, expected prefix, newline count, never value. `op --field NAME` and `--fields label=NAME` can return the wrong concealed field when an item has duplicate/legacy credential fields. If shape is wrong, read the known item as JSON and extract the exact label.

```bash
cat > /tmp/op-read-field.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
set +x
ITEM_TITLE="Known API Credential Item"
FIELD_LABEL="api_token"
VAULT="Molty"
value="$(
  OP_LOAD_DESKTOP_APP_SETTINGS=false \
    OP_BIOMETRIC_UNLOCK_ENABLED=false \
    OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" \
    op item get "$ITEM_TITLE" --vault "$VAULT" --format json </dev/null |
    FIELD_LABEL="$FIELD_LABEL" node -e 'let s=""; process.stdin.on("data",d=>s+=d); process.stdin.on("end",()=>{const item=JSON.parse(s); const f=(item.fields||[]).find(x=>x.label===process.env.FIELD_LABEL); if(!f?.value) process.exit(2); process.stdout.write(f.value);})'
)"
echo "field_len:${#value}"
case "$value" in sk-*) echo "field_prefix:sk" ;; *) echo "field_prefix:other" ;; esac
echo "field_has_newline:$(printf %s "$value" | wc -l | tr -d ' ')"
SCRIPT
chmod 700 /tmp/op-read-field.sh
tmux -S "$SOCKET" send-keys -t "$WIN" -- "bash /tmp/op-read-field.sh; rm -f /tmp/op-read-field.sh" C-m
```

Keep JSON extraction scoped to the known item and vault. Do not enumerate vaults/items to discover candidates.

## Explicit item search

Only use this when the user explicitly asks to search, gives a screenshot/listing, or the exact title guess failed. Stay vault-scoped (Molty, service account) and metadata-only; print candidate titles/ids/categories/vault names, never fields or values. Prefer exact visible strings from screenshots first: vault name, item title, and field label.

```bash
cat > /tmp/op-find-item.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
set +x
VAULT="Molty"
QUERY="minimax"
OP_LOAD_DESKTOP_APP_SETTINGS=false \
  OP_BIOMETRIC_UNLOCK_ENABLED=false \
  OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" \
  op item list --vault "$VAULT" --format json </dev/null |
  QUERY="$QUERY" VAULT="$VAULT" node -e '
let s=""; process.stdin.on("data",d=>s+=d); process.stdin.on("end",()=>{
  const q=process.env.QUERY.toLowerCase();
  const vault=process.env.VAULT;
  const items=JSON.parse(s).filter(x => [
    x.title, x.id, x.category, ...(x.tags || [])
  ].filter(Boolean).join("\n").toLowerCase().includes(q));
  for (const item of items.slice(0, 10)) {
    console.log(`title:${item.title} id:${item.id} category:${item.category || ""} vault:${vault}`);
  }
  console.log(`matches:${items.length}`);
})'
SCRIPT
chmod 700 /tmp/op-find-item.sh
tmux -S "$SOCKET" send-keys -t "$WIN" -- "bash /tmp/op-find-item.sh; rm -f /tmp/op-find-item.sh" C-m
```

After choosing a candidate, switch back to exact item/field JSON extraction and shape-only validation. No Molty match → desktop consent ask (path 2), never a silent personal-vault read.

## Redacted debugging

Interactive-flow debugging only (consented desktop path). Keep the whole pipeline inside the same task window. Inspect status and output length, never secret values.

```bash
cat > /tmp/op-debug.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
set +x
SIGNIN_OUTPUT="$(op signin --account my.1password.com 2>&1 || true)"
echo "signin output bytes: ${#SIGNIN_OUTPUT}"
op account list 2>&1 | sed -E "s/(xox[baprs]-)[A-Za-z0-9-]+/\\1REDACTED/g; s/(xapp-)[A-Za-z0-9-]+/\\1REDACTED/g"
SCRIPT
chmod 700 /tmp/op-debug.sh
tmux -S "$SOCKET" send-keys -t "$WIN" -- "bash /tmp/op-debug.sh; rm -f /tmp/op-debug.sh" C-m
```

## Guardrails

- Never paste secrets into logs, chat, or code.
- Path-1 `op` commands always set `OP_LOAD_DESKTOP_APP_SETTINGS=false` and `OP_BIOMETRIC_UNLOCK_ENABLED=false`, pass the service token explicitly, and keep stdin plus secret-bearing stdout off the pane TTY.
- Every `op` run can spawn a background `op daemon` (cache flags do not prevent it in 2.35). Stale daemons can re-trigger the dialog. Only when no `op` task is active, `pkill -f 'op daemon'` is safe; never broadly kill active `op` commands.
- An App Data Allow/Don't Allow choice may be PID-scoped and repeat on the next `op` process. Stop the source command and fix its invocation instead of approving a prompt loop.
- Never `eval "$(op completion zsh)"` unguarded in rc files; it runs `op` on every shell start and is a known dialog-spam source.
- Prefer `op run` / `op inject` over writing secrets to disk.
- Desktop app path only after explicit chat consent; the 1Password unlock prompt then handles the actual authorization — no extra chat round trip at prompt time.
- If sign-in without app integration is needed, use `op account add`.
- If a command returns "account is not signed in" in a consented interactive flow, re-run `op signin` inside tmux and let Peter authorize in the app.
- `sag` only when a consented unlock prompt sits unanswered; never as a pre-alert.
- Do not run `op` outside tmux; stop and ask if tmux is unavailable.
