---
name: nextgen-slides
description: >-
  Create polished, self-contained HTML slide decks OR motion-graphics videos, and
  iterate on them live in a browser visualizer with a side panel. Use when the user
  wants to build a presentation, slide deck, or talk as HTML, wants an animated
  HTML "video" (kinetic typography / explainer / promo), or wants to open one in a
  preview where they can point at elements, type change requests to the agent, and
  edit the HTML directly. Triggers: "make slides", "build a deck", "HTML
  presentation", "make an HTML video", "animated explainer", "open the slides so I
  can review them", "let me edit the slides visually".
---

# nextgen-slides

Build a single self-contained HTML deck, then open it in the **visualizer** — a
local browser tool with a side panel where the user targets an element, types a
task, and the agent picks it up and edits the deck live.

## Files in this skill
- `references/outline-template.html` — a plain **white content canvas** for the
  outline phase (content first, no style yet).
- `references/stage.css` — the full-bleed responsive base rules + type scale.
- `references/deck-template.html` — a working styled starter deck.
- `references/style-presets.md` — committed visual styles to draw from.
- `references/animation-patterns.md` — motion guidance.
- `references/motion-explainer.html` — a **video** reference (motion-graphics
  explainer) built on the timeline engine; `references/bold-signal-video.html` —
  a stat-driven hype-reel reference. See **Building videos** below.
- `visualizer/bin/slides-viz.js` — the CLI that runs the live editor + feedback loop.

Read `outline-template.html` before the outline phase; read `stage.css` +
`style-presets.md` before applying a style. For a video, read
`references/motion-explainer.html` first — it *is* the engine + authoring model.

---

## The deck contract (non-negotiable)
Every deck is ONE self-contained `.html` file, inline CSS/JS, **zero external
runtime deps** (fonts via `<link>` are fine).

**The deck is a self-scaling fixed 1920×1080 stage.** Slides live inside
`.viewport > .stage`; the deck's own JS sets `--vizscale` so the stage scales
uniformly to fit whatever shows it (browser, editor, projector). The whole slide
is always visible; a thin letterbox appears only when the container isn't 16:9.
This means it renders **identically everywhere** — standalone file, editor, and
Preview — because the scaling is baked into the deck.

Size type with **container-query units against the stage, not `vw`/`vh`**:
`cqw`/`cqh` (1cqw = 19.2px, 1cqh = 10.8px). Design as if the canvas is 1920×1080.
`.stage` sets `container-type: size` so `cqw`/`cqh` resolve to the fixed design
width — that's what keeps sizes stable regardless of window size.

Structure the visualizer depends on:
- Each slide is an element with class **`.slide`** that fills the viewport.
- The currently shown slide additionally has **`.active`**.
- Slides toggle via `visibility`/`opacity`, **never `display:none`**.
- Expose **`window.goToSlide(index)`** (0-based) so the panel can navigate.
- A live **`#counter`** element is filled by JS as `current / total` — the page
  count is computed, never hand-numbered.

`references/deck-template.html` already satisfies all of this — start from it.
Use `references/stage.css` for the base rules and the recommended type scale.

---

## Workflow — content first, style later

Four stages, in order:
1. **Content** — nail the words on a plain white canvas (no style at all).
2. **Reference slide** — once content is settled, style *one* slide, iterate on
   it live, and get explicit confirmation of the look.
3. **Propagate** — only then roll that locked style across the whole deck.
4. **Iterate** — propagate is **not** the finish line. Once the deck is styled,
   stay in the live loop and refine it *with* the user — polish, fixes, content
   tweaks — until they close the editor. This is where most of the work happens.

Never jump ahead: no styling until content is settled, and no full-deck styling
until the reference slide is confirmed. And don't treat propagate as "done" —
the deck isn't finished, it's *ready to iterate on*.

### Phase 1 — Interview (before touching files)
Understand what to make. In one turn ask: purpose (pitch / teach / conf /
internal), audience, the angle/argument, and rough length. Use a structured
question for the crisp parts; keep it short. Don't ask about visuals yet.

### Phase 2 — Open the outline editor (white canvas)
Turn the interview into a **content outline** and open it for the user to edit:
1. Scaffold the file. `launch` on a non-existent path auto-creates it from the
   outline template (page-swap JS + a live `current / total` counter baked in);
   or scaffold explicitly first:
   ```bash
   node <skill>/visualizer/bin/slides-viz.js new deck.html          # outline (default)
   ```
