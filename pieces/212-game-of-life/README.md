# Game of Life — Four Rules, Infinite Complexity

Conway's Game of Life is the canonical example of emergence: four dead-simple birth and death rules applied simultaneously to every cell on an infinite grid produce gliders, oscillators, spaceships, and structures of arbitrary computational complexity.

## The Four Rules

Every cell is either alive or dead. At each generation, all cells update simultaneously:

1. A live cell with fewer than 2 live neighbors dies (underpopulation).
2. A live cell with 2 or 3 live neighbors survives to the next generation.
3. A live cell with more than 3 live neighbors dies (overpopulation).
4. A dead cell with exactly 3 live neighbors becomes alive (reproduction).

That is the entire rule set. There are no exceptions and no special cases.

## Controls

| Control | Effect |
|---------|--------|
| **Play / Pause** | Toggle the simulation |
| **Step** | Advance exactly one generation |
| **Clear** | Empty the grid |
| **Heat Map** | Tint live cells by age: amber-yellow (newborn) → deep red (long-lived) |
| **Click / drag on grid** | Toggle cells on or off |
| **Speed slider** | Set the simulation rate from 1 to 60 generations per second |
| **Presets** | Load a named pattern centered on the grid |

## Preset Patterns

**Glider** — A 5-cell pattern that travels diagonally across the grid, returning to its original shape every 4 generations. Gliders are the "bullets" used to build logic gates in Turing-complete constructions.

**Blinker** — A 3-cell oscillator that alternates between a horizontal and vertical bar with period 2. The simplest and most common oscillator.

**Pulsar** — A large period-3 oscillator with 48 live cells and 12-fold symmetry. One of the most visually striking patterns in the standard library.

**Glider Gun (Gosper)** — A period-30 oscillator discovered by Bill Gosper in 1970 that emits a new glider every 30 generations, refuting Conway's conjecture that no pattern could grow without bound. Placing this preset and letting it run fills the grid with gliders that collide and produce secondary structures.

**Random** — 30% of cells seeded at random, producing an initial chaotic phase that typically settles into a mixture of still lifes, blinkers, and occasional gliders.

## Implementation

The grid is a flat `Uint8Array` of 120 × 80 = 9,600 cells, wrapped toroidally so the left edge connects to the right and the top to the bottom. A second scratch buffer holds the next generation; the buffers swap each tick to avoid in-place updates altering the neighbor count mid-computation.

Rendering uses the Canvas `ImageData` API: every pixel is written directly into a typed array and pushed to the canvas with `putImageData` — faster than `fillRect` for large grids.

An `age` counter tracks how many consecutive generations each cell has been alive. In heat-map mode this counter drives a color ramp from bright amber-yellow (newborn) to deep red (long-lived), making the different temporal layers of the automaton visible at a glance.

## Pattern Recognition

The sidebar scans the grid every 5 generations for six named patterns: the Block and Beehive (still lifes), the Blinker, Toad, and Beacon (oscillators), and the Glider (spaceship). The scan checks all orientations of each pattern. The count shown is the number of distinct occurrences detected.

## Conway and Turing-Completeness

John Horton Conway (1937–2020) published Life in 1970. Within months, a global community had discovered gliders, guns, and infinite-growth patterns. By constructing logic gates from glider collisions, researchers proved Life is Turing-complete: any computation expressible as an algorithm can be carried out inside it. This means predicting the fate of an arbitrary Life pattern is undecidable — the same theoretical barrier as the halting problem.
