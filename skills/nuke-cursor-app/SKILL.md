---
name: nuke-cursor-app
description: 'Safely quit and kill ALL Cursor IDE processes on the user''s MacBook to recover from the known renderer memory leak that makes Cursor lag. Manual-only — run ONLY when the user explicitly invokes it (/nuke-cursor-app, "nuke cursor"). Differentiator: kills the Cursor desktop app; cursor-cli sessions are unrelated.'
disable-model-invocation: true
---

# Nuke Cursor App

## Why this exists

Cursor (the AI IDE) is an Electron-based VS Code fork. It has a known,
Cursor-acknowledged memory leak: the renderer process accumulates tool-call
state (diffs, file contexts) during long agent sessions and never frees it,
especially in the Agents window. The UI gets laggy, then freezes. The only
reliable recovery is a full restart — that is what this skill does.

## How Cursor runs

One main process at `/Applications/Cursor.app/Contents/MacOS/Cursor` plus
helper processes (Renderer, GPU, extension host, network service, crashpad)
that all live under the `/Applications/Cursor.app` bundle path.

## Safety rules

- Match processes ONLY by the bundle path `/Applications/Cursor.app` —
  never by the bare word "cursor".
- Do NOT touch `CursorUIViewService` — despite the name it is a macOS
  system text-input service, not part of the Cursor app.
- Warn the user first if you have reason to think an important agent run is
  in flight; killing Cursor kills its local agent sessions.

## Procedure

```bash
# 1. See what is running (read-only)
ps -axo pid,rss,comm | grep "/Applications/Cursor.app" | grep -v grep

# 2. Graceful quit first — lets Cursor save session state
osascript -e 'tell application "Cursor" to quit' 2>/dev/null
sleep 3

# 3. Kill anything still alive under the bundle path
pkill -f "/Applications/Cursor.app" 2>/dev/null
sleep 1

# 4. Verify; force-kill leftovers by PID if needed
ps -axo pid,comm | grep "/Applications/Cursor.app" | grep -v grep
# if any remain:  kill -9 <pid> ...

# 5. Final check — must print nothing
ps -axo pid,comm | grep "/Applications/Cursor.app" | grep -v grep && echo "STILL RUNNING" || echo "all Cursor processes gone"
```

The graceful quit (step 2) often fails exactly when this skill is needed —
a leaked renderer blocks the main thread — which is why steps 3–4 exist.
Report the final check result to the user; never claim success without it.
