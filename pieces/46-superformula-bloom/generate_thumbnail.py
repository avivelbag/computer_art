"""Generate a static SVG thumbnail for piece 46 — Superformula Bloom.

Renders the Flower-5 waypoint (m=5, n1=3, n2=3, n3=3) with three concentric
copies at 100 %, 70 %, and 45 % scale using the rose/blush/mauve palette.
"""

import math
import pathlib

SAMPLES = 512
WIDTH   = 400
HEIGHT  = 400
CX      = WIDTH  / 2
CY      = HEIGHT / 2
RADIUS  = min(WIDTH, HEIGHT) * 0.44

# Flower-5 waypoint shown in the thumbnail.
M, N1, N2, N3 = 5, 3, 3, 3

SCALES  = [1.0, 0.70, 0.45]
STROKES = ["#d4a0b5", "#b5748e", "#8b4f6e"]
WIDTHS  = [1.0, 1.5, 2.0]


def r_super(theta: float, m: float, n1: float, n2: float, n3: float) -> float:
    """Gielis superformula r(θ) with a=b=1."""
    t1  = abs(math.cos(m * theta / 4)) ** n2
    t2  = abs(math.sin(m * theta / 4)) ** n3
    s   = t1 + t2
    return s ** (-1 / n1) if s > 0 else 0.0


def shape_points(
    m: float, n1: float, n2: float, n3: float, radius: float
) -> list[tuple[float, float]]:
    """Return SAMPLES+1 (x, y) pairs for the superformula, normalized to radius."""
    thetas = [2 * math.pi * i / SAMPLES for i in range(SAMPLES + 1)]
    rs     = [r_super(t, m, n1, n2, n3) for t in thetas]
    max_r  = max(rs) if rs else 1.0
    scale  = radius / max_r if max_r > 0 else 0.0
    return [
        (CX + r * scale * math.cos(theta), CY + r * scale * math.sin(theta))
        for theta, r in zip(thetas, rs)
    ]


def generate_svg() -> str:
    """Render three concentric Flower-5 outlines as a 400×400 SVG string."""
    parts: list[str] = [f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#fdf6f0"/>']
    for i, sc in enumerate(SCALES):
        pts       = shape_points(M, N1, N2, N3, RADIUS * sc)
        pts_str   = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        is_inner  = i == len(SCALES) - 1
        fill_attr = 'fill="#c47088" fill-opacity="0.07"' if is_inner else 'fill="none"'
        parts.append(
            f'<polygon points="{pts_str}" {fill_attr} '
            f'stroke="{STROKES[i]}" stroke-width="{WIDTHS[i]}" '
            f'stroke-linejoin="round"/>'
        )
    body = "\n  ".join(parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">\n'
        f'  {body}\n'
        f'</svg>'
    )


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(generate_svg(), encoding="utf-8")
    print(f"Written {out}")
