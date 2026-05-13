"""Generate the static SVG thumbnail for Piece 87 — Phyllotaxis.

Plots ~300 seeds using the Fermat spiral formula and the golden angle,
matching the visual style of the canvas animation in index.html.
"""

import math
import pathlib

PIECE_DIR = pathlib.Path(__file__).parent

GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # ≈ 2.39996 rad

N = 300
SIZE = 400
SPACING = 8.0
BG = "#1a0800"

PALETTE = [
    (245, 166, 35),   # #F5A623 saffron (centre)
    (192, 86, 42),    # #C0562A copper
    (80, 20, 0),      # #501400 dark rust (edge)
]


def _lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t."""
    return a + (b - a) * t


def _color_at(norm: float) -> str:
    """Map a normalised radius value in [0, 1] to an RGB hex colour.

    Interpolates linearly through PALETTE: saffron at 0, dark rust at 1.

    Args:
        norm: normalised radius, clamped to [0, 1].

    Returns:
        Hex colour string, e.g. '#f5a623'.
    """
    t = max(0.0, min(1.0, norm))
    seg = (len(PALETTE) - 1) * t
    i = min(int(seg), len(PALETTE) - 2)
    lt = seg - i
    c0, c1 = PALETTE[i], PALETTE[i + 1]
    r = round(_lerp(c0[0], c1[0], lt))
    g = round(_lerp(c0[1], c1[1], lt))
    b = round(_lerp(c0[2], c1[2], lt))
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_svg(
    n: int = N,
    size: int = SIZE,
    spacing: float = SPACING,
    bg: str = BG,
    dot_r_max: float | None = None,
    dot_r_min: float | None = None,
) -> str:
    """Return a complete SVG document with n phyllotaxis dots.

    Uses the Fermat spiral formula: r = spacing * sqrt(i), θ = i * golden_angle.
    Dot colour encodes normalised radius (saffron → rust). Dot size decreases
    with distance from centre, matching real sunflower seed sizing.

    Args:
        n: number of seeds to place.
        size: square canvas dimension in pixels.
        spacing: radial scale factor (pixels per sqrt-unit).
        bg: background fill colour (hex string).
        dot_r_max: dot pixel radius at centre; defaults to size * 0.012.
        dot_r_min: dot pixel radius at edge; defaults to size * 0.003.

    Returns:
        Complete SVG document as a string.
    """
    cx = size / 2.0
    max_r = spacing * math.sqrt(max(n, 1))
    if dot_r_max is None:
        dot_r_max = size * 0.012
    if dot_r_min is None:
        dot_r_min = size * 0.003

    circles = []
    for i in range(n):
        r = spacing * math.sqrt(i)
        theta = i * GOLDEN_ANGLE
        x = cx + r * math.cos(theta)
        y = cx + r * math.sin(theta)
        norm_r = r / max_r
        color = _color_at(norm_r)
        dot_r = _lerp(dot_r_max, dot_r_min, norm_r)
        circles.append(
            f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="{dot_r:.2f}" fill="{color}"/>'
        )

    body = "\n".join(circles)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size}" width="{size}" height="{size}">\n'
        f'  <rect width="{size}" height="{size}" fill="{bg}"/>\n'
        f'{body}\n'
        f'</svg>'
    )


if __name__ == "__main__":
    svg = generate_svg()
    out = PIECE_DIR / "thumbnail.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
