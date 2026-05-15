# Piece 167 — Everything Divides Evenly in the End

A recursive Mondrian-style rectangle subdivision where the canvas perpetually divides itself until every cell rests. Inspired by De Stijl — Piet Mondrian's reductive grid compositions — the algorithm splits each rectangle horizontally or vertically, biased toward the longer axis and toward golden-ratio (0.618 / 0.382) or rule-of-thirds (0.333 / 0.667) proportions. Recursion stops when any side falls below 90 px or the depth cap of 7 is reached.

Color follows Mondrian's "airy" principle: most cells rest in white or near-white, while two or three of the largest cells receive a primary color — cadmium red, ultramarine blue, or cadmium yellow. Primary colors are drawn from a shuffled list so no two consecutive compositions use the same hue assignment. The composition regenerates every 8–12 seconds; a one-second CSS opacity dissolve replaces the hard cut with a quiet breath before the next division begins.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static snapshot of a characteristic seven-cell composition
- `README.md` — this file
