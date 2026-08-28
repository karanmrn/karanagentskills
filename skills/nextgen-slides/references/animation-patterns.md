# Animation patterns

Motion should support reading, not decorate. All CSS/JS is inline in the deck.

## Slide transitions
The stage cross-fades via `.slide { transition: opacity .5s }`. That's usually
enough. For a subtle rise, add on the active slide:

```css
.slide > * { opacity: 0; transform: translateY(16px); transition: .6s ease; }
.slide.active > * { opacity: 1; transform: none; }
.slide.active > *:nth-child(2) { transition-delay: .08s; }
.slide.active > *:nth-child(3) { transition-delay: .16s; }
```

## Entrance on build (per-element reveal)
Give elements `data-build` and reveal them with an IntersectionObserver or on
slide activation. Keep it to headline → body → visual order.

## Ambient background motion
Slow, low-amplitude only — a drifting gradient or a single floating shape:

```css
@keyframes drift { to { transform: translate(40px, -30px); } }
.glow { animation: drift 18s ease-in-out infinite alternate; }
```

## Counters / numbers
Animate large stats with `requestAnimationFrame`, easing out over ~800ms, once
the slide becomes active.

## Rules
- Respect `prefers-reduced-motion: reduce` — disable non-essential motion.
- Never animate layout in a way that causes overflow of the 1920×1080 stage.
- Durations: transitions 300–600ms, ambient loops 12–24s. Nothing frantic.
