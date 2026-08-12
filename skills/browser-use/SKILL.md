---
name: browser-use
description: "Existing Chrome automation: Chrome plugin first; OpenClaw extension-backed mcporter fallback."
---

# Browser Use

Use this for browser tasks against the existing Chrome session.

Config repair details live in `mcporter-config.md`.

## Route

1. If the Codex `Chrome` or `Chrome [Internal]` plugin is callable in the current session, use its bundled Chrome-control skill.
2. Otherwise use the mcporter `chrome-devtools` route below.

Bundled or installed on disk does not mean available; the plugin must be callable in the active session. Both routes must use the user's existing Chrome profile.

For the mcporter fallback, use this target:

```bash
mcporter call chrome-devtools.<tool>
```

Most login-heavy sites fail in isolated profiles because fresh sessions trigger captcha, device checks, or missing SSO/extension state. Strongly prefer the existing Chrome profile for any website that needs login.

Never use `chrome-isolated`, Playwright, Puppeteer, the Codex in-app browser, AppleScript, `osascript`, GUI scripting, or macOS `open` for browser control unless the user explicitly asks for an isolated/new browser.

Screenshot/live UI bugs require this existing-Chrome path. `curl`, source
inspection, Worker smoke tests, or local Playwright are supporting proof only;
do not treat them as equivalent when the user showed a rendered browser problem
or the page may depend on login/profile state.

## Prompt-free OpenClaw relay

Current mcporter `main` can replace `chrome-devtools-mcp --autoConnect` with the
paired OpenClaw extension relay. This keeps the real Chrome profile while
avoiding Chrome's blocking **Allow remote debugging?** dialog.

Use this route when the OpenClaw checkout and extension are available:

The examples use an installed `openclaw` command. If it is absent, run the
same arguments as `pnpm -s openclaw ...` from `~/Projects/openclaw`.

1. Resolve and verify the unpacked extension directory before presenting it:

   ```bash
   extension_dir="$(openclaw browser extension path)"
   if [ ! -f "$extension_dir/manifest.json" ]; then
     extension_dir="$HOME/Projects/openclaw/extensions/browser/chrome-extension"
   fi
   test -f "$extension_dir/manifest.json"
   printf '%s\n' "$extension_dir"
   ```

   A source checkout may report an unstaged `dist/extensions/...` path. Never
   hand that path to the user unless `manifest.json` exists. The verified source
   fallback is `~/Projects/openclaw/extensions/browser/chrome-extension`.

2. In the real Chrome profile, open `chrome://extensions`, enable Developer
   mode, choose **Load unpacked**, and select the verified directory. Use
   Peekaboo for UI automation or give the user the exact verified path.

3. Start or reach the OpenClaw gateway/browser service, then generate and paste
   the pairing string with `openclaw browser extension pair`. Pairing strings
   contain a host-local secret: never print one in chat or tool output. For
   automated local pairing, extract `pairingString` from `--json` directly into
   `pbcopy`, paste only into the confirmed OpenClaw popup, and clear the
   clipboard immediately afterward.

4. Run `openclaw browser status --browser-profile chrome --json` to activate
   the browser sidecar when necessary. The extension popup must say
   **Connected to OpenClaw**. Share one controlled tab; success moves it into
   the orange **OpenClaw** tab group.

5. Confirm the mcporter definition is still the normal auto-connect form:

   ```bash
   mcporter config get chrome-devtools
   # Transport should include: chrome-devtools-mcp ... --autoConnect
   ```

   Do not manually replace the server definition with a token-bearing command.
   mcporter reads `~/.openclaw/credentials/browser-extension-relay.secret`,
   probes the relay, and rewrites the child arguments in memory.

6. Use a mcporter build that contains the relay rewrite. When testing current
   source rather than the installed binary:

   ```bash
   cd "$HOME/Projects/mcporter"
   pnpm install
   pnpm build
   node dist/cli.js --version
   ```

   Call that `node dist/cli.js` entry point for the proof; an older global
   `mcporter` binary does not prove current `main`.

The default relay URL is `http://127.0.0.1:18799`. A custom gateway port can
produce a different relay port; read `relayPort` from
`openclaw browser extension pair --json` and pass only the non-secret URL:

```bash
relay_port=18799 # replace with the reported relayPort when non-default
MCPORTER_CHROME_DEVTOOLS_RELAY_URL="http://127.0.0.1:$relay_port" \
  mcporter call chrome-devtools.list_pages --args '{}' --output text
```

If OpenClaw uses a custom `OPENCLAW_STATE_DIR`, pass the same variable to
mcporter so it can find the relay secret. Never display the secret itself.

### Relay proof

After sharing a controlled tab, prove read and write access through the normal
`--autoConnect` definition:

