# Through the Fourth Wall

A tesseract (4D hypercube) rotates simultaneously in two independent 4D planes,
projected through two perspective stages onto a 600×600 canvas.

## Geometry

The 16 vertices of a unit tesseract are all combinations of (±1, ±1, ±1, ±1).
Two vertices share an edge iff they differ in exactly one coordinate, yielding
exactly 32 edges. This is the standard combinatorial definition of the 4D
hypercube graph.

## Rotation

Two simultaneous 4D rotation planes drive the animation:

- **XW plane** at 0.007 rad/frame — mixes the x and w axes
- **YZ plane** at 0.011 rad/frame — mixes the y and z axes

The ratio 0.007/0.011 is irrational, so the combined motion is quasiperiodic
and never exactly repeats. Each rotation is a 4×4 matrix applied in sequence:

```
Rxw(θ): x' = x·cos θ − w·sin θ,  w' = x·sin θ + w·cos θ
Ryz(φ): y' = y·cos φ − z·sin φ,  z' = y·sin φ + z·cos φ
```

## Projection

Two-stage perspective projection reduces 4D to 2D:

1. **4D → 3D**: perspective factor `f4 = D4 / (D4 − w)` where `D4 = 2`. Each
   4D vertex `(x, y, z, w)` maps to 3D point `(x·f4, y·f4, z·f4)`.

2. **3D → 2D**: perspective factor `f3 = D3 / (D3 − z3)` where `D3 = 3`.
   Screen coordinates: `sx = cx + x3·f3·scale`, `sy = cy − y3·f3·scale`.

The scale factor of 168 px (≈ 28 % of the 600 px canvas) keeps the full
tesseract comfortably within the viewport at all rotation angles.

## Visual encoding

Edge colour and opacity encode the 4D w-depth of the edge (average w of its
two endpoints after rotation):

- **w = +1 (near)**: bright cyan `#00e5ff`, fully opaque
- **w = −1 (far)**: deep indigo `#1a0050`, ghostly (opacity 0.2)

The colour and opacity are linearly interpolated from `t = (w + 1) / 2 ∈ [0, 1]`.
This gives an immediate visual cue for which hypercube cells are "in front" in
the fourth dimension, analogous to depth-cued opacity in 3D wireframe rendering.

## Implementation

All 4D rotation matrices and projection math are implemented in plain JavaScript
with no external libraries. The animation loop uses `requestAnimationFrame` for
a seamless 60 fps loop. The total JS logic is under 70 lines.
