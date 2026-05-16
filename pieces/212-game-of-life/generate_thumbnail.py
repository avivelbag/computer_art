#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 212 — Game of Life.

Renders the Gosper Glider Gun (36×9 cells) plus two fired gliders
on a near-black background in warm amber, matching the canvas palette.
"""
import pathlib

CELL = 6   # px per cell (5 drawn + 1 gap)
PAD  = 6   # canvas margin

BG   = "#0a0a12"
LIVE = "#c8a96e"   # amber — resting gun cells
SHOT = "#e8d070"   # bright yellow — fired glider cells

# Gosper Glider Gun cells as (col, row)
GUN = [
    (24, 0),
    (22, 1), (24, 1),
    (12, 2), (13, 2), (20, 2), (21, 2), (34, 2), (35, 2),
    (11, 3), (15, 3), (20, 3), (21, 3), (34, 3), (35, 3),
    (0,  4), (1,  4), (10, 4), (16, 4), (20, 4), (21, 4),
    (0,  5), (1,  5), (10, 5), (14, 5), (16, 5), (17, 5), (22, 5), (24, 5),
    (10, 6), (16, 6), (24, 6),
    (11, 7), (15, 7),
    (12, 8), (13, 8),
]


def glider_at(ox: int, oy: int) -> list[tuple[int, int]]:
    """Return the five cells of a SE-moving glider at offset (ox, oy)."""
    return [(ox+1, oy), (ox+2, oy+1), (ox, oy+2), (ox+1, oy+2), (ox+2, oy+2)]


# Two gliders to the right of the gun, far enough not to overlap
GLIDERS = glider_at(38, 1) + glider_at(43, 5)

GLIDER_SET = set(GLIDERS)


def render() -> str:
    """Build and return the SVG document string for the thumbnail."""
    all_cells = GUN + GLIDERS
    max_col   = max(c[0] for c in all_cells)
    max_row   = max(c[1] for c in all_cells)
    vw = (max_col + 1) * CELL + PAD * 2
    vh = (max_row + 1) * CELL + PAD * 2

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' viewBox="0 0 {vw} {vh}" width="{vw}" height="{vh}">',
        f'<rect width="{vw}" height="{vh}" fill="{BG}"/>',
    ]
    for (gx, gy) in all_cells:
        x     = gx * CELL + PAD
        y     = gy * CELL + PAD
        color = SHOT if (gx, gy) in GLIDER_SET else LIVE
        lines.append(f'<rect x="{x}" y="{y}" width="5" height="5" fill="{color}"/>')
    lines.append('</svg>')
    return '\n'.join(lines)


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(render())
    print(f'Written {out}')