2. Populate it: one `.slide` per section, each with a `.slidelabel`, a heading,
   and the points to include (use `.hint` italics for "what could go here"
   prompts the user replaces). Match the count/structure to the interview.
   **Never hand-number slides — the counter is computed in JS**, so adding or
   removing a `.slide` just works.
3. Launch the editor (auto-scaffolds if you skipped step 1):
   ```bash
   node <skill>/visualizer/bin/slides-viz.js launch deck.html
   ```
4. Tell the user: this is the plain content canvas — **double-click any text to
   edit it in place**, use ‹ / › (or arrows) to move between slides, and
   single-click → comment to ask you to draft/restructure something. **Say "done"
   in chat when the content is ready.**
5. **Immediately start the poll loop (Phase 3) — do not ask whether to begin
   polling.** An open editor with no poller is a dead editor: the user's comments
   would pile up unheard. Launching the editor and starting to poll are one
   inseparable action.

### Phase 3 — Collaborate on content (live loop)
Whenever the editor is open, you **must** be in the poll loop — start it the
moment you launch, without asking. Listen and help with wording/structure:
```bash
node <skill>/visualizer/bin/slides-viz.js poll deck.html   # long-polls until they send
```
Each item prints its `slide` + `target` selector + `message`. Apply edits to
`deck.html` (it live-reloads), then **poll again immediately** — re-arming the
poll is also what flips the panel's per-item badge from *Working* to *Done ✓*, so
the user can see each request land. The user edits text inline; you handle
drafting, reordering, splitting/merging slides. Re-read `deck.html` before
editing — the user may have changed it. **Stay in this loop until the user says
they're done, or the poll reports `SESSION ENDED by user`** (they clicked **Done
& Close** in the editor) — then stop polling and move on. (Still white/unstyled
the whole time.)

### Phase 4 — Style interview
Once the user says the content is ready, **enter the design phase by asking, not
styling.** Ask about the look before touching CSS: mood/vibe, color direction,
and typography feel (a short structured question is ideal; or take a free
description or a reference they like). Pull a committed direction from
`references/style-presets.md`.

### Phase 5 — Style ONE reference slide, then iterate to lock it
Do **not** style the whole deck yet. Design **slide 1 only** as the reference:
1. Apply the chosen palette/fonts/background and fully compose slide 1, replacing
   its outline scaffolding (`.slidelabel`/`.hint`). Leave slides 2+ as the plain
   outline for now.
2. It live-reloads — the user sees one real, styled slide. **Keep polling and let
   them iterate on it** (comments + inline edits): colors, type, spacing, mood,
   until they say *"this is the style."*
3. Treat that as an explicit confirmation gate. Don't proceed until they confirm.

This makes the style cheap to change — it lives on one slide, not twenty.

### Phase 6 — Roll the locked style across the whole deck
With the reference slide confirmed, propagate that exact style to every remaining
slide: lift its palette/fonts/base rules into global CSS, compose each slide's
content to match, and strip all outline scaffolding (`.modebar`, `.slidelabel`,
`.hint`). Keep every bit of the user's content and the `#counter`. Saving
live-reloads the styled deck — but this is **not** the finish line. Go straight
to Phase 7.

### Phase 7 — Iterate live (the real work)
Propagating the style is where iteration *starts*, not where the deck is done.
**Stay in the poll loop** and refine the full deck with the user — this is
usually the longest phase:
- Fix anything the propagation didn't nail: overflow, spacing, alignment,
  awkward line breaks, weak slides.
- Apply their comments and inline edits as they arrive (they carry a
  **Queued → Working → Done ✓** badge in the panel), re-reading `deck.html`
  before each edit and re-polling immediately after.
- Proactively suggest polish — motion, hierarchy, tightening copy — don't just
  wait passively.

Do **not** announce the deck as "finished" or stop polling on your own. Keep
iterating until the user ends it via **Continue** (your poll returns
`SESSION ENDED by user`) or says they're done. Only then move on.

### End the session
The user can end a stage themselves with the editor's green **Continue** button
(top bar, beside Help/Preview) — it confirms, hands over anything still queued,
then stops the server. Your next `poll` returns `SESSION ENDED by user`; stop
polling when you see it. You can also end it from the CLI:
```bash
node <skill>/visualizer/bin/slides-viz.js end deck.html
```