```bash
mcporter call chrome-devtools.list_pages --args '{}' --output text
mcporter call chrome-devtools.navigate_page \
  --args '{"url":"https://example.com/?mcporter-relay-proof=1"}' --output text
mcporter call chrome-devtools.evaluate_script \
  --args '{"function":"() => ({title: document.title, href: location.href})"}' \
  --output text
```

Success requires all of the following:

- `list_pages` shows the explicitly shared real-profile tab, not an isolated
  blank Chrome.
- navigation and evaluation return the proof URL from that tab.
- Chrome does not show the blocking **Allow remote debugging?** dialog.
- Chrome may show the dismissible **"OpenClaw" started debugging this browser**
  banner with a **Cancel** button. That banner is expected; Cancel revokes the
  tab share and is not the MCP attach alert.

If the blocking remote-debugging dialog appears while the extension is paired,
treat the relay rewrite as failed. Check the mcporter binary, relay URL, shared
tab, secret location, and relay reachability before clicking anything. Do not
count a fallback `--autoConnect` attachment as success for this flow.

## Check MCP

The attach-alert recovery below is only for the direct/legacy `--autoConnect`
path when the extension relay is unavailable. During an OpenClaw relay proof,
do not click **Allow remote debugging?**; its appearance means the rewrite did
not apply.

```bash
mcporter list chrome-devtools --schema
mcporter call chrome-devtools.list_pages --args '{}' --output text
```

`list_pages` must show the user's real open tabs. If it shows a blank/default isolated Chrome, stop and say reattach failed.

If the call appears to hang while Chrome shows an auth/attach/update prompt, handle the attach alert before falling back. Prefer Peekaboo to press an explicit Chrome `Allow` button when visible; otherwise wait for the human. Do not restart daemons or kill MCP processes just because the first output is slow.

Tested attach-prompt recovery:

```bash
PB="${PEEKABOO_BIN:-$HOME/bin/peekaboo}"
[ -x "$PB" ] || PB="$(command -v peekaboo)"
"$PB" permissions status --json
"$PB" see --app frontmost --path /tmp/chrome-attach.png --json --annotate
# If the UI shows Chrome "Allow remote debugging?", click only the visible Allow button.
"$PB" click --coords <allow_x>,<allow_y> --json
mcporter call chrome-devtools.list_pages --args '{}' --output text
```

Use coordinates from the current Peekaboo snapshot, not stale notes. Success means `list_pages` returns the user's real Chrome tabs.

Attach-alert rule: when the current snapshot clearly shows Chrome asking to
allow DevTools/MCP/browser automation attachment, click the visible `Allow`
button once, then rerun `list_pages`. If the button is not visible or the prompt
is ambiguous, stop and ask; do not silently switch to Playwright/Puppeteer.

If `list_pages` fails with `DevToolsActivePort`, ask the user to restart Chrome or the DevTools bridge, then retry once:

```bash
mcporter daemon restart
mcporter call chrome-devtools.list_pages --args '{}' --output text
```

If it still fails, stop and say Chrome DevTools MCP is unavailable. Do not use AppleScript.

Avoid noisy recovery loops. Repeated MCP/browser restarts can trigger
reconnect/login prompts and alerts. Try once, then pause and choose a quieter
path.

## Typical Flow

```bash
# pick the page id from list_pages
mcporter call chrome-devtools.select_page --args '{"pageId":9}' --output text

# inspect page
mcporter call chrome-devtools.take_snapshot --args '{}' --output text

# navigate selected page
mcporter call chrome-devtools.navigate_page --args '{"url":"https://example.com"}' --output text

# click an element uid from the latest snapshot
mcporter call chrome-devtools.click --args '{"uid":"1_38","includeSnapshot":true}' --output text

# type/fill
mcporter call chrome-devtools.fill --args '{"uid":"1_13","value":"text","includeSnapshot":true}' --output text

# run JS, keep secrets out of output
mcporter call chrome-devtools.evaluate_script --args '{"function":"() => document.title"}' --output json
```

Use `take_snapshot` before actions and use current `uid` values only. Avoid `take_screenshot` unless visual layout matters.

## Live UI Proof

For screenshot regressions, deployed dashboard checks, or anything where the
rendered browser is the bug:

```bash
mcporter call chrome-devtools.list_pages --args '{}' --output text
mcporter call chrome-devtools.select_page --args '{"pageId":9}' --output text
mcporter call chrome-devtools.navigate_page --args '{"url":"https://example.com"}' --output text
mcporter call chrome-devtools.take_snapshot --args '{}' --output text
mcporter call chrome-devtools.evaluate_script --args '{"function":"() => document.body.innerText"}' --output json
```

Use the existing logged-in/profile-bearing tab set. If browser automation is
unavailable, report that as a verification gap instead of substituting isolated
browser tooling.

## Secret Handling

Never print tokens/passwords from page DOM, network logs, or inputs. For token checks, return shape only: present/absent, length, status code, account/org name.
