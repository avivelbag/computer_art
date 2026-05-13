# Piece 115 — The Field Remembers

4 000 particles drift through a smoothly-varying 2D simplex-noise vector field. Each particle leaves a faint ink trail; the cumulative marks build up into dense, flowing compositions before the canvas is cleared every 600 frames, beginning a new layer — a palimpsest of invisible forces.

## How it works

A 2D simplex-noise function is sampled at each particle's current position scaled by `NOISE_SCALE = 0.003`. The noise return value (in approximately `[−1, 1]`) is multiplied by `2π` to obtain a heading angle. The particle advances `1.5 px` in that direction every frame and wraps toroidally at all four canvas edges.

Time is introduced by shifting the y-axis noise sample by `frameCount × TIME_SCALE` (0.0005 per frame), causing the field to slowly evolve and preventing particles from locking into static attractors.

## Palette

The piece uses a four-colour pen-plotter palette:

| Role       | Hex       |
|------------|-----------|
| Background | `#f2ede4` |
| Navy ink   | `#1a2744` |
| Rust ink   | `#c0392b` |
| Sage ink   | `#4a7c59` |

Each particle is assigned one of the three ink colors at spawn. Trails are drawn at approximately 6% opacity (`0x0f` alpha) so individual marks are nearly invisible — pattern emerges only through accumulation.

## Periodical clearing

Every 600 frames the canvas is refilled with the cream background, erasing all accumulated marks and beginning a fresh layer. The timing is chosen so a single layer takes about 10 seconds at 60 fps, long enough to develop strong compositional density before the reset.

## Files

- `index.html` — self-contained canvas animation; no external dependencies
- `generate_thumbnail.py` — pure-stdlib Python; writes `thumbnail.png`
- `thumbnail.png` — static PNG snapshot generated at seed 42
- `README.md` — this file
