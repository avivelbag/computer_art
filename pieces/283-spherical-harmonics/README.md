# Orbital Hymn — Spherical Harmonics

A displaced sphere whose radius at each point is `r(θ,φ) = 1 + a·|Y_l^m(θ,φ)|`, coloured by
the sign of the real spherical harmonic: warm amber for positive lobes, cool teal for negative
lobes.  The piece cycles through eight (l, m) pairs — mixing zonal, sectoral, and tesseral
harmonics — with smooth morphing between forms via linear interpolation of the vertex
displacements.

## Technique

- **Spherical harmonics** — real Y_l^m computed from the associated Legendre polynomial
  recurrence (Condon-Shortley convention), normalised to unit L² norm on the sphere.
- **Mesh** — 40 × 40 (θ, φ) triangle grid; each vertex displaced radially by `SCALE · |Y_l^m|`.
- **Rendering** — canvas 2D with painter's algorithm (faces sorted by average camera-space Z,
  drawn back-to-front).  Back-facing quads are culled; diffuse lighting uses the face-centre
  direction as an approximate surface normal.
- **Animation** — Y-axis auto-rotation at ~0.28 rad/s; morphing via a smoothstep lerp over 3 s
  with a 2 s hold on each form.  A pre-allocated Float32Array avoids per-frame GC allocation
  during the lerp.

## Harmonic sequence

| (l, m) | type       | notes                         |
|--------|------------|-------------------------------|
| (1, 0) | zonal      | two polar lobes (p_z orbital) |
| (2, 1) | tesseral   | four lobes in xz plane        |
| (3, 2) | tesseral   | six-lobe clover               |
| (4, 0) | zonal      | three-band layered form        |
| (4, 3) | sectoral   | eight azimuthal lobes          |
| (5, 2) | tesseral   | alien twelve-lobe form         |
| (3,−2) | tesseral   | rotated (3,2) by 45°           |
| (2,−1) | tesseral   | rotated (2,1) by 90°           |

## Palette

| element         | colour  |
|-----------------|---------|
| background      | #1a0a3a |
| positive lobes  | #f5a030 |
| negative lobes  | #30d0c0 |
| mesh edges      | rgba(255,255,255,0.04) |
