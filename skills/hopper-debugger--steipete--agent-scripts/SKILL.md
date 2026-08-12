---
name: hopper-debugger
description: "Hopper debugging: macOS/iOS binaries, ObjC/Swift symbols, dyld, LLDB."
---

# Hopper Debugger

Use Hopper through `mcporter` as a queryable disassembler, then combine the result with local source, LLDB, logs, and focused repros.

## Setup (one time)

Hopper 6.0+ **ships its own MCP server**. Do not install a third-party one.

```bash
mcporter config add hopper --scope home \
  --command "/Applications/Hopper Disassembler.app/Contents/MacOS/HopperMCPServer" \
  --description "Hopper Disassembler built-in MCP server (stdio)"
```

`--scope home` is required. The default scope is **project**, which writes `config/mcporter.json` into whatever repo you are standing in (untracked repo dirt, lost with the worktree).

Verify:

```bash
MCPORTER_LIST_TIMEOUT=25000 timeout 40 mcporter list hopper --brief
```

## Call convention — the one that bites

**Always pass arguments with `--args`. Never `--params`.** `mcporter` accepts an unknown `--params` flag *silently*, drops the payload, and the call arrives with no arguments. Hopper then answers `Document not found.`, which reads like a licensing or state problem and is not.

```bash
# WRONG — arguments silently dropped, fails with "Document not found."
mcporter call hopper.list_segments --params '{"document":"AppKit"}'

# RIGHT
mcporter call hopper.list_segments --args '{"document":"AppKit"}'
```

Related: the server does **not** fall back to the current document. A call with no `document` argument fails even when `current_document` returns a valid name. Pass `document` on every document-scoped call.

Document names come from `list_documents` and carry **no `.hop` extension** (window title `AppKit.hop` → document name `AppKit`).

If a call still fails, drive the server directly over stdio to see the raw JSON-RPC — this bypasses mcporter entirely and isolates who is at fault:

```bash
"/Applications/Hopper Disassembler.app/Contents/MacOS/HopperMCPServer" <<'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"p","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_documents","arguments":{}}}
EOF
```

## Licensing — do not misdiagnose

Hopper 6.x still uses the bundle id and preferences domain **`com.cryptic-apps.hopper-web-4`**. The absence of a `hopper-web-6` domain does **not** mean the app is unlicensed. Check the real state in the About panel (`Hopper Disassembler > About Hopper Disassembler`); it prints the licensee, order id, and update-plan expiry. There is no Register/License menu item in Hopper 6.

Peter's license: order `HOP140213-7833-95831`, updates through 2027-05-17. The `.hopperLicense` file is in 1Password (Molty vault, document item "Hopper Disassembler License (HOP140213-7833-95831)"); load `$one-password` to retrieve it. Opening a `.hopperLicense` file with Hopper does **not** register it — Hopper disassembles it as a document.

## Opening documents

```bash
open -a "Hopper Disassembler" /path/to/Binary
```

Small binaries import with no dialog. Large frameworks take minutes; poll instead of sleeping:

```bash
until mcporter call hopper.list_documents --output json 2>/dev/null | grep -qi "appkit"; do sleep 10; done
```

Dismiss any first-open dialog with an Accessibility press, never a synthetic click — clicking moves Peter's physical pointer:

```bash
osascript -e 'tell application "System Events" to tell process "Hopper Disassembler" to perform action "AXPress" of (button 1 of window 1)'
```

## Apple frameworks

Apple frameworks live in the dyld shared cache, not on disk. Two routes:

1. **Prefer Peter's pre-made exports** at `~/Library/CloudStorage/Dropbox/Hopper/` — `.hop` documents plus `.m` pseudo-code dumps for AppKit, AccessibilityKit, and others. Grepping the `.m` is often faster than any MCP round-trip (`AppKit.m` is 244 MB).
   **Check provenance before trusting them for version work.** These are snapshots; as of 2026-08 they predate macOS 26.6 and 27.0, and their class/method inventory differs from both live runtimes. Good for structure, unreliable for OS-version diffing.
2. Extract fresh with `/usr/lib/dsc_extractor.bundle` (present on macOS; extracts all dylibs, multi-GB, slow).

## Query workflow

1. Start from the local source path or runtime symbol you are trying to explain.
2. Find the symbol, then inspect one small target at a time:

```bash
mcporter call hopper.search_procedures --args '{"document":"AppKit","pattern":"addCursorRect"}' --output json
mcporter call hopper.procedure_pseudo_code --args '{"document":"AppKit","procedure":"0x185475b2c"}' --output json
```

`procedure` accepts a symbol name or a hex address. Other useful tools: `list_documents`, `current_document`, `set_current_document`, `list_segments`, `list_procedures`, `list_strings`, `search_strings`, `procedure_info`, `procedure_address`, `current_procedure`.

3. Summarize the relevant control flow; do not paste large decompilations.
4. Validate the hypothesis with LLDB/logging/repro before editing app code.

## Pairing with runtime evidence

Disassembly tells you which store a value lands in; only the runtime tells you whether it got there. Read the pseudo-code first to learn *which* ivar/collection the API actually writes to, then read that exact store at runtime with `class_copyIvarList` + `object_getIvar` + `perform`. Instrumenting the wrong (legacy) path is the classic time sink: on modern AppKit, `-[NSWindow _addCursorRect:cursor:forView:]` is dead code, and cursor rects are stored in `_NSTrackingAreaAKViewHelper`'s `cursorAreas` set.

Always run the same probe on a second machine at a different OS version before concluding "regression". Several no-op probes look identical on a known-good OS and a known-broken one; a control run is what tells you the probe is measuring nothing. See `$remote-mac` for the fleet and `codexbar-ui-verification-quirks` memory for the cursor-measurement harness.

## Failure handling

- Wrap Hopper calls with `timeout`; a modal or import can leave the transport stuck.
- Do not send concurrent Hopper MCP requests during import.
- `Connection closed` usually means Hopper is not running or is showing a modal. Check windows via System Events, then retry.
- `Document not found.` almost always means missing arguments (see `--args` above), not a broken document.
- If mcporter is wedged, prefer restarting its daemon over broad process kills:

```bash
mcporter daemon stop && mcporter daemon start
```
