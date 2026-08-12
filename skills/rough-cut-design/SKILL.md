---
name: rough-cut-design
description: Use this skill to generate well-branded interfaces and assets for Rough Cut, a transcript-based video editor — either for production, throwaway prototypes, marketing mocks, or slide decks. Contains essential design guidelines, colors, typography, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, then treat
`ui_kits/editor/` as the source of truth for the full editor surface.
Use `preview/` as primitive and token reference cards.
Also inspect `colors_and_type.css` and `assets/` as needed.

Rough Cut is a local-first, transcript-based video editor for agent-assisted
rough cuts. The product's core editing metaphor is **reading a manuscript** —
the transcript is the primary surface, and the user edits by marking
**passages** to keep or skip. The other concept is **footage** (the video
file). A passage lives inside a footage; the cut is the list of footages in
order, each playing only its kept passages. The design system is **light,
literary, futuristic**: a faintly-warm near-white paper for the transcript,
a faintly-cool near-white canvas for chrome, a sharp modern serif (DM Serif
Display) for display, and a mono (JetBrains Mono) for all UI labels and data.
The accent is a vermillion red — the editor's pen.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy
assets out and create static HTML files for the user to view. Always:

- Link `colors_and_type.css` (or inline its `:root` block).
- Use the three families as documented; do **not** introduce a generic sans.
- Match the voice rules in README's **CONTENT FUNDAMENTALS** section. Sentence
  case. No emoji. No exclamation marks. Verbs do the work. Status pills read
  like `key: value`; dock presence can read like `agent · listening`. The
  agent is named **`agent`**; never give it a personal proper name.
- Match the visual rules: hairlines over decorative shadows, 2–4px radii max,
  vermillion for keep actions and active passage / footage state, ultramarine
  for the agent and agent-specific actions, paper vs canvas contrast.
- Two nouns, two granularities: **passage** (prose-level, in the manuscript)
  and **footage** (the video file, what the cut is an ordered list of).
  Passage status is **keep**, **skip**, or **active**. There is no separate
  "clip" or "source" concept and no separate agent-review surface. Agent
  discussion lives in the dock; edits are applied through the project model.
- For icons, use the Lucide-style set in `ui_kits/editor/icons.jsx` or match it
  with a 1.5px stroke and square line-caps.

If working on production code, copy the assets out, read `colors_and_type.css`
to pull tokens, and treat `ui_kits/editor/` as the canonical component pattern
reference. The UI kit is still prototype code, not production code.

If the user invokes this skill without any other guidance, ask them what they
want to build or design. Useful questions:

- Is this a product surface (in-editor) or a marketing / docs surface?
- Should the transcript-as-prose metaphor appear, or is this something more
  chrome-focused (e.g. settings, project list, login)?
- Do they want a static design or an interactive prototype?
- Any specific Rough Cut concepts in scope (footages, passages, agent,
  render, transcribe)?

Then act as an expert designer who outputs HTML artifacts _or_ production
code, depending on the need.
