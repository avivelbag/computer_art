#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 127 — Voronoi Mosaic: Scattered Light.

Renders a Voronoi diagram on a 60×60 grid using brute-force nearest-seed
assignment. Each grid cell becomes a CELL×CELL pixel SVG rectangle. The
palette and border colour match index.html exactly. A fixed random seed
(127) makes the thumbnail reproducible across runs.
"""
import pathlib
import random

W = H = 480
GRID = 60       # cells per axis
CELL = W / GRID  # 8 px per cell in the SVG viewport
N = 200

# 12-tone jewel palette — identical to index.html PALETTE
PALETTE = [
    (0x0F, 0x52, 0xBA),  # sapphire
    (0x9B, 0x11, 0x1E),  # ruby
    (0xD2, 0x8C, 0x00),  # amber
    (0x00, 0x78, 0x50),  # jade
    (0x6E, 0x3C, 0xAA),  # amethyst
    (0x00, 0x64, 0x78),  # deep teal
    (0xC8, 0x50, 0x14),  # topaz
    (0x1E, 0x82, 0x6E),  # aquamarine
    (0xBE, 0x14, 0x5A),  # rose
    (0x32, 0xA0, 0x5A),  # emerald
    (0xB4, 0xA5, 0x00),  # gold
    (0x14, 0x32, 0x9B),  # cobalt
]

BORDER_COLOR = "#14141C"
BG_COLOR = "#0C0C14"


def make_seeds(n: int, rng: random.Random) -> list[tuple[float, float, int]]:
    """Return *n* (x, y, color_index) tuples in GRID-coordinate space.

    Positions are uniform random in [0, GRID). Color index cycles through
    PALETTE so every colour appears roughly equally.
    """
    return [
        (rng.random() * GRID, rng.random() * GRID, i % len(PALETTE))
        for i in range(n)
    ]


def nearest_seed_idx(
    cx: float,
    cy: float,
    seeds: list[tuple[float, float, int]],
) -> int:
    """Return the index of the seed nearest to (cx, cy) by squared distance."""
    best_dist = float("inf")
    best_idx = 0
    for idx, (sx, sy, _) in enumerate(seeds):
        d = (cx - sx) ** 2 + (cy - sy) ** 2
        if d < best_dist:
            best_dist = d
            best_idx = idx
    return best_idx


def voronoi_grid(seeds: list[tuple[float, float, int]]) -> list[list[int]]:
    """Return a GRID×GRID array of seed indices (colour assignments).

    Row-major order: result[row][col] is the seed index for that cell.
    Cell centre (col + 0.5, row + 0.5) is used for the distance query.
    """
    return [
        [nearest_seed_idx(cx + 0.5, cy + 0.5, seeds) for cx in range(GRID)]
        for cy in range(GRID)
    ]


def is_border(grid: list[list[int]], cy: int, cx: int) -> bool:
    """Return True when any 4-neighbour of (cx, cy) belongs to a different seed."""
    si = grid[cy][cx]
    return (
        (cx > 0 and grid[cy][cx - 1] != si)
        or (cx < GRID - 1 and grid[cy][cx + 1] != si)
        or (cy > 0 and grid[cy - 1][cx] != si)
        or (cy < GRID - 1 and grid[cy + 1][cx] != si)
    )


def generate_svg(n: int = N) -> str:
    """Return a complete SVG string of the Voronoi mosaic at W×H pixels.

    *n* controls how many seed points are placed. Passing n=0 returns a
    valid SVG with only the background rectangle (useful for edge-case tests).
    """
    rng = random.Random(127)  # fixed seed → reproducible thumbnail
    seeds = make_seeds(n, rng) if n > 0 else []

    if n == 0:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg"'
            f' width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'<rect width="{W}" height="{H}" fill="{BG_COLOR}"/>\n'
            f"</svg>"
        )

    grid = voronoi_grid(seeds)

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{BG_COLOR}"/>',
    ]

    for cy in range(GRID):
        for cx in range(GRID):
            si = grid[cy][cx]
            x = cx * CELL
            y = cy * CELL
            if is_border(grid, cy, cx):
                fill = BORDER_COLOR
            else:
                r, g, b = PALETTE[si % len(PALETTE)]
                fill = f"#{r:02X}{g:02X}{b:02X}"
            lines.append(
                f'<rect x="{x:.1f}" y="{y:.1f}"'
                f' width="{CELL:.1f}" height="{CELL:.1f}"'
                f' fill="{fill}"/>'
            )

    lines.append("</svg>")
    return "\n".join(lines)


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(generate_svg(), encoding="utf-8")
    print(f"Written {out}")
