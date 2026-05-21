# Mondrian Recursion: The Rectangle That Cannot Stop

Binary space partitioning (BSP) recursively divides a rectangle into two children by placing a random dividing line — vertical or horizontal, biased by the cell's aspect ratio — at a ratio sampled from 0.5 ± 0.2 so that splits are organic rather than mechanical. The process continues until each region falls below a minimum size or a maximum recursion depth is reached, at which point it becomes a leaf and receives a colour from the palette.

The connection to Piet Mondrian is structural rather than literal: Mondrian's canonical works are compositions of axis-aligned rectangles separated by bold black lines, and BSP generates exactly that geometry — balanced, asymmetric, and surprisingly calm — but driven by a randomised algorithm instead of a painter's eye.

## Palette

Five curated colours replace Mondrian's primary triad with softer, less saturated alternatives:

| Name | Hex |
|------|-----|
| Dusty rose | `#c4888a` |
| Slate blue | `#5f8fa8` |
| Ochre | `#c8a84b` |
| Off-white | `#f2ede0` |
| Sage green | `#8aaf96` |

Adjacent cells (siblings in the BSP tree) are always assigned different colours. Thin near-black (`#1a1a1a`) borders separate every cell.

## Animation

Splits are revealed breadth-first — largest rectangles first — at 80 ms intervals so the viewer watches the composition assemble itself from coarse to fine. After the final leaf appears the piece holds for 4 seconds, then fades to neutral white and redraws with a new set of random splits.
