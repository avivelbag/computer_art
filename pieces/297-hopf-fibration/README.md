# Piece 297 — Rings of the Fourth: Hopf Fibration

The Hopf fibration η: S³ → S² maps the 3-sphere onto the ordinary 2-sphere such that every point on S² has exactly one circle as its preimage. Projected stereographically into R³, these circles form interlocked rings that never intersect, arranged on nested tori colored from cool blue-green at the poles to warm amber at the equator.

## Mathematical Structure

A point on S³ is a unit quaternion (a, b, c, d) with a²+b²+c²+d²=1. The Hopf map sends it to:

```
h(a,b,c,d) = (2(ac+bd),  2(bc−ad),  a²+b²−c²−d²)  ∈ S²
```

For a base point expressed via spherical coordinates (φ, θ) as (sinφ cosθ, sinφ sinθ, cosφ) ∈ S², the complete fiber is the unit-speed circle:

```
q(t) = (cos(φ/2) e^{i(t+θ/2)},  sin(φ/2) e^{i(t−θ/2)})
```

written as four real components:

```
a(t) = cos(φ/2) cos(t + θ/2)
b(t) = cos(φ/2) sin(t + θ/2)
c(t) = sin(φ/2) cos(t − θ/2)
d(t) = sin(φ/2) sin(t − θ/2)
```

One can verify h(q(t)) = (sinφ cosθ, sinφ sinθ, cosφ) for all t — every point on the circle maps to the same base point on S².

## Stereographic Projection

Each S³ fiber is then mapped to R³ by stereographic projection from the south pole (0,0,0,1):

```
(a, b, c, d)  →  (a/(1−d),  b/(1−d),  c/(1−d))
```

This sends great circles on S³ to circles (or lines) in R³. Fibers at the same latitude φ all lie on a single torus in R³; fibers at different latitudes nest inside one another.

## Implementation

- **14 latitudes** (φ from 15° to 165°) × **18 longitudes** (θ = 0° … 360°) = **252 fibers**
- Each fiber sampled at **64 points** then drawn as a closed polyline
- **Y-axis rotation** at one full revolution per 20 seconds via `requestAnimationFrame`
- **Depth fading**: average post-rotation Z per fiber determines alpha (0.10 … 0.60)
- **Painter's algorithm**: fibers sorted back-to-front each frame so near rings occlude far ones
- PHI range [15°, 165°] avoids the stereographic singularity at the south pole (φ = 180°)
- All math is self-contained in under 180 lines of JavaScript; no external libraries

## Color Palette

| Region | Hex | Role |
|--------|-----|------|
| `#0a0a12` | near-black | background |
| `#d4832a` | amber | equatorial fibers (φ ≈ 90°) |
| `#2a8a9f` | blue-green | polar fibers (φ ≈ 0° or 180°) |

Color interpolates by `|cos(φ)|`: 1 at poles → teal, 0 at equator → amber.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static still frame at 0.35 radian Y-axis rotation (120 fibers)
- `generate_thumbnail.py` — Python script that produced `thumbnail.svg`
- `README.md` — this file
