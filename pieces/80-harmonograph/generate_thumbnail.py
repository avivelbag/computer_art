"""Generate a static SVG thumbnail for Piece 80 — Harmonograph.

Simulates the same damped-pendulum equations used in index.html for the
first preset (3:2 frequency ratio, warm cream on near-black) and writes
the resulting polyline path to thumbnail.svg.
"""

import math
import pathlib

PIECE_DIR = pathlib.Path(__file__).parent

W, H   = 400, 400
CX, CY = 200, 200
SCALE  = 170
BG     = "#0d0d0d"
FG     = "#f5e6c8"

# Preset 0 parameters (3:2 frequency ratio).
A1, F1, P1, D1 = 0.85, 3.0, math.pi / 4, 0.003
A2, F2, P2, D2 = 0.10, 2.0, math.pi / 3, 0.005
B1, G1, E1     = 0.90, 2.0, 0.003
T_MAX          = 1000


def harmonograph_points(steps: int = 4000) -> list[tuple[float, float]]:
    """Return pixel coordinates tracing the harmonograph figure.

    Evaluates:
        x(t) = A1*sin(F1*t + P1)*exp(-D1*t) + A2*sin(F2*t + P2)*exp(-D2*t)
        y(t) = B1*sin(G1*t)*exp(-E1*t)

    for t uniformly spaced from 0 to T_MAX, then maps into pixel space
    centred at (CX, CY) with the given SCALE.

    Args:
        steps: number of line segments (returns steps+1 points).

    Returns:
        List of (px, py) tuples in pixel coordinates.
    """
    pts = []
    for i in range(steps + 1):
        t   = (i / steps) * T_MAX
        ex  = math.exp(-D1 * t)
        ey  = math.exp(-D2 * t)
        ez  = math.exp(-E1 * t)
        x   = A1 * math.sin(F1 * t + P1) * ex + A2 * math.sin(F2 * t + P2) * ey
        y   = B1 * math.sin(G1 * t) * ez
        pts.append((CX + x * SCALE, CY + y * SCALE))
    return pts


def points_to_svg_polyline(pts: list[tuple[float, float]]) -> str:
    """Convert a list of (x, y) pairs to a SVG polyline points string.

    Args:
        pts: sequence of (x, y) pixel coordinates.

    Returns:
        Space-separated "x.xx,y.yy" pairs suitable for a polyline points= attribute.
    """
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def generate_svg() -> str:
    """Return a complete SVG document string for the harmonograph thumbnail.

    Uses the first preset (3:2 ratio, warm cream stroke on near-black ground).
    """
    pts   = harmonograph_points()
    pdata = points_to_svg_polyline(pts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
        f'  <rect width="{W}" height="{H}" fill="{BG}"/>\n'
        f'  <polyline points="{pdata}" fill="none" stroke="{FG}" '
        f'stroke-width="1.2" stroke-linejoin="round" stroke-linecap="round" '
        f'opacity="0.85"/>\n'
        f'</svg>'
    )


if __name__ == "__main__":
    svg = generate_svg()
    out = PIECE_DIR / "thumbnail.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
