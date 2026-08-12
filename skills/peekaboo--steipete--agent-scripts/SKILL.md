---
name: peekaboo
description: "macOS screen capture, accessibility inspection, and background-first app/window/UI automation with Peekaboo v4."
---

# Peekaboo

Use Peekaboo for native macOS capture, UI inspection, and automation. Prefer its
native app, window, Accessibility, and input commands over AppleScript or
`osascript` whenever Peekaboo exposes the operation.

## Binary

- Prefer `~/bin/peekaboo` when present; it is Peter's signed local release copy.
- Otherwise use `peekaboo` from `PATH`.
- Check the selected binary before relying on syntax or installed state.

```bash
PB="${PEEKABOO_BIN:-$HOME/bin/peekaboo}"
[ -x "$PB" ] || PB="$(command -v peekaboo)"
"$PB" --version
```

## Runtime host and permissions

- Launch `Peekaboo.app` without taking focus when a GUI Bridge host is needed:
  `open -gj -a Peekaboo`.
- The app owns its TCC grants and serves
  `~/Library/Application Support/Peekaboo/bridge.sock`. The reusable daemon has
  separate permissions and serves `daemon.sock`; `daemon start` is not an app
  launch.
- Normal runtime selection prefers a healthy reusable daemon, then the GUI
  host, before starting a daemon. Use `bridge status --verbose --json` to see
  the actual selection. When app-held TCC is required, pass
  `--bridge-socket "$HOME/Library/Application Support/Peekaboo/bridge.sock"`
  and verify `hostKind: gui` instead of assuming the app was selected.
- Check `permissions status --all-sources --json`. Grant Screen Recording,
  Accessibility, and Event Synthesizing to the process reported as the selected
  source, not merely to the invoking terminal.
- Prefer Bridge capture from SSH, LaunchAgent, Codex, and other background
  sessions. `--no-remote --capture-engine cg` is a local-debug override and can
  return wallpaper-only pixels outside the active Aqua session.
- Never run an unsigned or ad-hoc build against saved TCC or Keychain state.

## Background-first safety

- Keep the user's foreground app, keyboard focus, and physical cursor untouched
  by default. Supply an exact `--app`, `--pid`, `--window-id`, or fresh snapshot
  target and use Peekaboo's background delivery.
- Never add `--foreground` merely to make a command work speculatively. Add it
  only when the user authorized foreground interaction or the target demonstrably
  rejects background delivery.
- Shared-cursor and targetless global input must use explicit foreground mode.
  This includes `move`, `drag`, targetless/smooth scroll, and targetless keyboard
  input; `click --long-press` is foreground-only. Foreground mode can interrupt
  the user.
- Background typing, key chords, and paste need a resolvable app/PID and Event
  Synthesizing permission. Window selectors require foreground mode for these
  process-targeted keyboard operations.
- Do not click, type, paste, quit, or otherwise mutate UI unless the user asked
  or the target is a controlled test. Re-observe after mutations; never replay
  an indeterminate input blindly.

## v4 command names

- Inventory: `app list`, `window list`, and `screen list`; there is no top-level
  `list` command.
- Screenshots and UI inspection: `see --no-elements` for pixels, or
  `see --tree --no-screenshot` for AX-only text; do not use the removed `image`
  or `inspect-ui` CLI commands.
- Keyboard chords: `press`; do not use the removed `hotkey` command.
- Named Accessibility actions: `action`; do not use `perform-action`.
- Coordinate clicks: `click --at x,y`; do not use `--coords`.

## Common commands

```bash
"$PB" permissions status --all-sources --json
open -gj -a Peekaboo
"$PB" bridge status --verbose --json

"$PB" screen list --json
"$PB" app list --include-hidden --include-background --json
"$PB" window list --app Safari --json

# Screenshot only; observation does not activate the target app.
"$PB" see --no-elements --mode screen --path /tmp/screen.png --json

# Interactive map plus a directly accessible image artifact.
"$PB" see --app Safari --annotate --path /tmp/safari-see.png --json

# AX-only inspection, with no pixel capture or screenshot artifact.
"$PB" see --app Safari --tree --no-screenshot --json

# Use IDs and the snapshot returned by a fresh `see`.
"$PB" click --on "$ELEMENT_ID" --snapshot "$SNAPSHOT_ID" --json
"$PB" action AXPress --on "$ELEMENT_ID" --snapshot "$SNAPSHOT_ID" --json

# Process-targeted background keyboard delivery.
"$PB" type "text" --app TextEdit --json
"$PB" press cmd+shift+t --app Safari --json
"$PB" paste "text" --app TextEdit --json

"$PB" tools --json
"$PB" tools describe click --json
```

## Click coordinates safely

Screenshot pixels are not automatically click coordinates. `click --at` uses
logical points. With target flags, coordinates are relative to the resolved
window; without them they are global screen coordinates. Add `--global` to make
targeted coordinates use the global logical space. Use `screen list --json` for
display bounds and scale factors when converting Retina pixels.

A background coordinate click requires an explicit snapshot from a fresh
exact-window observation. First resolve the canonical window ID, then observe
that exact window and use both its window ID and returned snapshot ID:

```bash
"$PB" window list --app Safari --json
"$PB" see --app Safari --window-id 12345 --path /tmp/safari.png --json
"$PB" click --window-id 12345 --at 20,40 --snapshot "$SNAPSHOT_ID" --json
```

Peekaboo revalidates the captured PID, process generation, window ID, and bounds
before dispatch. If the exact receipt cannot be established, background input
must fail instead of guessing. Use `--foreground` only when visible shared-pointer
interaction is intentional. Background right/double click can be dispatched to
an exact route but remains effect-unverifiable; run a fresh `see` before retrying.

For element work, prefer IDs from a fresh `see` and pass the snapshot explicitly.
Queries and the implicit latest snapshot are convenient but less deterministic.
After an action changes UI, capture a new snapshot rather than reusing stale IDs.

## Workflow

1. Resolve `PB`, confirm its version, and launch the signed GUI host in the
   background when app-held TCC is needed.
2. Verify the selected Bridge host and compare permissions across sources.
3. Resolve the target with `app list` or `window list`; prefer PID/window ID over
   a broad name or title when cleanup or mutation must be exact.
4. Observe without focus theft: use `see --no-elements` for a screenshot,
   ordinary `see` for element IDs, or `see --tree --no-screenshot` for AX-only
   inspection. Pass `--path` when the caller needs the image file.
5. Interact in the background with an exact target and fresh snapshot. Prefer
   `action` or an element click over coordinate input.
6. Verify every mutation with a new `see` or a purpose-built read-only command.
7. Escalate to explicit `--foreground` only for authorized shared cursor/global
   input or a confirmed application limitation; never silently promote modes.
8. Use `capture live` for change-aware capture, `capture video` for video frame
   sampling, `tools describe <name>` for MCP schemas, and `<command> --help` for
   current CLI syntax.
9. Verify image artifacts with `sips -g pixelWidth -g pixelHeight <path>` or view
   them locally.

Source of truth: `~/Projects/peekaboo/docs/commands/` and the selected binary's
`--help` output.
