# 268 — Laminar Drift

4 000 particles follow a time-animated sinusoidal flow field across a dark charcoal canvas, threading from deep teal through gold into warm white as each particle's heading angle shifts with the evolving field.

## How it differs from 115 and 238

This gallery already contains two flow-field pieces:

- **115 — The Field Remembers** uses 2D simplex noise on a warm cream background (`#f2ede4`), assigning each particle a fixed pen-plotter ink color (navy, rust, sage) at spawn. The canvas is cleared every 600 frames, building palimpsest layers.
- **238 — Curl Noise: The River That Doesn't Repeat** derives velocity from the curl of a 3D value-noise scalar potential via central finite differences — a divergence-free field — on a deep-purple ground (`#0a0010`), coloring particles by their instantaneous speed.

This piece differs on every axis:

- **Noise construction**: three octaves of amplitude-halving, frequency-scaling sin/cos pairs — no simplex, no value-noise lookup table, no finite differences, no external library.
- **Background**: dark charcoal `#1c1c1e` — neither cream nor deep purple.
- **Color mapping**: heading angle → three-stop gradient (teal `#0d7377` → gold `#d4a843` → warm white `#fff5e6`), recomputed each frame as the field evolves.
- **Particle lifecycle**: each particle respawns at a random position after ~300 frames; there is no periodic canvas clear and no unlimited-lifetime drift.

## Technique

- **Noise**: `noise(x, y, t) = Σ amp·sin(freq·x + t)·cos(freq·y + 0.7t + i)` for 3 octaves, amp halving, freq scaling by 2.1.
- **Angle field**: `angle = noise(x·0.003, y·0.003, frame·0.0005) × 2π`. The time parameter acts as a z-slice through a 3D noise volume, shifting the field continuously.
- **Trails**: `rgba(28,28,30,0.03)` fill each frame dims old marks without full clears.
- **Torus topology**: particles wrap at all four canvas edges; wrap-crossing segments are skipped.

## Palette

| Stop | Color | Hex |
|------|-------|-----|
| 0 (angle 0) | Deep teal | `#0d7377` |
| 0.5 (angle π) | Gold | `#d4a843` |
| 1 (angle 2π) | Warm white | `#fff5e6` |

## Files

| File | Purpose |
|------|---------|
| `index.html` | Self-contained animation — no external dependencies |
| `generate_thumbnail.py` | Deterministic SVG thumbnail generator (stdlib only) |
| `thumbnail.svg` | Pre-generated 400×400 thumbnail |
