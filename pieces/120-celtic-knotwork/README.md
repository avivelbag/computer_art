# Piece 120 — Celtic Knotwork: Over, Under, Forever

A (3, 5) torus knot projected to 2D and rendered as a Celtic interlace: one closed strand weaving over and under itself ten times, drawn in warm bronze on deep forest green. The knot slowly breathes — a gentle oscillating tilt changes which crossings pop forward and which recede.

## Algorithm

### The torus knot parametric equations

A (p, q) torus knot wraps p times around the large circle of a torus and q times around the tube. Its parametric form in 3D is:

```
x(t) = (R + r·cos(q·t)) · cos(p·t)
y(t) = (R + r·cos(q·t)) · sin(p·t)
z(t) = r · sin(q·t)
```

where R is the major radius, r the minor radius, and t ∈ [0, 2π).

For p = 3, q = 5, a single closed strand crosses itself exactly 10 times. The curve is sampled at 500 uniformly-spaced t values to give a polyline.

### Projecting to 2D and creating depth

The 3D curve is tilted slightly around the x-axis by a time-varying angle θ:

```
x_screen = x + CX
y_screen = y·cos(θ) − z·sin(θ) + CY
z_depth  = y·sin(θ) + z·cos(θ)
```

The z_depth value at each point determines which strand is "in front" at every crossing.

### Over/under crossing rendering

At each of the 10 crossings the piece uses a three-step paint trick:

1. **Draw the full strand** — shadow layer (dark bronze, slightly wider), main colour layer (bronze/gold), and a thin cream highlight down the centre of each segment. This creates the illusion of a round, shiny rope.
2. **Erase the under-strand** — wherever two segments of the curve come within a threshold distance in screen space, the one with the lower z_depth is "behind". A background-coloured stroke (slightly wider than the strand itself) is painted over it, cutting a clean gap.
3. **Redraw the over-strand** — all three layers (shadow, main, highlight) are repainted for the "over" segment, covering any gap area that the erase accidentally clipped.

Crossings are found by comparing 2D midpoints of all segment pairs separated by at least SKIP = 25 indices (to ignore adjacent segments). Multiple detections of the same physical crossing are merged using a spatial radius threshold.

### Animation

The tilt angle oscillates as `θ = 0.45 + 0.15·sin(t·0.00025)`, cycling approximately every 25 seconds. This rocks the knot gently so the crossing depths shift, making the strand appear to flow continuously.

## Palette

| Role | Hex | Description |
|------|-----|-------------|
| Background | `#1f3320` | Deep forest green |
| Shadow | `#7a4500` | Dark bronze (gives strand depth) |
| Strand | `#c8860a` | Warm bronze/gold |
| Highlight | `#f5e6b0` | Cream (top of the 3D rope) |

The three overlapping strokes (shadow wider, main, highlight narrower) create a convincing round-cable illusion without any 3D shader code.

## Files

- `index.html` — self-contained canvas animation; no external dependencies
- `generate_thumbnail.py` — pure-stdlib Python; writes `thumbnail.png` using disk-stamping rasterisation
- `thumbnail.png` — static 400×400 PNG snapshot at tilt = 0.45 radians
- `README.md` — this file
