# Piece 50 — Spirograph: Closed and Infinite

A hypotrochoid cycles through six curated presets, each drawing a roulette
curve stroke by stroke before fading and handing off to the next. The loop is
seamless and never repeats the same palette twice in a row.

## What is a hypotrochoid?

A hypotrochoid is the path traced by a pen attached to a small circle of
radius *r* rolling inside a larger fixed circle of radius *R*. The pen sits
at distance *d* from the rolling circle's centre.

Parametric equations:

```
x(t) = (R−r)·cos(t) + d·cos((R−r)/r · t)
y(t) = (R−r)·sin(t) − d·sin((R−r)/r · t)
```

When *d = r* the inner circle has no slippage — this is the special case
called a hypocycloid, producing exactly *R/r* sharp cusps. Varying *d* away
from *r* smooths the cusps into loops (d < r) or inflated lobes (d > r).

## Closure

The curve closes after *n* full revolutions of the rolling circle's centre,
where *n = r / gcd(R, r)*. Choosing *R* and *r* to be ratios of small
integers (5:3, 7:2, 8:3, 11:4, 13:5, 9:4) keeps *n* small — at most 5
revolutions — so each curve completes quickly and cleanly.

| Preset | R  | r | gcd | n turns | approx petal count |
|--------|----|---|-----|---------|---------------------|
| 1      | 5  | 3 |  1  |    3    | 5                   |
| 2      | 7  | 2 |  1  |    2    | 7                   |
| 3      | 8  | 3 |  1  |    3    | 8                   |
| 4      | 11 | 4 |  1  |    4    | 11                  |
| 5      | 13 | 5 |  1  |    5    | 13                  |
| 6      | 9  | 4 |  1  |    4    | 9                   |

## Animation

1 500 parameter steps are allocated per revolution so each curve is
perfectly smooth. The drawing phase runs for 22 seconds, enough to see the
curve assemble one stroke at a time. After a 2-second hold the canvas fades
to the next preset's background colour over 1.2 seconds, then the next curve
begins from scratch. The cycle repeats infinitely.

No full-canvas redraw occurs during the drawing phase — only the newly added
segments are stroked per frame, so the canvas accumulates the curve at very
low cost.

## Palettes

| Preset | Background          | Stroke              |
|--------|---------------------|---------------------|
| 1      | `#fdf6f0` cream     | `#c4706a` rose      |
| 2      | `#0d2240` navy      | `#3ecabf` teal      |
| 3      | `#1c1c1c` charcoal  | `#d4a256` gold      |
| 4      | `#1a0a2e` deep plum | `#e891b4` pink      |
| 5      | `#0f2210` dark green| `#7ec86d` sage      |
| 6      | `#18000f` near-black| `#f0c060` amber     |

## Files

- `index.html` — animated canvas, self-contained, no external scripts
- `thumbnail.svg` — static completed R=5/r=3 hypotrochoid (400×400 px)
- `generate_thumbnail.py` — Python script that produced `thumbnail.svg`

**Year:** 2026
