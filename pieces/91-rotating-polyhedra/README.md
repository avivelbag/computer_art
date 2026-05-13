# Piece 91 — Rotating Polyhedra: 3D Wireframe Pen-Plotter Projection

Three nested Platonic solids — tetrahedron, icosahedron, and dodecahedron — spin on slightly different axes and speeds, rendered as cream wireframes on an 800 × 800 deep-charcoal canvas. There is no WebGL; every vertex is transformed and projected with plain arithmetic.

## Polyhedra Shown

**Tetrahedron** (innermost, scale 0.38): 4 vertices, 6 edges. Vertices sit at the four sign-consistent corners of the cube — (1,1,1), (−1,−1,1), (−1,1,−1), (1,−1,−1) — normalized to the unit sphere by √3.

**Icosahedron** (middle, scale 0.68): 12 vertices, 30 edges. Vertices are all cyclic permutations of (0, ±1, ±φ) where φ = (1+√5)/2 ≈ 1.618 (the golden ratio), normalized to the unit sphere by √(1+φ²) ≈ 1.902.

**Dodecahedron** (outermost, scale 1.00): 20 vertices, 30 edges. Vertices are (±1, ±1, ±1) together with cyclic permutations of (0, ±1/φ, ±φ), all normalized by √3. The icosahedron and dodecahedron are dual polyhedra — each vertex of one corresponds to a face of the other — which is why they nest naturally in the same sphere.

## Perspective Projection Math

Standard pinhole (central) projection, camera fixed at (0, 0, d):

    sx = cx + fov × vx / (vz + d)
    sy = cy − fov × vy / (vz + d)

`fov = 400` px, `d = 3.5` (camera distance in unit-sphere radii), canvas centre `cx = cy = 400`. Dividing by `(vz + d)` rather than a constant `d` shrinks distant features — the standard perspective divide.

## Rotation

Each frame, two Euler angles accumulate (they are never clamped or taken mod 2π, so there is no wrap-around glitch):

    v' = Rx(0.4 · t · s) × Ry(t · s) × v

where `t` grows by 0.007 per frame (≈ 0.42 rad/s at 60 fps) and `s` is a per-solid speed multiplier: 2.1× for the tetrahedron, 1.3× for the icosahedron, 1.0× for the dodecahedron. The different speeds keep the three solids in constant relative motion, so the composition never visually repeats.

## Depth Cueing

Edge opacity is a linear remap of each edge's average z-value:

    alpha = 0.15 + 0.75 × (z_avg − z_min) / z_range

Edges whose midpoint has the largest z value (nearest the camera) are drawn at α ≈ 0.90; edges at the far side (smallest z) are drawn at α ≈ 0.15. `z_min` and `z_range` are recomputed each frame from the current rotated vertices so the remap always spans the full dynamic range.

## Why No Hidden-Line Removal

Hidden-line removal requires computing face visibility, clipping edges against occluding polygon boundaries, and sorting results — roughly 300 lines of computational geometry that would dominate the codebase. More importantly, full transparency is the aesthetic intent: the wireframe lets you see every edge of every face simultaneously, reading the solid's complete combinatorial structure as a transparent mathematical object. Depth cueing via alpha provides sufficient spatial legibility without hiding anything.

## Palette

Cream/off-white strokes `rgba(245, 240, 230, α)` on deep charcoal `#1c1c1e`. Line width 0.9 px keeps the drawing precise and plotter-like.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG preview at 45°/25° rotation
- `generate_thumbnail.py` — Python script that produced `thumbnail.svg`
- `README.md` — this file
