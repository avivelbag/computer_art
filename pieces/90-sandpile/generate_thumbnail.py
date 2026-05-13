"""Generate an SVG thumbnail of the abelian sandpile model for Piece 90."""

import pathlib

PALETTE = {
    0: "#1a1a2e",  # deep navy  — height 0 (background / empty)
    1: "#c97b7b",  # dusty rose — height 1
    2: "#7ba87b",  # sage green — height 2
    3: "#f0ede0",  # warm white — height 3
}

DEFAULT_W       = 201
DEFAULT_H       = 201
DEFAULT_GRAINS  = 8192
DEFAULT_CELL_PX = 2


def compute_sandpile(w: int, h: int, cx: int, cy: int, n_grains: int) -> list:
    """
    Compute the stable abelian sandpile configuration on a w×h grid.

    Drops n_grains at cell (cx, cy) then topples until no interior cell
    holds ≥4 grains.  Each topple fires floor(v/4) times atomically:
    the cell loses 4·t grains and each von-Neumann neighbour gains t.
    Boundary cells (row/col 0 and w-1/h-1) act as sinks — they accumulate
    grains but never topple.  The abelian property guarantees the final
    stable configuration is unique regardless of toppling order.

    Returns a flat list of grain counts indexed row-major (grid[y*w + x]).
    """
    grid = [0] * (w * h)
    grid[cy * w + cx] = n_grains

    while True:
        changed = False
        for y in range(1, h - 1):
            row = y * w
            for x in range(1, w - 1):
                i = row + x
                v = grid[i]
                if v >= 4:
                    t       = v >> 2        # floor(v / 4) — batch all topplings
                    grid[i] = v - (t << 2)  # remainder: v mod 4
                    grid[i - 1] += t
                    grid[i + 1] += t
                    grid[i - w] += t
                    grid[i + w] += t
                    changed = True
        if not changed:
            break

    return grid


def generate_svg(
    w: int       = DEFAULT_W,
    h: int       = DEFAULT_H,
    grains: int  = DEFAULT_GRAINS,
    cell_px: int = DEFAULT_CELL_PX,
) -> str:
    """
    Compute the sandpile on a w×h grid and render it to an SVG string.

    Each cell maps to a cell_px × cell_px rectangle.  Consecutive cells of
    the same colour in the same row are merged into a single wider rect
    (run-length encoding) to keep SVG file size manageable.  Background
    cells (height 0) are skipped because the initial background rect covers
    them already.
    """
    cx, cy  = w // 2, h // 2
    grid    = compute_sandpile(w, h, cx, cy, grains)
    svg_w   = w * cell_px
    svg_h   = h * cell_px

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">',
        f'<rect width="{svg_w}" height="{svg_h}" fill="{PALETTE[0]}"/>',
    ]

    for y in range(h):
        row_y = y * cell_px
        x = 0
        while x < w:
            v = grid[y * w + x]
            height = min(v, 3)
            x_start = x
            # Extend run while same clamped height
            while x < w and min(grid[y * w + x], 3) == height:
                x += 1
            if height != 0:
                run_w = (x - x_start) * cell_px
                lines.append(
                    f'<rect x="{x_start * cell_px}" y="{row_y}" '
                    f'width="{run_w}" height="{cell_px}" fill="{PALETTE[height]}"/>'
                )

    lines.append("</svg>")
    return "\n".join(lines)


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    svg = generate_svg()
    out.write_text(svg)
    print(f"Written {out} ({len(svg):,} bytes, {svg.count('<rect')} rects)")
