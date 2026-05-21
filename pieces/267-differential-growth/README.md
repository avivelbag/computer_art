# Differential Growth: Coral Maze

A closed curve that grows by repeatedly inserting new vertices at the midpoints of over-stretched edges. Each new vertex is repelled from every nearby node on the curve, preventing self-intersection, while a spring force pulls each node toward the midpoint of its two neighbours, keeping the boundary smooth. The result is a curve that behaves like the edge of a coral polyp or a lettuce leaf — forced to grow faster than the space it occupies, it crinkles into dense, space-filling folds.

## Simulation

Starting from a regular 16-sided polygon at radius 90 px, the algorithm runs one step per animation frame:

1. **Edge subdivision** — any edge longer than 10 px gains a new midpoint vertex.
2. **Repulsion** — every pair of non-adjacent nodes closer than 24 px is pushed apart by a short-range spring force, resolved in O(n) time via a spatial-hash grid.
3. **Smoothing** — each node is pulled toward the average position of its two neighbours by a mild spring (k = 0.35), rounding sharp kinks left by the repulsion pass.
4. **Boundary** — a soft circle of radius 360 px constrains nodes with a spring proportional to their excess distance, preventing the curve from growing past the canvas boundary.

The simulation runs until the curve reaches 3 000 nodes, at which point it fades to black over roughly 1.3 seconds and restarts from a fresh polygon with small random jitter on each vertex so no two cycles look identical.

## Palette

| Role | Hex |
|---|---|
| Background | `#050d14` (near-black teal) |
| Fill | `rgba(0, 80, 60, 0.22)` (translucent deep teal) |
| Glow stroke | `rgba(0, 210, 165, 0.20)` (wide, faint) |
| Crisp stroke | `#00c8a0` (bright cyan-teal) |

The dark ground and luminous cyan stroke echo deep-ocean bioluminescence and contrast with the geometric, angular palette of neighbouring pieces in the gallery.

## Connection to biology

Differential growth is the mechanism behind many organic forms: the ruffled edge of a leaf, brain coral folds, and intestinal villi all arise when a sheet or boundary grows faster at its edge than at its interior. The simulation here is a 1-D analogue — a closed curve rather than a 2-D surface — but the qualitative behaviour is the same: the curve crinkles because growth and self-avoidance compete.
