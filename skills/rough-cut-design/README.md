# Rough Cut — Design System

A reimagined design language for **Rough Cut**, a local-first, transcript-based
video editor for agent-assisted rough cuts. You edit a video the way you'd edit
a manuscript: by reading the transcript like a piece of literature, marking
passages to keep or strike, and letting the timeline assemble itself.

> _"Cut by transcript, collaborate in the browser, render without leaving your
> shell."_ — Rough Cut tagline

---

## The product, in one paragraph

Rough Cut opens video files in a browser editor, transcribes them with
ElevenLabs, and lets you assemble a rough cut by **keeping** or **skipping**
passages of the transcript. The transcript is the manuscript; the cut is
the kept text, in order. A local CLI agent can long-poll the project, read
structured snapshots, and apply edit operations programmatically — so an
LLM agent can do the boring scrubbing while the human reviews the prose.
Everything is plain files on disk: `project.json` is the editor's source
of truth, `timeline.json` is the render contract, the browser preview plays
kept passages live, and `ffmpeg` produces final MP4 exports.

### Core nouns

- **Footage** — an original video file referenced by absolute path. Never
  copied or mutated. The thing on disk. Has a label, a duration, and (after
  transcription) a list of passages.
- **Transcript** — word-level timing for a footage, written by ElevenLabs.
- **Passage** — a speaker segment inside a footage. Has a `(start, end)`
  range, a transcribed text, and a status of `keep`, `skip`, or `active`.
  Passages are the **prose-level editing unit** — what the user marks up in
  the manuscript surface.
- **Timeline** — the project's footages in order. The render contract.
  Each footage in the timeline plays only its kept passages. There is **no
  separate "clip" object**: the prose surface manages passage-level edits,
  the timeline strip manages footage-level order. Two granularities, one
  data model.
- **Project** — directory under `~/.rough-cut-axi/projects/` containing
  `project.json`, `timeline.json`, transcripts, and renders.
- **Agent** — the asynchronous LLM collaborator named simply **`agent`**.
  The user queues prompts in the browser; the agent polls them from the
  CLI, reads structured snapshots, and writes back edit operations
  directly to the project. There is no human-approval step inside the
  product.

### Core verbs

`open · transcribe · keep · skip · trim · split · reorder · prompt · apply ·
render final · end`

`keep` / `skip` / `trim` / `split` operate on **passages**.  
`reorder` operates on **footages**.  
`prompt` / `apply` operate through the agent dock.  
These are the user's vocabulary _and_ the API.
Passage state is usually shown by manuscript styling; explicit verbs belong in controls, labels, tooltips, and focused action surfaces, not as persistent chrome on every passage.

---

## Source materials

This system was built by reading:

