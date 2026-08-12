# Fonts

Rough Cut uses three Google Fonts:

- **DM Serif Display** — display + drop caps  
  https://fonts.google.com/specimen/DM+Serif+Display
- **Newsreader** — body prose / transcript  
  https://fonts.google.com/specimen/Newsreader
- **JetBrains Mono** — UI, data, timecodes  
  https://fonts.google.com/specimen/JetBrains+Mono

They are loaded via Google Fonts CDN at the top of `colors_and_type.css`:

```css
@import url("https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap");
```

For offline / self-hosted builds, download the families from the URLs above
and drop the `.woff2` files into this folder, then replace the `@import` with
local `@font-face` blocks.

## Substitution note for the user

These three families are **first-choice picks** for the look the brand is
going after (literary + futuristic + light). They are not "the official Rough
Cut typefaces" — there are none yet. If you want to commission or license a
proper title face later, good directions to explore:

- For display: GT Sectra, Tiempos Headline, Source Serif Display, Reckless Neue
- For body: Tiempos Text, Source Serif 4, Lyon Text
- For mono: Berkeley Mono, GT America Mono, IBM Plex Mono

The CSS variables in `colors_and_type.css` (`--font-display`, `--font-body`,
`--font-mono`) make swapping a one-line change.
