"""Generate thumbnail.svg for piece 63 — Rhodonea.

Renders three concentric rose curves (k=3, k=2, k=5/2) in the same
gold-on-charcoal palette as the live canvas piece.  Run from any directory:

    python3 pieces/63-rhodonea/generate_thumbnail.py
"""

import math
import pathlib

SIZE   = 400
CX     = SIZE / 2
CY     = SIZE / 2
RADIUS = 175
POINTS = 2000

BG_COLOR     = "#1a1208"
STROKE_COLOR = "#d4a84b"


def rose_polyline(k: float, R: float, points: int = POINTS) -> list[tuple[float, float]]:
    """Return (x, y) sample points for r = cos(k·θ) at outer radius R.

    The sweep covers 2π·d where d is the denominator of the closest rational
    approximation k ≈ n/12 in lowest terms, clamped to [1, 12].
    """
    n  = round(k * 12)
    d  = 12
    g  = math.gcd(abs(n), d) if n != 0 else d
    nd = max(1, d // g)
    end  = 2 * math.pi * nd
    step = end / points
    coords = []
    for i in range(points + 1):
        theta = i * step
        r     = R * math.cos(k * theta)
        coords.append((CX + r * math.cos(theta), CY + r * math.sin(theta)))
    return coords


def polyline_to_svg(coords: list[tuple[float, float]], opacity: float, stroke_width: float) -> str:
    """Serialize a list of (x, y) tuples as an SVG <polyline> element."""
    pts_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in coords)
    return (
        f'  <polyline points="{pts_str}" '
        f'fill="none" stroke="{STROKE_COLOR}" '
        f'stroke-width="{stroke_width}" opacity="{opacity}"/>'
    )


def build_svg() -> str:
    """Compose the full SVG string with three overlapping rhodonea curves."""
    roses = [
        (3.0,   RADIUS,       0.55, 0.8),
        (2.0,   RADIUS * 0.72, 0.40, 0.7),
        (2.5,   RADIUS * 0.44, 0.30, 0.7),
    ]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">',
        f'  <rect width="{SIZE}" height="{SIZE}" fill="{BG_COLOR}"/>',
    ]
    for k, R, opacity, sw in roses:
        coords = rose_polyline(k, R)
        lines.append(polyline_to_svg(coords, opacity, sw))
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    svg = build_svg()
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg)
    print(f"wrote {out}")
