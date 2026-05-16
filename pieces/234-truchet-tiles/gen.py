"""Generate a quarter-circle Truchet tiling as a deterministic static SVG.

Each square cell is assigned one of two orientations via seeded random:
  A — arcs curve through the top-left and bottom-right corners
  B — arcs curve through the top-right and bottom-left corners

Adjacent tiles that share a matching edge midpoint merge visually into
continuous flowing curves — the Truchet effect. Two arc colors (indigo
for A, terracotta for B) let the eye follow each orientation's stream
independently across the grid.
"""

import pathlib
import random

COLS = 30
ROWS = 30
CELL = 20
SEED = 7
MARGIN = CELL
BG = "#f5f0e6"
COLOR_A = "#1e1b4b"
COLOR_B = "#7c3030"
STROKE_W = round(CELL * 0.18, 2)


def make_orientations(cols: int, rows: int, seed: int) -> list[list[int]]:
    """Return a grid[row][col] of 0 (orientation A) or 1 (B) via seeded random.

    Deterministic: same (cols, rows, seed) always produces the same grid.
    """
    rng = random.Random(seed)
    return [[rng.randint(0, 1) for _ in range(cols)] for _ in range(rows)]


def tile_paths(px: float, py: float, r: float, orient: int) -> tuple[str, str]:
    """Return two SVG arc path strings for one quarter-circle Truchet tile.

    px, py: pixel coordinates of the tile's top-left corner
    r:      arc radius, equal to cell / 2
    orient: 0 = orientation A, 1 = orientation B

    Orientation A — arcs curve through the top-left and bottom-right corners:
      Arc 1: top-midpoint (px+r, py)   → left-midpoint  (px,    py+r),   centre (px,    py)
      Arc 2: right-midpoint (px+2r, py+r) → bottom-midpoint (px+r, py+2r), centre (px+2r, py+2r)

    Orientation B — arcs curve through the top-right and bottom-left corners:
      Arc 1: top-midpoint (px+r, py)   → right-midpoint (px+2r, py+r),   centre (px+2r, py)
      Arc 2: left-midpoint (px, py+r)  → bottom-midpoint (px+r, py+2r),  centre (px,    py+2r)

    Sweep flags (SVG sweep-flag=1 is clockwise in screen space, y-axis down):
      A arc 1: centre at top-left,     start angle 0°,   end 90°  CW  → sweep=1
      A arc 2: centre at bottom-right, start angle 270°, end 180° CCW → sweep=0
      B arc 1: centre at top-right,    start angle 180°, end 90°  CCW → sweep=0
      B arc 2: centre at bottom-left,  start angle 270°, end 0°   CW  → sweep=1
    """
    if orient == 0:
        a1 = f"M {px + r},{py} A {r},{r} 0 0 1 {px},{py + r}"
        a2 = f"M {px + 2 * r},{py + r} A {r},{r} 0 0 0 {px + r},{py + 2 * r}"
    else:
        a1 = f"M {px + r},{py} A {r},{r} 0 0 0 {px + 2 * r},{py + r}"
        a2 = f"M {px},{py + r} A {r},{r} 0 0 1 {px + r},{py + 2 * r}"
    return a1, a2


def generate_svg(
    cols: int = COLS,
    rows: int = ROWS,
    cell: int = CELL,
    seed: int = SEED,
    bg: str = BG,
    color_a: str = COLOR_A,
    color_b: str = COLOR_B,
    stroke_w: float = STROKE_W,
    margin: int = MARGIN,
) -> str:
    """Return a self-contained SVG string of a Truchet quarter-circle tiling.

    Orientation-A arcs are painted color_a; orientation-B arcs are painted
    color_b. All arcs of the same color are emitted as a single <path> element
    with multiple M subpaths, which is valid SVG and minimises element count.
    stroke_w should be generous relative to cell (≥ 15 % of cell size) so the
    composition breathes and curves read as continuous lines.
    """
    orientations = make_orientations(cols, rows, seed)
    r = cell / 2
    w = cols * cell + 2 * margin
    h = rows * cell + 2 * margin

    paths_a: list[str] = []
    paths_b: list[str] = []

    for row in range(rows):
        for col in range(cols):
            px = margin + col * cell
            py = margin + row * cell
            arc1, arc2 = tile_paths(float(px), float(py), r, orientations[row][col])
            if orientations[row][col] == 0:
                paths_a.extend([arc1, arc2])
            else:
                paths_b.extend([arc1, arc2])

    def path_el(paths: list[str], color: str) -> str:
        d = " ".join(paths)
        return (
            f'  <path d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{stroke_w}" stroke-linecap="round"/>'
        )

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">',
        f'  <rect width="{w}" height="{h}" fill="{bg}"/>',
    ]
    if paths_a:
        lines.append(path_el(paths_a, color_a))
    if paths_b:
        lines.append(path_el(paths_b, color_b))
    lines.append("</svg>")
    return "\n".join(lines)


def main() -> None:
    """Write piece.svg and thumbnail.svg next to this script."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg()
    thumb = generate_svg(
        cols=15,
        rows=15,
        cell=14,
        margin=14,
        stroke_w=round(14 * 0.18, 2),
    )
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(f"piece.svg: {len(piece):,} bytes | thumbnail.svg: {len(thumb):,} bytes")


if __name__ == "__main__":
    main()
