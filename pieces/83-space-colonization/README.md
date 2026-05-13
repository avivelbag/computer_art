# Piece 83 — Space Colonization

Organic vascular branching grown by the Runions space-colonization algorithm — the same process that shapes leaf venation, coral, and lung vasculature.

## Algorithm

A cloud of 500 attractor points is placed by rejection-sampling inside an ellipse centred above the root. A growing skeleton begins at a single root node. Each tick:

1. Every active attractor locates its nearest node within the influence radius (100 px).
2. Every node that attracted at least one attractor computes the average normalised direction toward those attractors and spawns a child node 5 px in that direction.
3. Any attractor within the kill distance (10 px) of any node is removed.

Growth continues until all attractors are consumed, then the canvas fades out and the simulation restarts.

## Stroke tapering

Line width follows `max(0.5, 4 × (1 − depth / MAX_DEPTH))` — 4 px at the root, hairline (0.5 px) at the deepest tips.

## Palette

Cream/ivory background (`#f8f4ec`) with warm terracotta strokes (`#c45e2a`).

## Animation

Growing phase runs until the attractor cloud is exhausted (~3–5 s depending on topology), followed by a 0.9 s hold and a 0.7 s fade before the next cycle begins.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG preview of the branching structure
- `README.md` — this file
