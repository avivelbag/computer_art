# 270 — Harmonograph: Where the Pendulums Rest

A two-pendulum harmonograph whose coupled oscillations decay slowly to stillness, tracing a dense spiralling figure on warm cream paper in deep indigo ink.

## How it differs from 80 — Harmonograph

Piece 80 cycles through five distinct Lissajous presets with a dark background and variable stroke weight that follows the damping envelope. This piece uses a single, carefully tuned parameter set with a warm cream paper ground (`#f5f0e8`), flat stroke weight, and a pen-plotter opacity model where overlapping strokes build up density rather than being explicitly weighted — the visual accumulation of ink.

## Technique

Four-oscillator parametric equations:

```
x(t) = A1·sin(f1·t + p1)·exp(−d1·t) + A2·sin(f2·t + p2)·exp(−d2·t)
y(t) = A3·sin(f3·t + p3)·exp(−d3·t) + A4·sin(f4·t + p4)·exp(−d4·t)
```

| Parameter | Value | Role |
|-----------|-------|------|
| f1 | 2.001 | slight irrationality keeps the figure from closing too early |
| f2 | 3.0 | integer ratio with f1 ≈ 2 creates a Lissajous 3:2 skeleton |
| f3 | 3.0 | — |
| f4 | 2.0 | — |
| p2 | π/2 | quarter-phase offset rotates the x-oscillator |
| p3 | π/4 | eighth-phase offset tilts the y-oscillator |
| d1–d4 | 0.0025 | slow decay — curve fills the canvas before settling |
| t ∈ | [0, 4000] | long enough for full decay to a point |

80 000 points are pre-computed once; each animation frame draws 80 points as a single canvas path segment. Translucency (opacity 0.6) lets crossing strokes darken naturally — pen-plotter density without explicit tracking. After the curve completes, the canvas fades back to background over 60 frames and the animation restarts from blank.

## Palette

| Role | Color | Hex |
|------|-------|-----|
| Paper | Warm cream | `#f5f0e8` |
| Ink | Deep indigo | `#1a1a2e` |

## Files

| File | Purpose |
|------|---------|
| `index.html` | Self-contained animation — no external dependencies |
| `generate_thumbnail.py` | Deterministic SVG thumbnail generator (stdlib only) |
| `thumbnail.svg` | Pre-generated 800×800 thumbnail (≈55 KB) |
