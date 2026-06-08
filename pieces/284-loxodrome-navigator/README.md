# The Rhumb Lines — Loxodrome Navigator

A loxodrome (rhumb line) is a path of constant compass bearing on a sphere. Unlike a great circle,
it spirals toward the poles in a logarithmic curve rather than taking the shortest geodesic route.
Sixteen loxodromes at evenly-spaced bearings are traced on a slowly rotating wireframe globe.

## Technique

- **Loxodrome parametrization** — Mercator formula: `lat(t) = 2·atan(eᵗ) − π/2`,
  `lon(t) = lon₀ + t·tan(β)`, sampled over t ∈ [−4, 4] (covers ±88° latitude).
- **Projection** — each (lat, lon) point is converted to Cartesian coordinates on the unit sphere,
  rotated around the Y axis, and projected orthographically to (x, y) on the canvas. Only the
  front hemisphere (rotated z ≥ 0) is drawn; segments crossing to the back are clipped.
- **Wireframe grid** — latitude parallels every 30° and meridians every 30°, drawn at 15% opacity
  in dim slate (#2a3550) before the loxodrome curves.
- **Color** — each curve uses `hsl(bearing° × 2, 90%, 65%)`, sweeping the full visible spectrum
  across the 16 bearings (5.6° → 174.4°).

## Parameters

| parameter      | value                          |
|----------------|--------------------------------|
| curves         | 16                             |
| bearing range  | 5.6° – 174.4°, step 11.25°     |
| t range        | [−4, 4], 600 samples per curve |
| rotation speed | 0.25 rad/s                     |
| canvas size    | 700 × 700                      |

## Palette

| element    | colour                       |
|------------|------------------------------|
| background | #060a18 (deep navy)          |
| grid lines | #2a3550, α 0.15 (dim slate)  |
| curves     | hsl(bearing×2, 90%, 65%)    |
