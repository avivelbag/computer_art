# Piece 46 — Superformula Bloom

The Gielis superformula encodes an extraordinary range of natural shapes — flowers,
snowflakes, leaves, star polygons — in four parameters. Slowly morphing those parameters
through a hand-curated sequence reveals a continuous natural morphology.

## The mathematics

The polar superformula with a=b=1 is:

```
r(θ) = [ |cos(mθ/4)|^n2 + |sin(mθ/4)|^n3 ]^(−1/n1)
```

`m` controls rotational symmetry (m=5 → pentagonal, m=6 → hexagonal).
`n1` controls the overall roundness: large n1 compresses the radial range toward
a single value; n1=1 allows maximum spikiness. `n2` and `n3` bend the radial
profile; when they differ, the shape loses bilateral symmetry, producing leaf-like forms.

Six waypoints are interpolated in a seamless 30-second cycle:

| Waypoint   | m | n1  | n2  | n3  | Character           |
|------------|---|-----|-----|-----|---------------------|
| Flower 5   | 5 | 3   | 3   | 3   | 5-petal rose        |
| Star 6     | 6 | 2   | 4   | 4   | 6-point star        |
| Near-circle| 4 | 100 | 100 | 100 | rounded 4-fold form |
| Snowflake  | 6 | 1   | 0.5 | 0.5 | spiky hexagonal     |
| Leaf       | 2 | 1   | 1   | 0.5 | asymmetric leaf     |
| Koch-like  | 8 | 3   | 0.5 | 0.5 | 8-fold spiky star   |

Smoothstep interpolation (s = 3t² − 2t³) gives zero velocity at each waypoint
boundary, so no form rushes through another — each shape holds briefly, then
dissolves into the next.

## Depth layer

Three concentric copies at 100 %, 70 %, and 45 % of the base radius are drawn
from outermost to innermost. Stroke opacity increases toward the centre; the
innermost shape receives a translucent rose fill wash. The result resembles a
layered botanical illustration.

## What makes it surprising

A single closed-form equation draws a 5-petal rose, then morphs it continuously
into a 6-point star, a rounded form, a snowflake, a leaf, and an 8-fold spiky
star — and back to the flower, seamlessly. The transition is not a crossfade or
blend of images; the parameters literally slide from one natural archetype to
another, and the shape follows with mathematical inevitability. Watching petal
count change as a continuous parameter, rather than an integer jump, reveals
that the diversity of natural symmetries is a single connected space.

## Palette

| Role           | Colour                       |
|----------------|------------------------------|
| Background     | `#fdf6f0` warm cream         |
| Outer outline  | `#d4a0b5` light rose         |
| Mid outline    | `#b5748e` dusty blush        |
| Inner outline  | `#8b4f6e` dusty mauve        |
| Inner fill     | `rgba(196,112,138,0.07)`     |

## Files

- `generate_thumbnail.py` — renders the Flower-5 waypoint as a static SVG
- `thumbnail.svg` — 400×400 px static preview
- `index.html` — canvas animation, self-contained, no external scripts

**Year:** 2026
