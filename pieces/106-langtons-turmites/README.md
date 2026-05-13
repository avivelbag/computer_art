# Piece 106 — Highway Builders: Langton's Ant and Turmite Variants

Five Langton's Ant / turmite agents share a single 512×512 toroidal grid, each driven by a different rule string and rendered in a distinct colour. The simulation starts in four quadrants plus the centre; ants build their characteristic highways until the structures grow large enough to collide.

## Langton's Ant

A Langton's Ant is a 2D Turing machine.  At each step:

1. Read the colour index *c* of the current cell.
2. Turn according to `rules[c % len]` — **R** = right 90°, **L** = left 90°, **U** = U-turn, **N** = straight ahead.
3. Advance the cell colour: `(c % len + 1) % len`.
4. Move one cell forward.

The grid wraps toroidally, so ants crossing any edge reappear on the opposite side.

## Rule Strings

| # | Rule   | Colours | Behaviour                                             |
|---|--------|---------|-------------------------------------------------------|
| 1 | `RL`   | 2       | Classic Langton. Chaotic start → diagonal highway ~10 000 steps. |
| 2 | `RLR`  | 3       | Slowly expanding spiral with symmetric lobes.         |
| 3 | `LLRR` | 4       | Square-symmetric pattern, grows in a blocky diamond.  |
| 4 | `RLLR` | 4       | Expanding rectangular ring structure.                 |
| 5 | `LRRL` | 4       | Pinwheel / rotational-symmetric fill.                 |

## Palette

Each ant owns a base hue; cells display a lightness proportional to their colour index, so freshly cycled-back cells (index 0) show a dim tint while high-index cells glow brightly.  Cross-ant interaction happens when one ant reads a cell whose colour index was set by another — the reading ant applies modulo against its own rule length, creating emergent interference patterns when highways meet.

## Performance

- Grid: 512×512 `Uint8Array` (cell colour) + `Uint8Array` (last-visitor owner)
- Canvas: 1 024×1 024 pixels (2 px per cell), CSS-scaled to `100vmin`
- 200 steps batched per `requestAnimationFrame` — highway structure emerges in ≈1 second
- Full `ImageData` buffer repaint each frame; alpha channel pre-filled to 255

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static pixel-art SVG preview showing five ant regions
- `README.md` — this file
