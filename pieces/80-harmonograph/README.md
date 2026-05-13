# Piece 80 — Harmonograph

Damped-pendulum Lissajous line art rendered live in-browser on a `<canvas>`.

## Equations

The pen position at time *t* is determined by two coupled damped pendulums on the
x-axis and one on the y-axis:

```
x(t) = A1·sin(f1·t + φ1)·exp(−d1·t)  +  A2·sin(f2·t + φ2)·exp(−d2·t)
y(t) = B1·sin(g1·t)·exp(−e1·t)
```

Frequency ratios f1:g1 are chosen from simple rationals — 3:2, 5:4, 5:3, 7:4, 1:1 —
so each preset produces a recognisable Lissajous-family figure.  Damping constants
d ∈ [0.002, 0.006] cause the trace to spiral inward over the T_MAX = 1000 time span.

## Animation

- 100 000 steps drawn over 8 seconds via `requestAnimationFrame`.
- Stroke is split into segments of 500 points; each segment's `lineWidth` follows the
  dominant damping envelope (`MIN_WIDTH + (MAX_WIDTH − MIN_WIDTH)·exp(−d1·t)`), so
  strokes taper from 2.5 px down to 0.15 px as the figure decays.
- `globalAlpha 0.6` lets overlapping passes stack naturally to build density.
- After the figure completes it holds for 1.5 s then cross-fades into the next preset.

## Presets

| # | Ratio f1:g1 | Frequencies          | Description                              |
|---|-------------|----------------------|------------------------------------------|
| 1 | 3:2         | f1=3, g1=2           | Double-lobed harmonograph, warm cream on near-black |
| 2 | 5:4         | f1=5, g1=4           | Four-lobe figure, chalk white on deep black |
| 3 | 5:3         | f1=5, g1=3           | Asymmetric star-like figure, amber on near-black |
| 4 | 7:4         | f1=7, g1=4           | Complex multi-petal, golden on deep black |
| 5 | 1:1 (det.)  | f1=1, g1=1.001       | Precessing ellipse (Lissajous pendulum), bright white on near-black |

## Palette

Near-black backgrounds (`#0d0d0d`, `#0a0a0f`) with a single-colour stroke per preset:
warm cream (`#f5e6c8`), chalk white (`#e8e0d0`), amber (`#d4a836`), golden (`#e8c890`),
bright white (`#f0f0e8`).

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG of the 3:2 preset after full damping decay
- `generate_thumbnail.py` — Python script that regenerates `thumbnail.svg`
- `README.md` — this file