- **GitHub:** [`kunchenguid/rough-cut-axi`](https://github.com/kunchenguid/rough-cut-axi)
  — the CLI + browser editor prototype. Specific files of interest:
  - [`README.md`](https://github.com/kunchenguid/rough-cut-axi/blob/main/README.md)
    — product copy, tagline, CLI reference.
  - [`src/project-schema.js`](https://github.com/kunchenguid/rough-cut-axi/blob/main/src/project-schema.js)
    — the canonical project shape.
  - [`src/edit-operations.js`](https://github.com/kunchenguid/rough-cut-axi/blob/main/src/edit-operations.js)
    — every edit verb (`setPassageStatus`, `trimPassage`, `splitPassage`,
    `reorderFootages`, `replacePassageRange`, `setPassageReason`).
  - [`src/server.js`](https://github.com/kunchenguid/rough-cut-axi/blob/main/src/server.js)
    — the existing browser shell (deliberately replaced; functionality preserved).
  - [`src/transcription.js`](https://github.com/kunchenguid/rough-cut-axi/blob/main/src/transcription.js),
    [`src/rendering.js`](https://github.com/kunchenguid/rough-cut-axi/blob/main/src/rendering.js)
    — backends.

The repo's existing visual language (sepia gradient, mixed Inter/Georgia
typography, neon timeline chips on a dark panel) was treated as a wireframe of
the _functionality_ only. None of it was preserved in this system — the user
asked for a complete rethink: clean, futuristic, literary, light theme.

---

## CONTENT FUNDAMENTALS

The product's existing copy points at a specific voice — terse, technical,
honest about being a workshop tool. The design system extends that voice into
something with a little more confidence and a little more poetry, fitting the
"literature" cue.

### Tone

- **Direct and unembellished.** The README says _"Rendering is explicit"_, not
  _"Effortlessly render with one click!"_ Copy should describe what happens,
  not what it feels like.
- **Mechanical honesty.** When something is asynchronous, say so. When the
  agent is waiting, the UI says `agent: waiting` — not `Helper is on standby`.
- **Quiet, not chatty.** No exclamation points. No emoji. No second-person
  cheerleading.
- **Verbs do the work.** Buttons are `Keep`, `Skip`, `Trim`, `Split`,
  `Add footage`, `Send`, `End session`. Not `Save Changes` or `Get Started`.
- **A measured literary register** is welcome in headers and empty states —
  this is a tool for people cutting words, and the chrome can use a sharp
  sentence here and there.

### Casing

- **Sentence case everywhere.** `Live preview`, not `Live Preview`. `Footages`,
  not `Footage List`. The only Title Case is for proper nouns (`ElevenLabs`,
  `ffmpeg`, `Rough Cut`).
- **All-caps reserved for kickers and counters** — short labels above titles,
  speaker tags in the transcript, the slim "section title" strip on a panel.
  Always with letter-spacing `0.14em`–`0.18em`.

### Person

- **Second person, sparingly.** _"You'll need an ElevenLabs API key."_ The user
  is addressed, but the product never narrates itself in the first person
  (no _"I'll render that for you"_ — that's reserved for the agent's own chat
  messages, which are quoted, not narrated).
- The CLI speaks in **plain key/value pairs** (`auth: elevenlabs / status:
  stored`). The browser should echo this register in status pills and
  inspector strips.

### Numbers & timecodes

- Time in the editor transcript and player: `mm:ss.d` (`01:23.4`). Always monospaced.
- Precise range fields may use `mm:ss.cs` (`01:23.45`). Always monospaced.
- Time on footage cards: `00:20.0` kept / `04:23` total. Always tabular.
- Counts in pills: `3 footages · 1m 04s` or `11 kept · 2 skipped`.
  The middle dot is the separator.
- IDs are monospaced when shown. The editor mock prioritizes human labels and
  footage order in the main surface, with passage IDs available in focused
  metadata or tooltips.

### Voice examples

**Empty states.** Sharp, slightly literary.

> _No transcript yet. Run `rough-cut-axi transcribe` and the prose will fill in._
>
> _No footage opened._

**Status pills.** Just the fact.

> `agent: listening` · `3 footages` · `11 kept · 2 skipped` · `1m 04s`

**Confirmations.** Pre-undo, not pre-permission.

> `Passage skipped. Undo` _(toast, 6s, never a modal)_

**Agent presence.**

> `Agent waiting for a prompt.` / `Agent reading transcript_3.` /
> `Agent applied 4 edits.`

### Emoji

Not used. Not in chrome, not in chat, not in onboarding. Where a visual cue is
needed, we use a glyph from the icon set or a dedicated status dot.

### Vibe summary

> Imagine the editorial page of a small literary magazine that happens to run
> on real-time infrastructure. Quiet, exact, occasionally dryly poetic. The
> tool respects you. It also respects the original footage.

---

## VISUAL FOUNDATIONS

### The system in one line

A **paper-warm reading surface** for the manuscript, a **cool near-white chrome**
for the workshop, a **vermillion** ink for edits, and an **ultramarine** for
the agent. Three typefaces. Almost no rounding. Almost no shadow. The grid does
the work.

### Color

Two surface temperatures live side-by-side, both reading as **white**:

- **Paper** (`#FAF9F5`, faintly warm) — the transcript. The thing being edited.
  Reads as a printed page, not a cream wash. The "page" itself (`paper-2`,
  `#FFFFFE`) is effectively white.
- **Canvas** (`#F3F3F0`, faintly cool) — everything else: chrome, panels,
  player frame, the agent dock. The "workshop."

The delta between paper and canvas is intentionally small — the eye reads
"page vs panel" without ever naming a colour.

**Ink** is a slightly cool near-black (`#16161A`), kept short of pure black
so the page doesn't feel printed-by-photocopier. Secondary ink (`#5A5750`)
is warmed up to belong to the paper. Hairlines (`#E5E4DE` on canvas,
`#E5E2D5` on paper) are always _drawn_, never _shadowed_.

Two accents, used like signs:

- **Vermillion** (`#C7361F`) — the editor's red pen. Marks the active passage,
  the active footage rail, keep actions, the active scrubber, and destructive
  confirmations. Use it sparsely so the manuscript keeps visual priority.
- **Ultramarine** (`#1F3A7A`) — the agent. Used for agent-authored chat
  messages, the agent presence dot, links into agent context, and agent-specific
  actions such as `Send`. It is not used for global editor actions.

Plus three sober semantic colors: `caution` amber, `ok` ink-green, `mute` dust.

Full palette lives in [`colors_and_type.css`](./colors_and_type.css).

### Typography

Three families, picked to sit in the tension between "literature" and
"futuristic":

| Role | Family | Why |
| --- | --- | --- |
| Display / headings | **DM Serif Display** | A wide, confident modern serif with high-contrast strokes. Reads as literary and editorial — magazine-cover register — without feeling antique. Italic version carries the wordmark. |
| Body / transcript | **Newsreader** | Designed for screen reading. Quiet, warm, very legible at body sizes. The transcript prose lives in this. |
| UI / data / mono | **JetBrains Mono** | Every label, every timecode, every status pill, every keyboard cue. Mono is the futuristic register — it reads as terminal output, which is appropriate for a CLI-anchored product. |

No general-purpose sans. UI labels are mono. This is a deliberate constraint:
it gives the whole product the feel of a typesetting bench. If a sans is ever
needed for a long block of UI prose (e.g. a settings page) we extend with
mono at slightly tighter tracking, _not_ a Helvetica.

Full type scale and semantic styles live in
[`colors_and_type.css`](./colors_and_type.css).

### Spacing

A **4-pixel grid**, expressed as `--space-1` through `--space-12`. The system
favors a slightly tighter rhythm than most modern web design — panels sit at
`--space-4` from each other (16px), not 24. The point is to give the prose
itself plenty of air on the inside while the chrome stays compact.

### Backgrounds

- No images in chrome. No textures. No gradients in chrome.
- The transcript surface (paper) has _one_ very subtle vertical gradient
  baked in — a ~6% darker gutter at the left and right edges, suggesting
  the curve of a bound page. This is the only "trompe-l'œil" in the system.
- The player frame is a warm-black (`#0F0E0C`) container.
  The mock uses dark still-frame gradients or real video inside that frame.
- No background imagery, illustrations, or repeating patterns.
- The login / new-project surface uses a single full-bleed photograph of
  film stock or rushes on a desk — when one exists. Until then, a flat
  paper surface is fine.

### Borders, dividers, hairlines

- **Hairlines do most of the structural work.** 1px solid in `--line` on
  canvas, `--line-paper` on paper. Always 1px, never 2px.
- Cards: 1px solid hairline + 4px radius. No drop shadow unless lifted.
- Dividers between sections: full-bleed 1px hairline, no inset.
- The transcript page is framed by the paper field and hairlines.
  A full page border is optional, not required by the editor mock.

### Shadow / elevation

Almost nothing. Three steps:

- `--shadow-0`: none. Used for 95% of surfaces.
- `--shadow-1`: `0 1px 0 rgba(22,22,26,0.04), 0 8px 24px -12px rgba(22,22,26,0.18)`.
  Used for popovers, the agent dock when floating, and the timeline strip
  when it sits over the player.
- `--shadow-2`: `0 24px 60px -24px rgba(22,22,26,0.28)`. Modal-only.

No decorative inset shadows.
Active rails may use an inset bottom shadow, as in the passage and footage states.

### Radii

- `--radius-0`: 0px. Most chrome.
- `--radius-1`: 2px. Inputs, buttons, the "page" border.
- `--radius-2`: 4px. Cards, popovers, footage cards.
- `--radius-pill`: 999px. Status pills only.

Big rounded corners do not appear anywhere. This is part of the literary
register — books don't have rounded corners.

### Animation

- **Easing:** `cubic-bezier(0.2, 0.7, 0.2, 1)` everywhere. One easing curve,
  one mental model. We call it `--ease`.
- **Durations:** `--dur-1` 120ms (snaps, hovers), `--dur-2` 220ms
  (panel transitions), `--dur-3` 480ms (the rare large reveal — a modal,
  a render-complete confetti-less celebration).
- **No bounces, no springs.** The product is editorial. Things glide.
- **Hover states** are the gentlest fades: text 100% → 78% opacity, surfaces
  cross-fade `--canvas` → `--canvas-hover` (`#F4F2EC`). Pointer cursors are
  used liberally — discoverability matters.
- **Press states** dip the surface 4% darker and shift down by 0.5px. No
  scale. We don't squish.
- **Active selection** in the prose is a vermillion wash with an inset underline.
  The product physically marks the page.
- **Loading** is a single 1px hairline that pulses opacity 30% → 100%.

### Transparency & blur

- **Transparency is mostly avoided.** Surfaces are opaque. The exception is
  the agent dock when it floats over content — `rgba(251,250,246,0.92)` +
  `backdrop-filter: blur(12px)`.
- **Protection gradients** appear only over the video preview, at the top
  (controls overlay) and bottom (scrubber overlay), `linear-gradient(180deg,
  rgba(15,14,12,0.0), rgba(15,14,12,0.6))`. Never on chrome.

### Cards

Three styles, used in three contexts:

- **Paper card** — for transcript-adjacent things (margin notes, kept-passage
  receipts in the prose gutter). 1px solid `--line-paper`, `--radius-2`, no
  shadow, `--paper-2` background.
- **Canvas card** — for chrome (footage cards in the strip,
  agent messages). 1px solid `--line`, `--radius-2`, no shadow, `--canvas`
  background.
- **Lifted card** — for popovers and dropdowns only. `--shadow-1` on
  `--canvas`, `--radius-2`.

### Layout rules

- **Fixed elements:** the editor topbar is 52px tall in the full editor mock.
  The agent dock sits in the workshop pane rather than floating.
- **Two-pane spine:** the editor is always _reading surface left, workshop
  right_. On narrow screens the workshop stacks below.
- **Reading column is 64ch wide max.** The page never gets wider than a book.
  This is non-negotiable for the transcript.
- **Chrome is dense but breathing.** Internal panel padding is `--space-4`
  (16px). Buttons are `--space-2 --space-3` (8/12). Status pills are tight.

### Imagery

- All photographic imagery is **warm, grainy, daylit** — film-stock register.
  Lifted from cinematography moodboards, not stock-photo SaaS. When in doubt,
  use **no image** — the typography carries enough.
- Avoid: 3D renders, gradient meshes, AI-generated faces, gradient blobs.
- Loaded thumbnails of the user's own footage are clipped at `--radius-1`,
  desaturated 10%, slightly warm-tinted (a 4% paper overlay) so they sit on
  the canvas without screaming.

### Iconography

See [ICONOGRAPHY](#iconography) below.

---

## ICONOGRAPHY

### Approach

Rough Cut's icon language is **single-weight, hairline-thin (1.25px stroke),
24px grid, square caps, no fill, no rounded joins** — to match the system's
typographic register (sharp serif + mono). Icons read as marks made with a
fine technical pen.

### Source set

We use Lucide-style geometry: 24px viewBox, 1.5px stroke, square caps, no fill.
The full editor mock implements the current icon set inline in `ui_kits/editor/icons.jsx`.
If a production icon set is swapped in later, match those metrics so the replacement is free.

### Substitution flag

Rough Cut's existing repo does not ship its own icon font or SVG set, so
**Lucide is a substitution** — chosen for its closeness to the hand-drawn
technical register the brand calls for. If you build a production icon set
for Rough Cut, match Lucide's metrics (24px, 1.5px stroke, square caps)
so the swap is free.

### Common marks

| Verb / state | Icon |
| --- | --- |
| Keep | `check` |
| Skip | `x` (or `strikethrough` in prose) |
| Trim | `chevrons-left-right` |
| Split | `scissors` |
| Play live preview | `play` |
| Add footage | `plus` |
| Send to agent | `send` |
| End session | `log-out` |
| Agent | `sparkle` (single, not two) |
| Project / file | `file-text` |
| Footage | `clapperboard` |
| Footages strip | `align-left` (with timeline glyph fallback) |

### Emoji

Not used.

### Unicode glyphs

We use a small set of typographic glyphs as low-noise punctuation in the UI:

- `→` for time ranges (`00:12 → 00:18`)
- `·` for separators in pills
- `¶` for paragraph anchors in the transcript margin
- `§` for chapter / source breaks in the transcript
- `↳` for agent-message threading

These are typed inline. They are part of the literary register and should
never be replaced with icons.

### Logo

A minimal wordmark — `rough cut` set in **DM Serif Display italic** at low
contrast weight, with a vermillion **timeline playhead** running between the
two words. The playhead is the cursor of every video editor — and here, it
sits literally on the cut. Files in [`assets/logo/`](./assets/logo/).

---

## Index — what's in this repo

```
README.md                          ← you are here
SKILL.md                           ← cross-compatible skill manifest

colors_and_type.css                ← the design tokens (vars + semantic styles)
fonts/                             ← link to Google Fonts; mirrors documented

assets/
  logo/
    rough-cut-mark.svg             ← the wordmark
    rough-cut-glyph.svg            ← the c-strike glyph alone

preview/                           ← Design System tab cards
  type-display.html
  type-body.html
  type-mono.html
  colors-surfaces.html
  colors-ink.html
  colors-accents.html
  colors-semantic.html
  spacing.html
  radii-shadow.html
  buttons.html
  inputs.html
  pills-tags.html
  cards.html
  passage-states.html              ← the prose-level concept
  footages-strip.html              ← the cut-level concept
  agent-presence.html
  logo.html

ui_kits/
  editor/                          ← the one product surface
    README.md
    index.html                     ← interactive walkthrough
    demo.jsx                       ← app shell and layout
    components.jsx                 ← Topbar · Transcript · PlayerSurface · FootagesStrip · AgentDock
    primitives.jsx                 ← Button, Pill, Tag, Hairline, etc.
    icons.jsx                      ← Lucide wrapper
    data.js                        ← sample project + transcript

```

---

## How to use this system

This system is designed to be loaded by an LLM design agent (or a human) when
building new Rough Cut surfaces. The fastest path:

1. Treat `ui_kits/editor/` as the source of truth for the full editor surface.
2. Read `colors_and_type.css` and `<link>` it from your HTML.
3. Pull `preview/*.html` only as primitive/token reference cards.
4. Match the voice rules in CONTENT FUNDAMENTALS for every string you write.
5. When unsure: it's quieter than you think. Take an element away.

See [SKILL.md](./SKILL.md) for the agent-readable manifest.
