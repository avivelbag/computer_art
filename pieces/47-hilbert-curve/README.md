# Piece 47 — Every Point, Once

A Hilbert curve of order 6 fills a 64×64 grid with 4,096 cells. The animation
draws the curve stroke by stroke — one copper line snaking through every cell
exactly once — then pauses on the completed form before starting again.

## What is a space-filling curve?

A space-filling curve is a continuous path that visits every point in a
two-dimensional region. The Hilbert curve is the most famous example: at order
N it subdivides the plane into a 2^N × 2^N grid and threads a single
non-self-intersecting path through every cell.

Unlike a random walk, the path is completely deterministic. Every cell is
visited exactly once — no repetitions, no gaps — which is what makes the curve
"space-filling". As N → ∞ the path becomes infinitely long but still traverses
a finite square, which is one of the genuinely strange properties of
mathematical infinity.

## Why does order 6 give ~4,000 segments?

At order N the grid has 2^N × 2^N = 4^N cells, connected by 4^N − 1 segments.

| Order | Grid   | Points | Segments |
|-------|--------|--------|----------|
| 1     | 2×2    | 4      | 3        |
| 2     | 4×4    | 16     | 15       |
| 3     | 8×8    | 64     | 63       |
| 4     | 16×16  | 256    | 255      |
| 5     | 32×32  | 1,024  | 1,023    |
| 6     | 64×64  | 4,096  | 4,095    |

Order 6 sits at the edge of what a canvas can render clearly at 800×800 pixels:
each of the 64×64 = 4,096 cells is 12.5 px wide, and every cell receives
exactly one line segment.

## Why does it visit every point exactly once?

The Hilbert curve is constructed by a recursive subdivision rule. At each level
of recursion the square is divided into four quadrants, each containing a
quarter of the remaining points. The rule chooses a U-shaped connecting path
through the four quadrants that:

1. Enters at one corner of the full square,
2. visits all cells in the first quadrant,
3. connects to the second quadrant without backtracking,
4. continues through all four quadrants, and
5. exits at the adjacent corner.

Because the rule is applied identically at every level and the four quadrant
sub-curves are non-overlapping, the result is a single path with no repeated
cells and no gaps.

## Algorithm

Points are computed with the standard bit-manipulation method: for each index
`d` from 0 to N²−1, extract two bits at a time (a "quadrant code") and
apply a sequence of reflect-and-swap operations to accumulate the (x, y)
coordinates. This runs in O(log N) per point, making it trivial to precompute
all 4,096 positions before the animation begins.

## Animation

The 4,095 segments are drawn incrementally based on elapsed time. The full
curve appears over 50 seconds (≈ 82 segments per second), holds for 3 seconds,
then the canvas is cleared and the curve redraws from the beginning.

No full-canvas redraw occurs per frame — only the new segments added since the
last frame are stroked, so the canvas accumulates the curve cheaply.

## Palette

| Role       | Colour              |
|------------|---------------------|
| Background | `#1a0a2e` near-black deep purple |
| Stroke     | `#d4a256` copper / warm amber    |

## Files

- `index.html` — animated canvas, self-contained, no external scripts
- `thumbnail.svg` — static order-4 preview (255 segments, 400×400 px)

**Year:** 2026
