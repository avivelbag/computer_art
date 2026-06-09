# Piece 296 — Eightfold Path: Ammann-Beenker Quasicrystal Tiling

An aperiodic Ammann-Beenker tiling grown from an eight-rhombus octagonal seed by five rounds of substitution deflation. The tiling fills an 800 × 800 canvas: squares in deep ochre (#c8882a), rhombi in slate blue (#3a5a8a), on a warm cream background (#f5f0e8), separated by thin dark lines (#1a1a1a). The result exhibits exact 8-fold rotational symmetry at the center and quasiperiodic self-similarity at every scale.

## What Makes an Ammann-Beenker Tiling

The Ammann-Beenker tiling uses exactly two prototiles — a square and a 45°/135° rhombus, both with the same edge length — arranged by substitution rules that admit no translational period. The pattern has **perfect 8-fold rotational symmetry locally** yet never repeats globally, just as the Penrose tiling has 5-fold symmetry without periodicity.

The irrational scaling factor δ = 1 + √2 ≈ 2.414 (the silver ratio) plays the role that φ plays in Penrose tilings. Because δ is irrational, no integer multiple of the child tile edge equals any integer multiple of the parent edge, making any translational period impossible.

## Substitution / Deflation Rules

Starting from large tiles, each deflation step replaces every tile with smaller children scaled by 1/δ:

**Square → 5 children:**
- 1 smaller square (center, same orientation)
- 4 rhombi (one at each corner, acute tip pointing inward)

**Rhombus → 5 children:**
- 1 smaller rhombus (center, parallel to parent)
- 2 smaller squares (one at each acute 45° vertex)
- 2 smaller rhombi (one at each obtuse 135° vertex)

Each deflation multiplies the tile count by approximately δ² ≈ 5.83.

## Octagonal Seed

The initial seed is 8 rhombi arranged in a pinwheel around the origin, each rotated 45° from the last. This seed has exact 8-fold rotational symmetry (the dihedral group D₈), which is preserved under every deflation step, producing the characteristic octagonal symmetry at the center of the final tiling.

## Tile Count Growth

| Deflations | Squares | Rhombi | Total |
|------------|---------|--------|-------|
| 0 (seed)   | 0       | 8      | 8     |
| 1          | 16      | 24     | 40    |
| 2          | ~100    | ~200   | ~300  |
| 3          | ~580    | ~1160  | ~1740 |
| 4 (thumb)  | 1220    | 2456   | 3676  |
| 5 (piece)  | ~7100   | ~14300 | ~21400|

The ratio of rhombi to squares converges to 2 (= δ² - δ ≈ 2.414² - 2.414) as deflations increase — a mathematical fingerprint of the silver ratio embedded in the tiling's structure.

## Implementation

The JavaScript in `index.html` is entirely self-contained:

1. `makeOctagonalSeed(edge)` — builds the 8-rhombus octagonal seed at the origin
2. `inflateSquare(v, f, out)` — deflates one square into 5 child tiles
3. `inflateRhombus(v, f, out)` — deflates one rhombus into 5 child tiles
4. `inflate(tiles)` — one full deflation pass over all tiles; O(n)
5. All tiles pre-computed once, then drawn via canvas path operations

No external libraries. No WebGL. Static render — the geometric complexity is the piece.

## Files

- `index.html` — self-contained canvas piece, no external dependencies
- `thumbnail.svg` — static SVG preview at four deflation generations
- `generate_thumbnail.py` — Python script that produced `thumbnail.svg`
- `README.md` — this file
