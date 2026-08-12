---
name: hopper-debugger
description: "Hopper debugging: macOS/iOS binaries, ObjC/Swift symbols, dyld, LLDB."
---

# Hopper Debugger

Goal: use Hopper through `mcporter` as a queryable disassembler, then combine the result with local source, LLDB, logs, and focused repros.

## Quick Start

Validate the MCP server:

```bash
MCPORTER_LIST_TIMEOUT=15000 timeout 20 mcporter list hopper --brief
```

List open Hopper documents:

```bash
MCPORTER_CALL_TIMEOUT=20000 timeout 30 mcporter call hopper.list_documents --output json
```

If no document is open, open the binary/framework in Hopper first:

```bash
open -a "Hopper Disassembler" /path/to/Binary
```

Hopper may show a first-open/import dialog. Let the user click the confirmation button, then retry the MCP call. Avoid parallel Hopper MCP calls; the server can close the transport or crash Hopper while import is still settling.

## Apple Frameworks

Prefer already extracted dyld-cache framework binaries when present:

```bash
/tmp/dsc-appkit/System/Library/Frameworks/AppKit.framework/Versions/C/AppKit
/tmp/dsc-appkit/System/Library/Frameworks/SwiftUI.framework/Versions/A/SwiftUI
```

Open one at a time when debugging SwiftUI/AppKit boundary issues:

```bash
open -a "Hopper Disassembler" /tmp/dsc-appkit/System/Library/Frameworks/AppKit.framework/Versions/C/AppKit
mcporter call hopper.list_documents --output json

open -a "Hopper Disassembler" /tmp/dsc-appkit/System/Library/Frameworks/SwiftUI.framework/Versions/A/SwiftUI
mcporter call hopper.list_documents --output json
```

Verify access:

```bash
mcporter call hopper.list_documents --output json
mcporter call hopper.current_document --output json
mcporter call hopper.search_strings pattern=SwiftUI --output json
mcporter call hopper.search_strings pattern=NSStatusItem --output json
```

Document names can start as `Untitled`; retry after Hopper finishes importing. Use `current_document`, symbol/string searches, and window title changes to identify AppKit vs SwiftUI.

## Query Workflow

1. Start from the local source path or runtime symbol you are trying to explain.
2. Search names/procedures/strings:

```bash
mcporter call hopper.search_procedures pattern='NSStatusBar' --output json
mcporter call hopper.search_name pattern='NSStatusBarButtonCell' --output json
mcporter call hopper.search_strings pattern='NSStatusItem' --output json
```

3. Inspect one small target at a time:

```bash
mcporter call hopper.procedure_info procedure='<symbol>' --output json
mcporter call hopper.procedure_assembly procedure='<symbol>' --output json
mcporter call hopper.procedure_pseudo_code procedure='<symbol>' --output json
mcporter call hopper.procedure_callers procedure='<symbol>' --output json
mcporter call hopper.procedure_callees procedure='<symbol>' --output json
mcporter call hopper.xrefs address=0x12345678 --output json
```

4. Summarize the relevant control flow; do not paste large decompilations.
5. Validate the hypothesis with LLDB/logging/repro before editing app code.

## Status Item / Menu Click Bugs

Useful AppKit/SwiftUI searches:

```bash
mcporter call hopper.search_strings pattern='NSStatusItem_Private_ForSwiftUI' --output json
mcporter call hopper.search_procedures pattern='popUpStatusBarMenu' --output json
mcporter call hopper.search_procedures pattern='trackMouse' --output json
mcporter call hopper.search_name pattern='NSStatusBarButtonCell' --output json
mcporter call hopper.search_name pattern='NSStatusItem' --output json
```

Symbols worth inspecting when menu bar clicks do nothing:

- `-[NSStatusBarButtonCell trackMouse:inRect:ofView:untilMouseUp:]`
- `-[NSStatusBarButtonCell _sendActionFrom:]`
- `-[NSStatusItem popUpStatusBarMenu:]`
- `-[NSApplication sendAction:to:from:]`
- SwiftUI status/menu symbols that reference `NSStatusItem_Private_ForSwiftUI`

Compare disassembly against runtime state:

```bash
pgrep -af "App.app/Contents/MacOS/App"
lldb /path/to/debug/Binary
```

For hardened signed apps, attach may fail without `get-task-allow`; launch the raw debug binary under LLDB when needed.

## Failure Handling

- Wrap Hopper calls with `timeout`; a modal/import or closed document can leave the transport stuck.
- Do not send concurrent Hopper MCP requests during import. If a query is expensive, wait for it to finish before starting another.
- If calls report `Connection closed`, check for a Hopper modal, then retry after confirmation.
- If Hopper crashes, reopen a single document, wait for import/analysis, and re-run `list_documents` before deeper searches.
- If mcporter is wedged, inspect processes before killing anything:

```bash
pgrep -af 'mcporter|HopperMCPServer|Hopper Disassembler'
```

- Prefer restarting the mcporter daemon over broad process kills:

```bash
mcporter daemon stop
mcporter daemon start
```
