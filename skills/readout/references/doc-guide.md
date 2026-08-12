# Readout document guide

A readout is the durable artifact of a conversation-length investigation. The reader may be the author weeks later, or a teammate who has none of the conversation's context. Every choice below serves standalone readability.

## The one hard requirement: self-contained

One `.html` file. All CSS and JS inline; no CDN links, no external fonts, no external images (use inline SVG or data URIs). Readouts get shared over Slack and opened offline — a broken external dependency silently ruins the document. System font stacks look good everywhere and avoid font embedding entirely. (Sanctioned exceptions, all inside the bundled code pane and all click-time: fetching source from GitHub, and lazy-loading highlight.js from its CDN when the pane opens. The document itself must still render completely offline.)

## The canonical template — chrome is fixed

Readouts share one visual identity so the library reads as a set; small per-document styling drift is a bug. Start every document from `assets/template.html` (in this skill's directory, next to `references/`) and fill its slots:

- The `<style data-readout>` and `<script data-readout>` blocks are the shared chrome — copy them **verbatim** and never edit them. They fix the warm-paper serif typography and palette (light + dark), the sticky Contents rail with scrollspy, the header anatomy, section rules, callouts, badges, tables, figures, collapsibles, and the provenance footer.
- The header anatomy is fixed: a mono uppercase `.kicker` (repo · context · readout type), the `h1` title, a one-line `.subtitle` framing the document, and a mono `.meta` line (date · audience · `org/repo@commit` pin).
- Use the template's classes — `.callout` (+ `.callout-label`, `.warn`), `.badge` (`good`/`bad`/`neutral`), `.table-wrap`, `figure`/`figcaption`, `<details>` — rather than inventing parallel patterns.
- Document-specific CSS (a diagram's dimensions, a one-off content element) goes ONLY in the empty `<style data-doc>` block, and must not override the chrome's tokens or selectors.

## Linked code references

When the repository's host and the examined commit are known, make every `file.rs:123` reference a real hyperlink into the code — e.g. `https://github.com/<org>/<repo>/blob/<commit>/<path>#L123`, with `#L10-L25` for ranges, and link code-snippet captions the same way. Pin links to the commit, never a branch, so they stay valid as the code moves. Get the remote and commit from `git remote get-url origin` / `git rev-parse HEAD` when the repo is checked out; otherwise use whatever the source material states. If the host or commit is unknown, keep references as plain monospace text — never guess URLs.

### The code pane

Linked references get an in-document source viewer: clicking a GitHub blob link opens the code in a split pane on the right, pushing the document content aside rather than overlaying it; clicking another reference loads into the same pane; the pane is resizable by dragging its left edge; a close button (and Escape) dismisses it. Code is syntax-highlighted (highlight.js, loaded lazily from a CDN only when the pane opens — plain text when offline).

Do not write this viewer yourself — inline the bundled asset at `assets/code-pane.html` (in this skill's directory, next to `references/`) **verbatim** immediately before `</body>`. It auto-attaches to every GitHub blob link in the document, so references need no extra markup — which is also why they must stay ordinary anchors: with JS disabled (or on cmd/ctrl-click) the links simply open GitHub.

How the pane finds source, in order:
1. **Files embedded at generation time** — the only path that works offline and for private repos with zero reader setup, so do it whenever a referenced repo is checked out locally. After writing the doc, run the bundled helper:
   `python3 <skill-dir>/scripts/embed_snippets.py <doc.html> --repo <checkout> [--repo <another-checkout>]`
   It scans the doc's blob links, extracts each referenced file *at its pinned commit* (`git show <commit>:<path>`), embeds whole files (gzip+base64 for anything non-trivial — the pane inflates in-browser), and injects the `data-code-snippets` blob. Mind the audience before embedding: it ships that source inside a shareable file. Only hand-write the JSON blob (`{"org/repo@commit:path": {"start": N, "text": "..."}}` windows) if git isn't available.
2. **Runtime fetch** of `raw.githubusercontent.com` when the reader clicks — works for public repos online.
3. **Reader-supplied token** — when the fetch fails with an HTTP error, the pane offers a paste-a-token form and retries via `api.github.com`, so teammates with repo access can view private code even without embedded snippets. The token stays in the reader's `sessionStorage` for that tab; it is never part of the document — never embed tokens or credentials of any kind in a readout.
4. **Graceful fallback** — a cause-specific message plus an "open on GitHub" link.
The asset handles 2–4 itself; your job is 1.

## Content

- **Document the refined end-state, not the chronology.** Conversations wander and self-correct; the readout presents the final, corrected understanding. Keep a discarded belief only when it's an instructive gotcha — those earn callouts.
- **Curate.** Length should track information density, not conversation length. Cut anything the reader doesn't need; a readout is not a transcript.
- **Ground every claim.** Cite `file.go:123`-style references, function and type names, endpoints. Verify references against the codebase before asserting them — a doc with a wrong line number loses the reader's trust for all the right ones too.
- **Distinguish verified from inferred.** If something was concluded in conversation but not confirmed in code, say so.
- **Open with an executive summary** — a few sentences a reader can stop after and still have the headline understanding.
- **Give the document a one-sentence `<meta name="description" content="...">`** — the readouts index page (`~/.readouts/index.html`, regenerated by `scripts/update_index.py`) uses it as the entry's summary line.
- **Close with a provenance footer**: date, what conversation/investigation it came from, which repos (and commit, if relevant) were examined.

## Structure and layout

The chrome is fixed; the sectioning is yours. Let the material choose it:

- Cross-platform / cross-system findings → per-system sections plus a comparison matrix
- A "how does X work" investigation → narrative explainer following the data flow
- A decision or tradeoff discussion → options, criteria, recommendation

Elements that usually earn their place in longer documents (all already styled by the template):

- Tables for anything the reader will want to compare across columns — for before/after numbers, add an explicit delta column (`<span class="delta">`)
- `<details>` collapsibles for deep-dive appendices that would bloat the main read
- `.badge` chips for statuses, HTTP codes, platform names
- `.callout` with a `.callout-label` for gotchas, cautions, and instructive discarded theories — the template styles these as a soft tint with a full hairline border; never restyle them into a left-accent stripe (a thick colored left border as the sole edge treatment is banned in readouts)
- Diagrams as inline SVG when a flow or topology is central to understanding — draw with `currentColor` so both palettes work, and size them in the `data-doc` style block

## Reading experience

The template handles column width, responsive collapse, and both palettes. What remains your responsibility:

- Wrap wide tables in `.table-wrap` so they scroll instead of overflowing on phones
- Every TOC entry must point at a real `<section id>`; nested entries use `class="sub"`
- Monospace for code, paths, and identifiers; if you add syntax highlighting to code blocks in the document body, it must be inline (the code pane handles its own highlighting via its lazy CDN loader)

## JavaScript

Progressive enhancement only — scrollspy, collapsibles, theme toggles, and the bundled code pane. The document must read fine with JS disabled.

## Before you finish

Sanity-check the artifact: parse the file (e.g. with Python's `html.parser`) to catch unclosed tags, confirm there are zero external `http(s)://` resource references outside the bundled code-pane asset, and skim the rendered structure for empty sections or placeholder text left behind.
