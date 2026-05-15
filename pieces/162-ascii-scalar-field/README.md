# Piece 162 — Density in Characters: ASCII Scalar Field

A live mathematical scalar field rendered as a grid of monospaced characters, where character choice encodes field density and hue encodes field value. The medium — ASCII art — is woven into the mathematics itself: what you read as text is simultaneously a sampled wave interference pattern.

## Scalar Field: Superimposed Plane Waves

The field value at grid cell `(cx, cy)` at time `t` is the sum of four plane waves:

```
val = (1/N) Σᵢ sin(cx·fxᵢ + cy·fyᵢ + t·speedᵢ + phaseᵢ)
```

normalised to `[0, 1]` via `(val + 1) / 2`.

Each wave `i` is characterised by its spatial frequency vector `(fxᵢ, fyᵢ)`, which sets the direction and wavelength of the plane wave across the grid, and a temporal speed `speedᵢ` that advances the phase each frame.

| Wave | freq_x | freq_y | speed | phase |
|------|--------|--------|-------|-------|
| 0    | 0.08   | 0.05   | 0.9   | 0.0   |
| 1    | 0.04   | 0.09   | 0.7   | 1.2   |
| 2    | 0.10   | 0.03   | 1.1   | 2.4   |
| 3    | 0.06   | 0.07   | 0.6   | 3.7   |

Because the four waves travel in different directions at different speeds, they produce a complex, ever-shifting interference pattern — regions of constructive interference (peaks) alternate with destructive interference (troughs), creating the visual turbulence that drives character selection.

## Density Ramp: Field Value → Character

The eleven-character ramp orders glyphs by visual density — the proportion of ink they place within a fixed cell:

```
index:  0    1    2    3    4    5    6    7    8    9    10
char:   ' '  '.'  '·'  ':'  '-'  '='  '+'  'o'  'O'  '#'  '@'
```

`charIndex = floor(val × 11)`, clamped to `[0, 10]`. Low field values produce sparse punctuation; high values produce dense block glyphs. The eye reads this as a grayscale tone field — exactly what ASCII art has always done — but here the "image" is not a photograph but a mathematical function.

## Colour Palette

Each cell's hue is `200 + val × 60` degrees (deep cyan at val=0, warm yellow-cream at val=1). The background lightness is `max(3, 8 + val × 10)%`, and the foreground character lightness is `20 + val × 60%` — so the entire cell, background and glyph alike, shifts in hue and brightness together. Low-value cells are near-black teal; high-value cells are bright warm cream with dense glyphs.

## ASCII Art as a Mathematical Display Technology

ASCII art originated as a workaround: terminal hardware could render characters but not arbitrary pixels, so artists mapped luminance to character density. The mapping was always arbitrary — whichever characters happened to fill the most ink were the brightest. This piece inverts the historical relationship: rather than reducing a raster image to characters, it starts with a mathematical object (a wave interference field) and uses characters as its natural display medium. The density ramp is not an approximation of something richer; it *is* the signal. The piece belongs to the lineage of generative mathematics — pen plotters, BASIC graphics, demoscene text-mode effects — that turns computational constraints into aesthetic properties.

## Animation

`requestAnimationFrame` advances `t = timestamp / 1000` each frame, capped at 60 fps. Because all four component waves are pure sinusoids, the animation is everywhere smooth — no discontinuities, no resets. The field ripples continuously.

## Files

- `index.html` — self-contained full-viewport canvas animation, no external dependencies
- `thumbnail.svg` — static 400×400 SVG snapshot at t=2.5 (50×40 character grid)
- `generate_thumbnail.py` — Python script that regenerates `thumbnail.svg`
- `README.md` — this file
