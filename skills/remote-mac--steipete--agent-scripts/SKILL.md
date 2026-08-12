---
name: remote-mac
description: "Remote Macs: MacBooks, Mac Studios, hosted claw Macs, Tailscale, SSH, and OpenClaw."
---

# Remote Mac

Use when the user says `MacBook`, `Mac Studio`, `clawmac`, `foundationclaw`, `foundationmac`, `megaclaw`, `miniclaw`, `Molty`, Tailscale, or asks to run/check something on one of Peter's Macs.

## Peter's Topology

- Primary workstation for interactive approvals and day-to-day work: Peter's SF Mac Studio, local/Tailscale name `steipete-studio-sf`. Peter's MacBook Pro (`steipete-mbp`) is the portable/fallback workstation; do not route prompts there merely because it is online.
- London workhorse: Mac Studio, Tailscale `peters-mac-studio-1`, usually best reached as `steipete@steipete-macstudio.local` when on its LAN.
- San Francisco machines: `mac-studio-sf` (`100.72.210.5`), `clawstudio` (`100.86.255.34`; formerly `mac-studio-sf2`, renamed 2026-08-05 — the old userspace node `mac-studio-sf2` (`100.70.201.26`) is retired and shows as a stale offline entry in `tailscale status`; never treat it as a separate or offline machine), and the separately owned `mac-mini-sf` (local/Tailscale name `steipete-mini-sf`, `100.78.75.51`; SSH `steipete@100.78.75.51`). Always prefer live Tailscale addresses over these cached values. The Mini uses classic key-only OpenSSH over the tailnet TCP 22 grant because GUI Tailscale builds cannot host Tailscale SSH. Its own key is installed on both SF Studios, MegaClaw, and MiniClaw; see `manager/docs/fleet-setup.md` for live proof and offline/provider-blocked directions. Do not confuse it with FoundationClaw.
- Personal cloud OpenClaw: `clawmac` (Peter may typo/say `crabmac`), MacStadium service `100121942`, Tailscale/SSH `steipete@clawmac`, gateway via LaunchAgent `ai.openclaw.gateway`, loopback `127.0.0.1:18789`, Telegram connected. The current 2026-08-01 provider network outage is tracked by Atlanta remote hands on tickets #11481/#11484; one hard reboot restored SSH only briefly, so do not repeat power cycles.
- Network split:
  - `corporate`: Peter's work-managed environment. Treat Mac Studio as the main remote Mac to configure and inspect there.
  - `personal`: Peter's personal LAN / personal cloud environment, including `clawmac`.
- Network boundary: `clawmac` and the personal LAN are unreachable from Peter's corporate Mac. Never use `clawmac` as a relay or LAN vantage from there.
- Molty's former Mac Studio gateway is retired and must remain disabled; real Molty runs separately on Hetzner. Do not use the old Mac Studio runtime as a healthy-state expectation.
- `megaclaw`: Virtualized.gg product 22 (Mac Studio M4 Max, Phoenix), the active alternate Mac worker. Tailscale/SSH `steipete@megaclaw`. No OpenClaw gateway by design — the personal claw runs on `clawmac`; do not configure or start one on `megaclaw`.
- `miniclaw`: Virtualized.gg product 24 (Mac mini M4 Pro, Phoenix), public SSH `steipete@131.143.4.3`. Live 2026-08-01 state regressed: the privileged Homebrew daemon owns stale duplicate `miniclaw-1` and cannot reach coordination, while canonical `miniclaw` is unusable. Use public SSH until the stored personal admin credential is explicitly authorized for a privileged repair; do not claim the canonical tailnet path is healthy from provider SSH alone.
- `foundationclaw`: MacStadium service 100124960, M2.L in Atlanta, public address recorded in `computers.yaml`. Provider SSH verified a Mac14,12 M2 Pro Mac mini, hardware UUID, and the `administrator` admin account; its canonical local hostname is `foundationclaw`. Signed Tailscale and Jump Desktop Connect v10 are installed, but the previously working provider credential stopped authenticating and a data-preserving reset is pending on ticket #11386 before Tailscale enrollment and first-run GUI permissions can continue. Do not merge it with the separate SF Mini.

Non-Mac fleet nodes (full detail in `computers.yaml`):

- `gorillaclaw`: personal Ubuntu Linux node at GorillaServers (Los Angeles), Tailscale `100.93.99.79`; SSH user `steipete`.
- `steipetesurface`: Peter's personal Windows Surface, Tailscale `100.118.219.64`, SSH user `steip`. Corporate Windows laptop `CPC-steip-11ENO` is separate and work-managed.

Not Peter's Macs (do not configure/brand as his):

- `crabhammer`: Scaleway M4-XL given to vince; on Peter's tailnet + billing but provisioned for vince (no SSH access). Listed under `handed_off:` in `computers.yaml`.

Manager repo source of truth (canonical inventory of all nodes, Mac and non-Mac):

- `/Users/steipete/Projects/manager/computers.yaml`
- `/Users/steipete/Projects/manager/agents.yaml`

## Discovery

1. Start with live `tailscale status --json`; match hostname/DNS name and use the node's current IP. Manager-cached Tailscale IPs may be stale.
2. For rented Macs, reconcile the live identity with the provider service/product record in `computers.yaml`. Provider-active does not mean fleet-configured, and a public IP alone is not enough to merge identities.
3. For `clawmac`, if MacStadium reports Active while the public IP, SSH/VNC, and Tailscale all fail, treat it as a provider network/hardware incident. Check the current incident note in `computers.yaml`, update the existing ticket, and request console, NIC-link, and switch-port inspection. Do not repeat hard reboots or authorize reimage, erase, reinstall, storage replacement, credential resets, or other data-affecting work without Peter's approval.
4. In the `corporate` environment, default to Mac Studio for remote configuration work. Reach it through its live Tailscale node. MagicDNS may be disabled; use the current `TailscaleIPs[0]` directly. Do not try `clawmac`, mDNS, or personal-LAN discovery from there.
5. In the `personal` environment, if Tailscale is down or SSH times out, try LAN discovery:

