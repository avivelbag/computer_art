# The Grain That Broke the Symmetry

**Piece 90 — Abelian Sandpile Model**

Drop 65 536 grains at the center of a 401×401 grid. Any cell with four or more grains topples: it sheds four grains, one each to its four cardinal neighbors. Repeat until no cell has four or more grains.

The result is a fractal with exact 4-fold symmetry — deterministic order emerging from a single local rule applied millions of times. The four possible grain heights (0–3) map to four colors: deep navy, dusty rose, sage green, and warm white. The stained-glass tiling they produce is called *self-organized criticality*.

The animation shows the toppling front expanding outward in real time via `requestAnimationFrame`. Computation runs in chunked sweeps of 100 passes per frame so the browser stays responsive throughout. Click anywhere to restart.

**Technique:** Canvas / abelian sandpile / self-organized criticality / ImageData
