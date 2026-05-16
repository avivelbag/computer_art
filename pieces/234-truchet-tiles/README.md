# Truchet Tiles: Continuity from Chance

A 30×30 grid of quarter-circle Truchet tiles rendered as a static SVG. Each cell is assigned one of two orientations by seeded random: arcs curving through the top-left and bottom-right corners (orientation A, painted deep indigo), or arcs curving through the top-right and bottom-left corners (orientation B, painted dark terracotta). Where adjacent cells share a matching edge midpoint the arcs merge into continuous flowing curves — large-scale structure emerging from purely local chance.

**Palette:** warm off-white background (#f5f0e6), deep indigo arcs (#1e1b4b), dark terracotta arcs (#7c3030). Three colors; tiles are not plain black and white.

**Technique:** SVG / quarter-circle Truchet / dual-color orientation mapping / seeded random / static generation / Python gen.py

The dual-color encoding differentiates this piece from the gallery's existing Truchet entries (piece 04 — single-color animated canvas on a dark background; piece 65 — Smith diagonal variant): coloring by orientation lets the viewer trace each arc-stream independently across the grid, revealing the underlying flow topology of the random tiling.

## Regenerating

```bash
python3 gen.py
```

Outputs `piece.svg` (30×30 grid, 640×640 px canvas) and `thumbnail.svg` (15×15 grid, 238×238 px).
