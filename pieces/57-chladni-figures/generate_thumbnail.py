"""Generate thumbnail.svg for piece 57-chladni-figures.

Renders the (3,2) Chladni mode on a 400×400 grid as coloured SVG rectangles.
Pixels near the nodal line (|f| < threshold) are drawn in cyan/white with a
glow filter; all others are left as the deep indigo background.
"""
import math
import pathlib

SIZE     = 400
CELL     = 2           # px size of each SVG rect
GRID     = SIZE // CELL
M, N     = 3, 2
T_BASE   = 0.12        # nodal line threshold
BG       = "#0d0d2b"
CYAN     = "#00e5ff"
WHITE    = "#e0f8ff"

OUT = pathlib.Path(__file__).parent / "thumbnail.svg"


def chladni(m: int, n: int, x: float, y: float) -> float:
    """Chladni eigenmode on [-1,1]×[-1,1].

    Returns the signed value of the antisymmetric standing-wave function.
    The zero set is the nodal pattern — lines where the plate is still.
    """
    return (math.cos(m * math.pi * x) * math.cos(n * math.pi * y) -
            math.cos(n * math.pi * x) * math.cos(m * math.pi * y))


def main() -> None:
    cyan_rects  = []
    white_rects = []

    for gy in range(GRID):
        y = (gy / (GRID - 1)) * 2 - 1
        for gx in range(GRID):
            x  = (gx / (GRID - 1)) * 2 - 1
            af = abs(chladni(M, N, x, y))
            if af >= T_BASE:
                continue
            b  = 1 - af / T_BASE
            px = gx * CELL
            py = gy * CELL
            rect = f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}"/>'
            if b > 0.55:
                white_rects.append(rect)
            else:
                cyan_rects.append(rect)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}"'
        f' viewBox="0 0 {SIZE} {SIZE}">',
        "  <defs>",
        '    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">',
        '      <feGaussianBlur stdDeviation="1.5" result="b"/>',
        "      <feMerge><feMergeNode in=\"b\"/><feMergeNode in=\"SourceGraphic\"/></feMerge>",
        "    </filter>",
        "  </defs>",
        f'  <rect width="{SIZE}" height="{SIZE}" fill="{BG}"/>',
        f'  <g fill="{CYAN}" filter="url(#glow)">',
    ]
    lines.extend(f"    {r}" for r in cyan_rects)
    lines.append("  </g>")
    lines.append(f'  <g fill="{WHITE}">')
    lines.extend(f"    {r}" for r in white_rects)
    lines.append("  </g>")
    lines.append("</svg>")

    OUT.write_text("\n".join(lines) + "\n")
    print(f"Wrote {len(cyan_rects) + len(white_rects)} rects → {OUT}")


if __name__ == "__main__":
    main()
