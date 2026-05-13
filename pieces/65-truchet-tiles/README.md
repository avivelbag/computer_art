# Every Corner Has a Choice

**Technique:** canvas / Truchet tiles / Smith quarter-circle arc variant

Each square cell in a 30 × 30 grid holds one of two possible tiles.
In the **Smith (1987) variant** used here, each tile carries a pair of
quarter-circle arcs connecting the midpoints of adjacent edges:

- **Type 0** — arcs run top ↔ left (centre on the top-left corner) and
  bottom ↔ right (centre on the bottom-right corner).
- **Type 1** — arcs run top ↔ right (centre on the top-right corner) and
  left ↔ bottom (centre on the bottom-left corner).

The two types are mirror images of each other.  Because the arc radius
equals half the cell size, arcs always land exactly on edge midpoints.
Adjacent cells therefore connect seamlessly regardless of their types —
every arc segment continues smoothly into the next cell.

**Randomness and apparent flow** — each configuration is drawn from a
fresh uniform random seed: every cell independently flips a fair coin.
Yet the resulting image rarely *looks* uniform.  Local clusters of the
same tile type form straight corridors; clusters of mixed types spiral
into closed loops.  The eye traces rivers and eddies through purely
memoryless binary noise — a well-known perceptual property of Truchet
patterns first described by Sébastien Truchet in 1704 and revisited by
Cyril Smith in 1987.

**Interaction** — a new random seed crossfades in every four seconds.
Click anywhere to trigger an immediate reseed.  The transition uses an
ease-in-out curve so the labyrinthine paths dissolve and reform smoothly.

**Palette** — warm ivory (`#f5f0e8`) background with deep indigo
(`#1a1260`) arcs.  Two colours keep the topology readable without
distraction.
