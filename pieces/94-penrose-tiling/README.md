# Piece 94 — Penrose Tiling: Fivefold Symmetry

An aperiodic P3 (rhombus) Penrose tiling grown from a ten-triangle sun by six generations of golden-ratio substitution deflation. The tiling fills an 800 × 800 canvas: thick rhombs in warm terracotta (#c84b31), thin rhombs in dusty sage (#7a9e7e), on a parchment background (#f5f0e8). The palette evokes Islamic geometric tilework.

## What Makes a Penrose Tiling

A Penrose P3 tiling uses exactly two tile shapes — a thick rhombus (interior angles 72°/108°) and a thin rhombus (36°/144°) — arrayed with strict matching rules that prevent any periodic translation. The result has **perfect fivefold rotational symmetry locally** yet never repeats globally, an impossibility for ordinary periodic tilings.

## Substitution / Deflation Algorithm

Each tile is decomposed into two **Robinson triangles**:

- **Type A** (acute, 36° apex): half of a thick rhombus
- **Type B** (obtuse, 108° apex): half of a thin rhombus

One deflation step replaces each triangle with smaller ones, scaled by 1/φ, using the substitution rules:

    A  →  A(C, P, B)  +  B(P, C, A)        where P = A + (B−A)/φ
    B  →  B(R, C, A)  +  B(Q, R, B)  +  A(R, Q, A)
                                             where Q = B + (A−B)/φ
                                                   R = B + (C−B)/φ

The golden ratio φ = (1+√5)/2 ≈ 1.618 determines every split point. After six deflations from a ten-triangle sun (≈ 2 300 triangles), the pattern fills the viewport completely with no gaps or overlaps.

## Triangle Count Growth

| Generations | Type-A count | Type-B count | Total |
|-------------|-------------|-------------|-------|
| 0 (sun)     | 10          | 0           | 10    |
| 1           | 10          | 10          | 20    |
| 2           | 20          | 30          | 50    |
| 3           | 50          | 70          | 120   |
| 4           | 120         | 190         | 310   |  (thumbnail)
| 5           | 310         | 500         | 810   |
| 6           | 810         | 1310        | 2120  |  (full piece)

The ratio B/A converges to φ as deflations increase — a mathematical fingerprint of the golden ratio embedded in the tiling structure.

## Why It Tiles Without Repeating

Each deflation replaces one tile size with φ-smaller tiles following deterministic rules. Because φ is irrational, no integer multiple of the small tile size equals any integer multiple of the large tile size. This incommensurability prevents any translational period from forming while still allowing every finite patch of the tiling to appear infinitely often elsewhere in the plane.

## Implementation

The JavaScript in `index.html` is entirely self-contained:

1. `makeSun(radius)` — builds the 10-triangle seed at the origin using complex-number-style arithmetic (polar coordinates via `Math.cos`/`Math.sin`)
2. `deflate(tris)` — one substitution step; complexity O(n)
3. All triangles pre-computed once, split into `thick` and `thin` arrays, then drawn with canvas path batching (one `beginPath`/`fill`/`stroke` call per colour group)

No external libraries. No WebGL. Static render — the geometry is the piece.

## Files

- `index.html` — self-contained canvas piece, no external dependencies
- `thumbnail.svg` — static SVG preview at four deflation generations
- `generate_thumbnail.py` — Python script that produced `thumbnail.svg`
- `README.md` — this file
