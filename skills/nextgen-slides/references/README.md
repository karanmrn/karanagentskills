# Reference templates

A gallery of **ten fully-formed demo decks**, each committing hard to a single
visual and thematic direction. They exist to show the range of what an
`nextgen-slides` deck can look like — pick one as a starting point, or mine them for
palettes, type pairings, and layout ideas.

Every template obeys the same non-negotiable [deck contract](../SKILL.md#the-deck-contract-non-negotiable):
one self-contained `.html` file, a self-scaling fixed **1920×1080** stage, fonts
via `<link>` and zero other runtime deps, `cqw`/`cqh` sizing (never `vw`/`vh`), a
JS-computed `#counter`, and `window.goToSlide(i)`. Open any file directly in a
browser and drive it with **← / →** (or space).

## The gallery

| # | Template | Style | Subject | Slides |
|---|----------|-------|---------|:-:|
| 1 | [`editorial-serif.html`](editorial-serif.html) | Literary keynote — navy & gold, Fraunces + Newsreader, big italic pull-quotes | The Art of the Opening Line | 6 |
| 2 | [`bold-signal.html`](bold-signal.html) | Brutalist high-contrast — black/white + electric red, giant numerals | State of Remote Work 2026 | 8 |
| 3 | [`warm-paper.html`](warm-paper.html) | Warm print — cream paper, terracotta, Instrument Serif, hairline rules | The Third Wave of Coffee | 6 |
| 4 | [`electric-studio.html`](electric-studio.html) | Neon product keynote — near-black, mint/violet glows, gradient hero | Halo — Ambient AI Notetaker | 6 |
| 5 | [`swiss-grid.html`](swiss-grid.html) | Swiss/International — white, red accent, visible grid, Archivo | Principles of Good Typography | 7 |
| 6 | [`retro-memphis.html`](retro-memphis.html) | 80s Memphis — pastel shapes, squiggles, thick borders, tilted cards | The Golden Age of Arcades | 6 |
| 7 | [`terminal-mono.html`](terminal-mono.html) | Terminal/hacker — phosphor green on black, window chrome, scanlines | Anatomy of a Data Breach | 6 |
| 8 | [`botanical.html`](botanical.html) | Nature editorial — deep forest green, sage, botanical line art | Rewilding Your Backyard | 6 |
| 9 | [`saas-pitch.html`](saas-pitch.html) | Investor deck — deep indigo, blue→violet gradient, rounded cards | Ledgerly Series A | 7 |
| 10 | [`vintage-press.html`](vintage-press.html) | Vintage broadsheet — aged paper, masthead, drop caps, columns | The 1977 NYC Blackout | 6 |

Ten deliberately divergent directions: dark and light, serif and mono, minimal
and maximal, data-forward and narrative. No two share a palette, a type pairing,
or a layout system.

## Also in this folder

- [`outline-template.html`](outline-template.html) — the plain white **content
  canvas** for the outline phase (content first, no style yet).
- [`deck-template.html`](deck-template.html) — a minimal working styled starter.
- [`stage.css`](stage.css) — the self-scaling stage base rules + type scale.
- [`style-presets.md`](style-presets.md) — committed visual directions to draw from.
- [`animation-patterns.md`](animation-patterns.md) — motion guidance.

## Videos

Two motion-graphics **video** references, built the same self-scaling 1920×1080
way but time-driven instead of slide-driven — `.scene` elements with `data-dur`
on one master-clock timeline, exposing `window.videoDirector` (so the editor
shows a play/scrub/speed transport). See [Building videos](../SKILL.md#building-videos-instead-of-slides).

- [`motion-explainer.html`](motion-explainer.html) — an animated explainer of the
  skill itself (typed prompt, a drawn pipeline with a loop-back arc, a live-edit
  loop, a self-contained scene, a CTA). **It embeds the timeline engine** — copy
  it to start a new video.
- [`bold-signal-video.html`](bold-signal-video.html) — a stat-driven hype reel
  (kinetic typography + animated count-ups).

## Using a template

1. Copy the file you like to your deck path (e.g. `cp references/swiss-grid.html deck.html`).
2. Replace the copy with your own content, keeping the `.slide` / `.active`
   structure and the script block intact.
3. Open it in the visualizer to iterate live:
   ```bash
   node ../visualizer/bin/slides-viz.js launch deck.html
   ```
