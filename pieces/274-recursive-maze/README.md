# 274 — The Path Finds Itself

A recursive-backtracking depth-first search carves a perfect 40×40 maze cell by cell in real time, then a breadth-first wave sweeps through the cream passages to trace the single solution path in gold. The cycle — carve, solve, hold, fade, restart — runs continuously and produces a different maze on every loop.

## How it works

**Carving.** Iterative DFS starts at the top-left cell and maintains an explicit stack. At each step it picks a random unvisited neighbour, removes the shared wall, and pushes the neighbour. When no unvisited neighbour exists it backtracks by popping. The live animation shows the DFS tip in terracotta; completed cells turn cream. Because DFS produces a spanning tree of all 1,600 cells, the result is a _perfect_ maze — every cell is reachable from every other via exactly one path.

**Solving.** After carving completes, BFS fans out from (0, 0) following carved passages. The amber wave spreads until it dequeues the bottom-right corner, then immediately traces the solution path back to the start in gold.

**Rendering.** Each cell occupies a 20×20 px square on the 800×800 canvas. Its interior is an 16×16 px rectangle (2 px of dark charcoal border on every side). Carved passages are drawn as 4×16 or 16×4 px rectangles that bridge the 4-px gap between adjacent cell interiors, keeping wall lines hairline-thin and visually precise.

## Palette

| Role          | Colour             | Hex       |
|---------------|--------------------|-----------|
| Background    | Deep charcoal-brown| `#131008` |
| Carved passage| Warm cream         | `#ede5d0` |
| DFS tip       | Terracotta         | `#d4692a` |
| BFS wave      | Amber              | `#e8b04a` |
| Solution path | Gold               | `#f5d060` |

## Timing (at 60 fps)

| Phase   | Steps/frame | Duration    |
|---------|-------------|-------------|
| Carving | 4           | ≈ 6.7 s     |
| Solving | 6           | ≈ 1–3 s     |
| Tracing | 2           | ≈ 1–3 s     |
| Hold    | —           | 1.5 s       |
| Fade    | —           | ≈ 1 s       |

## Files

| File                    | Purpose                                              |
|-------------------------|------------------------------------------------------|
| `index.html`            | Self-contained animation — no external dependencies  |
| `generate_thumbnail.py` | Deterministic SVG thumbnail generator (stdlib only)  |
| `thumbnail.svg`         | Pre-generated 400×400 thumbnail (seed 42)            |
