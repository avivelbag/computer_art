# Every Seed Knows

~800 seeds spiral outward from a common center, each placed by the golden angle (137.508°) — the same geometry a sunflower uses to pack its florets without gaps.

Position of seed n:

```
angle  = n × 137.508°
radius = √n × scale
x      = cx + radius × cos(angle)
y      = cy + radius × sin(angle)
```

## Why the golden angle prevents repeating spirals

137.508° equals 360° × (1 − 1/φ), where φ = (1 + √5)/2 is the golden ratio. Any rational fraction of a full turn would eventually repeat, producing radial spokes and bare sectors. The golden ratio is irrational — in fact, the "most irrational" number in the sense that its continued-fraction expansion [1; 1, 1, 1, …] converges as slowly as possible. This means successive seeds never land on top of earlier ones, and the disk fills uniformly with no clustering.

The visual result is two interlocking families of clockwise and counter-clockwise spirals — the Fibonacci spirals visible in pine cones, pineapples, and sunflower heads.

## Color palette

Five botanical swatches cycle by seed index (n mod 5), progressing outward in repeating rings:

| Index | Name        | Hex       | Role                        |
|-------|-------------|-----------|---------------------------  |
| 0     | Sage        | `#8fad75` | Living leaf, mid-green      |
| 1     | Ochre       | `#d4a853` | Sun-dried husk, warm gold   |
| 2     | Terracotta  | `#c2644f` | Oxidised earth, dried petal |
| 3     | Cream       | `#e8dcc8` | Seed membrane, light scatter|
| 4     | Charcoal    | `#7a7a7a` | Shadow and depth            |

Background `#0f1a14` is a deep botanical dark — the colour of a seed vault at night.

Dot radius scales linearly from 1.5 px at the center to 5.0 px at the outer edge, mimicking the way florets enlarge as they age and move outward.

## Technique

Static SVG — no JavaScript, no server. Open `piece.svg` directly in any browser.  
`generate.py` regenerates both `piece.svg` and `thumbnail.svg` from scratch: `python3 generate.py`

**Year:** 2026
