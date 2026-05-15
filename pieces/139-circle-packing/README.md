# Piece 139 — Circle Packing: Every Gap Has a Name

A **greedy largest-empty-circle** algorithm iteratively fills an 800×800 canvas with
non-overlapping circles, always placing the biggest circle that fits in the remaining
open space, producing an organic mosaic that is visually compelling at every stage
of completion.

## How it differs from Piece 39 (Apollonian Gasket)

Piece 39 (`39-apollonian-gasket`) uses **Descartes' Circle Theorem** — a deterministic
algebraic method that constructs tangent circles in specific interstices. This piece
uses a **stochastic greedy sampling** approach: at each step, N random candidate
centers are sampled and the one with the largest clearance radius wins. The result is
a statistically uniform packing rather than a fractal one.

## Algorithm

1. Sample `N_CANDIDATES = 200` random center points on the canvas.
2. For each candidate, compute its **clearance radius** — the distance to the nearest
   obstacle (canvas edge or placed circle's perimeter).
3. Place the candidate with the largest clearance.
4. Repeat until the best clearance falls below `MIN_R = 2 px`.

Clearance at point (cx, cy):

```
r = min(cx, cy, W − cx, H − cy)
for each placed circle c:
    r = min(r, dist(candidate, c.center) − c.r)
```

## Coloring

Each circle is colored by its log-radius, normalized across the full radius range:

```
t = (log(r) − log(MIN_R)) / (log(maxR) − log(MIN_R))
```

| t | color |
|---|-------|
| 0 | deep teal `rgb(13, 59, 79)` — smallest circles |
| 0.5 | amber `rgb(232, 160, 32)` |
| 1 | cream `rgb(245, 240, 200)` — largest circles |

## Animation

- `CIRCLES_PER_FRAME = 20` circles placed per `requestAnimationFrame` tick.
- The filling is visibly animated: large cream circles appear first, then amber
  medium circles, then tiny teal circles densify the gaps.
- After the packing completes, the canvas pauses for `RESTART_DELAY_MS = 3000 ms`
  then resets with a fresh random packing (seeded by `Math.random()`).

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG of a representative packed-circle composition (300×300)
- `generate_thumbnail.py` — Python script that reproduces the thumbnail
- `README.md` — this file
