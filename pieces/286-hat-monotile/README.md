# The Spectre's Floor — Hat Monotile Aperiodic Tiling

An aperiodic plane tiling generated entirely from the Hat monotile — the first
single shape proven (Smith, Myers, Kaplan & Goodman-Strauss 2023) to tile the
plane without ever repeating, using only itself and its mirror image.

## Technique

- **Hat geometry** — the Hat's 13 vertices are hard-coded in triangular-grid
  coordinates `(q, r)` and converted to Cartesian via `x = q + r/2`,
  `y = r·√3/2`.
- **Substitution inflation** — the tiling grows through 4 levels of the Hat
  substitution rule: one parent Hat expands into 5 child Hats (4 in the H-role,
  1 reflected T-role), each scaled by `1/(1+√3) ≈ 0.366`. All placement is
  tracked as affine transforms composed through the recursion tree so leaf tiles
  are emitted directly in canvas coordinates.
- **Role coloring** — each leaf tile is colored by its substitution role (H, T,
  F, P), making the self-similar hierarchical structure visually legible.
- **Slow pan** — a gentle Lissajous-phase viewport drift with period ~40 s
  reveals additional aperiodic structure without distorting the tiling geometry.
- **No external libraries** — all Hat geometry and affine arithmetic computed
  from scratch in plain JS.

## Palette

| role | color        | hex       |
|------|-------------|-----------|
| H    | terracotta  | `#c4623a` |
| T    | sandy       | `#e8c88a` |
| F    | slate       | `#6a8fa8` |
| P    | cream       | `#f5f0e8` |
| bg   | dark umber  | `#1e1a14` |

## References

- Smith, Myers, Kaplan, Goodman-Strauss (2023). *An aperiodic monotile.*
  arXiv:2303.10798.