### Publish to a public URL
The editor's **Publish** button (top bar, beside Preview) uploads the current
deck to the public deploy host (`nextgenslides.dev`) and returns a shareable
`/s/<id>` link. The dialog takes an **optional password** — set one and viewers
must enter it to open the page. The upload is proxied through the local server
(`POST /__viz/publish`), never the browser, so the host's one-time **update key
stays a secret**: it's written to `~/.slides-viz/tokens.json` (mode `0600`),
keyed by deck path. Re-publishing overwrites the **same** link in place using
that stored key — the user never handles the token. Point at a different host
with `NEXTGEN_ORIGIN`. This is a user action; you don't publish on their behalf.

The live editor works identically in both the outline and styled phases — it's
the same `.slide` / `.active` / `window.goToSlide` contract. Each request the
user sends carries a live badge in the panel (**Queued → Working → Done ✓**), and
a status bar below the sent items shows whether the agent is **Listening** or
**Working** — both driven by your poll loop, which is why you must keep polling
the whole time the editor is open.

---

## Building videos (instead of slides)

The same skill builds **HTML videos** — self-contained motion-graphics as one
`.html` file. The editor is the same tool: launch/poll/end are identical, and the
panel **auto-switches to a video UI** (play/pause, a frame-accurate scrubber,
speed control, a Replay button) whenever the deck exposes `window.videoDirector`.
Comments the user leaves capture the current **timecode**, which `poll` prints as
`at: 0:13`.

**Start from `references/motion-explainer.html`.** It embeds the whole timeline
engine and demonstrates the authoring model — copy it and rewrite the scenes.
Read it before building a video.

### The video contract
Same self-scaling 1920×1080 stage as decks, but time-driven instead of slide-driven:
- Each scene is a **`.scene`** element with **`data-dur`** (ms). Scenes lay out
  **sequentially** on one timeline (a `data-start` overrides). The video plays
  through **once and holds the last frame** — it does **not** loop.
- Expose **`window.videoDirector`**: `duration()`, `currentTime()`, `seek(ms)`,
  `play()`, `pause()`, `toggle()`, `setRate(r)`, `onTick(cb)`. The editor's
  transport binds to this. **No `#counter`/`#timecode` element in the deck** — the
  editor shows the timecode; a video must be seamless (no baked-in timers).
- One **master `requestAnimationFrame` clock** drives everything as a pure
  function of time (via the Web Animations API), so **seek / reverse / speed are
  frame-accurate**. Never use bare CSS `@keyframes` for content motion — they
  can't be scrubbed.

### Authoring model (all inline, driven by the engine)
- **`data-anim="<preset>"`** + `data-at` (ms into the scene) + `data-dur`. Presets:
  `fade`, `rise`, `rise-lg`, `fall`, `zoom`, `pop`, `wipe`, `wipe-up`, `grow-x`,
  `grow-y`, `blur-in`, and **`draw`** (SVG stroke line-draw — put a `<path>`/`<line>`
  in an inline `<svg class="layer">`; bake arrowheads into the *same* path so they
  draw on naturally).
- **`data-count-to`** (+ `data-count-dur`, `data-count-dec`, `data-count-suffix`)
  interpolates a number over time.
- **`data-cue`** + `data-from`/`data-to` (scene-local ms) shows an element only
  during a window — use it to sequence things in *and* out (e.g. a label that
  appears then leaves, or swapping one element for another).

Keep motion purposeful and the pacing punchy (a short promo is ~15–25s). Iterate
live exactly like a deck: launch, **poll immediately**, apply, re-poll — and stay
in the loop until the user hits **Continue**.

---

## Notes
- The visualizer serves the deck at `http://127.0.0.1:<port>/` and watches the
  file — any change (agent edit or an in-place text edit) live-reloads the browser.
- The editor picks the UI from the deck: `window.videoDirector` → video editor;
  otherwise the slides editor. Shared logic lives in `visualizer/ui/editor-core.js`.
- `launch` reuses a running session for the same deck instead of starting a second.
- The user and the agent edit the *same* `deck.html`; always re-read it before
  editing so you don't clobber a manual change.
- Only `poll` blocks; `launch`/`end`/`status` return immediately.
- Verify visually: after big changes, screenshot or ask the user to confirm no
  overflow or overlap at the fixed stage size.