```bash
dns-sd -B _ssh._tcp local
arp -a
```

6. Try mDNS names such as `HOST.local` only when on the same LAN.
7. If Mac Studio's live Tailscale node is offline from the `corporate` environment, stop: it must wake or reconnect before SSH or Screen Sharing diagnosis can continue.

## SSH Rules

Use non-interactive SSH by default:

```bash
ssh -o RequestTTY=no -o RemoteCommand=none HOST 'COMMAND'
```

The local SSH alias `mac-studio` auto-attaches tmux. For one-shot commands, either use `steipete@steipete-macstudio.local` or override both options above.

For long-running or interactive remote work, use tmux on the remote host and keep the session name obvious.

## OpenClaw Checks

Use login shells on remote Macs so Homebrew and pnpm are on PATH:

```bash
ssh -o RequestTTY=no -o RemoteCommand=none steipete@steipete-macstudio.local \
  'zsh -lc "openclaw gateway status --json; openclaw channels status --json"'
```

Mac Studio / Molty healthy shape:

- `tmux list-sessions` includes `openclaw-gateway-watch-main`.
- `ps axww` includes `pnpm gateway:watch --benchmark`.
- `lsof -nP -iTCP:18789 -sTCP:LISTEN` shows a listener on `*:18789`.
- `openclaw channels status --json` shows Discord `Molty`, Slack, and Telegram connected.

clawmac healthy shape:

- `launchctl list` includes `ai.openclaw.gateway`.
- `lsof -nP -iTCP:18789 -sTCP:LISTEN` shows loopback listeners.
- `openclaw channels status --json` shows Telegram connected.

## Codex Automations

- Codex cron automations are host-local scheduler state, not generic cloud jobs.
- In the `corporate` environment, configure or mirror those automations on Mac Studio unless Peter says otherwise.
- Treat `~/.codex/automations/<automation-id>/automation.toml` on the target host as the source of truth for the scheduled job definition on that machine.
- If the goal is to move a cron automation from Peter's current corporate machine to Mac Studio, do the machine work on Mac Studio:
  - ensure the intended repo checkout exists there
  - sync the required repo-local policy files
  - create or update the matching `~/.codex/automations/...` entry on Mac Studio
  - disable or pause the old corporate-host copy if Peter wants only one runner
- Do not assume Codex app thread handoff moves cron scheduler ownership; thread movement and cron ownership are separate.

## clawmac GUI Access

- If `computers.yaml` records a provider network outage and public SSH/VNC plus Tailscale are all unreachable, GUI access is unavailable too. Continue through the existing MacStadium remote-hands ticket; do not power-cycle the host again.
- Prefer direct clawmac automation over Tailscale/SSH first: `open -a "Google Chrome"`, AppleScript, Chrome DOM JavaScript, and remote Peekaboo clicks.
- For `gog` OAuth on clawmac, keep the browser on clawmac. Start `gog auth add` in remote tmux, open the printed URL on clawmac Chrome, click consent with AppleScript/DOM automation, then verify with `zsh -lc 'gog auth list --check --json --no-input'`.
- If `GOG_KEYRING_PASSWORD` is exported by the remote shell environment, use the matching login shell for checks and tmux prompt feeding, and never print the value.
- If SSH/cron hits GUI-only prompts that direct automation cannot handle, use local Peekaboo through Jump Desktop's `clawmac` window as fallback.
- Find it with `peekaboo list windows --app "Jump Desktop" --json`; capture by `--window-title clawmac` or the reported `--window-id`.
- Clicks use local global coordinates through the Jump Desktop window; verify with a raw window screenshot before clicking.
- Chrome cookie/keychain issues: `security` may prompt for `Chrome Safe Storage`; Peter must enter the login keychain password, then click `Always Allow`.
- After approval, verify over SSH with `/Users/steipete/Projects/bird/bird check` and `/Users/steipete/.openclaw/bin/bird-gui check`.

## Live Testing Policy (OpenClaw)

- Default for live tests on any of Peter's Macs: session-owned dev gateway — isolated `OPENCLAW_STATE_DIR` scratch dir + free port. Never bind 18789 while a real gateway runs; never `launchctl kickstart/bootout/bootstrap` or `openclaw gateway stop/restart` a service this session did not start.
- clawmac = PRODUCTION. Any restart/stop, config/state write under `~/.openclaw`, or live test against its gateway needs explicit per-task approval from Peter in chat. One approval = one task, never standing.
- Any shared Mac Studio gateway or dev-watch session is semi-production: same approval rule; never stop a tmux session this task did not start.
- Tunnel footgun (megaclaw AND Peter's MacBook Pro): `127.0.0.1:18789` on those hosts is an SSH tunnel into clawmac — "localhost" tests there hit production. Same approval rule applies. Neither host runs a local gateway service.
- DB/state for testing or migration rehearsal: production copies need explicit per-task approval naming the destination and handling. Work only on the approved copy; writing back or migrating production in place needs separate approval.
- Heavier cross-machine/OS live E2E routes through `$crabbox`, not Peter's personal gateways.

## Safety

- Do not assume host identity from a stale IP; verify hostname/user when possible.
- Do not print secrets from remote files or shells.
- If a host is unavailable after Tailscale + LAN fallback, say what was tried.
- For OpenClaw Gateway on Peter's machines, follow repo docs/AGENTS; do not install/start/stop services unless asked.
