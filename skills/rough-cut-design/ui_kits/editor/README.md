# Rough Cut — Editor UI kit

A high-fidelity recreation of the **single product surface** Rough Cut ships:
the transcript-based editor.

The brief from the user was to **completely rethink** the existing prototype.
The codebase confirmed which functions the UI has to expose; the visuals here
were redesigned from scratch against the brand foundations
(`/colors_and_type.css`, `/README.md`).

## What's here

```
index.html        ← interactive demo (open this)
demo.jsx          ← the app shell; layout
components.jsx    ← Topbar · Transcript · PlayerSurface (with FootagesStrip) · AgentDock
primitives.jsx    ← Button · Pill · Tag · Hairline · KeyHint
icons.jsx         ← Lucide-style icon set, 1.5px stroke, square caps
data.js           ← a sample project: 3 footages, ~13 passages, an agent thread
```

## Screens covered

A Rough Cut browser session is always pointed at **one project** (you open
one via `rough-cut-axi open <video-files…>` or `rough-cut-axi open
<project-dir>` from the shell). So the UI is just one screen:

1. **Editor** — the manuscript, the player, the timeline, the agent dock.
   No project switcher, no home view; the CLI is the way you navigate
   between projects.

The preview is live in the editor mock.
There is no separate preview-render control or render modal in this UI kit.

## Components covered

- **`Topbar`** — wordmark, a quiet **last-saved** status (e.g. `● saved 2s
  ago`), and an **End session** button on the right (closes the local
  server — same as `rough-cut-axi end`). The project title isn't here
  because it's already large and italic in the manuscript directly below.
- **`Transcript`** — the manuscript page. Passages have `keep` / `skip` /
  `active` states. Speaker labels and
  timecodes in the left margin. **Footages are separated by a horizontal
  divider** (§ marker + footage label). Click a passage to toggle status.
- **`PlayerSurface`** — 16:9 video preview frame with a custom scrubber, and
  the `FootagesStrip` directly beneath it. The strip _is_ the timeline — a
  horizontal row of footage cards in cut order. Each card shows thumbnail,
  position, kept-ratio, kept duration. Active footage gets a vermillion rail.
- **`AgentDock`** — agent presence indicator, chat thread, composer.
  Agent messages are quoted with a vermillion / ultramarine rail.
- Primitives: `Button`, `Pill`, `Tag`, `Hairline`, `KeyHint`, `Icon`.

There is **no separate "media bin"** and **no separate "bottom timeline"** —
both concepts collapse into `FootagesStrip`.

## What's _not_ here

- Real video playback. The player uses a still-frame placeholder. (The CLI
  binary doesn't ship with sample footage.)
- Real ElevenLabs calls. The transcript data is canned.
- Real ffmpeg renders. Final export is product behavior outside this mock.
- Drag-and-drop reordering. Visual affordance only.

These are deliberate — the UI kit is for designing, not for running the
product. If you need a real cut, use the CLI.

## Notes on copy

Every string here was written against the tone rules in
[`../../README.md`](../../README.md#content-fundamentals). Sentence case, no
emoji, no exclamation marks, status pills read like `key: value`, dock presence
can read like `agent · listening`, time is monospaced, and the agent is just
**`agent`** (lowercase, no proper name). Don't drift.
