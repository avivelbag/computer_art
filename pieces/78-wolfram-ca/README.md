# Wolfram Elementary CA — Rule 30 / 90 / 110

An elementary cellular automaton (CA) is a one-dimensional array of cells, each either alive (1) or dead (0). Every generation, the next state of each cell is read from an 8-entry lookup table indexed by the cell's left neighbor, itself, and its right neighbor — three bits = eight possible patterns = one byte of rule data. Wolfram numbered these lookup tables 0–255 by treating the eight output bits as an integer: Rule 30 is 00011110₂, Rule 90 is 01011010₂, Rule 110 is 01101110₂.

**Starting from a single live cell centered in the row** the three rules diverge radically:

- **Rule 30** — provably chaotic. The right-hand column passes standard randomness tests; Wolfram used it as a pseudorandom number generator. The pattern never repeats and shows no obvious structure despite emerging from a completely deterministic rule.
- **Rule 90** — equivalent to XOR of the left and right neighbors (center is ignored). Grows the Sierpiński triangle: a self-similar fractal visible at every scale, with triangular voids opening inside larger triangles.
- **Rule 110** — Turing-complete. Small periodic "gliders" emerge from the background and interact. The densest and most structured of the three.

**Display:** each row of pixels is one generation, growing downward. When the canvas fills, the pattern scrolls upward continuously — new generations appear at the bottom — creating an infinite-scroll feel. The initial condition is always a single live cell at the horizontal center.

**Cycling:** the piece cycles through all three rules on a 9-second timer. During the 2-second cross-fade a fresh Rule B pattern (starting from its own seed) grows from the bottom of the incoming canvas while Rule A fades out, so viewers always see a clean start for each rule.

**Palette:** amber (#ffb000) on near-black (#0a080f) for Rule 30; teal (#00c8aa) for Rule 90; rose (#dc4678) for Rule 110.

**Algorithm:** each new row is computed in O(W) time: for each cell index i, read neighbors at (i−1) mod W and (i+1) mod W, form the 3-bit pattern, and shift the rule byte by that amount. Scrolling uses `TypedArray.copyWithin()` — a single O(W·H) memmove — instead of repainting the canvas. An off-screen `ImageData` receives pixel writes; the main canvas scales it to fill the viewport via `drawImage`.

Built with plain Canvas 2D API and `requestAnimationFrame`. No external libraries.
