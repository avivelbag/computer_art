"""Generate thumbnail.svg for piece 50 — Spirograph: Closed and Infinite.

Renders a completed hypotrochoid using R=5, r=3, d=2.7 (rose on cream)
— the classic five-lobe spirograph preset — as a 400×400 SVG polyline.
"""

import math
import pathlib

TWO_PI = 2 * math.pi

WIDTH  = 400
HEIGHT = 400
CX     = WIDTH  / 2
CY     = HEIGHT / 2

R  = 5
r  = 3
DR = 0.90
BG = "#fdf6f0"
FG = "#c4706a"

STEPS_PER_TURN = 400


def gcd(a: int, b: int) -> int:
    """Euclidean GCD for positive integers."""
    return a if b == 0 else gcd(b, a % b)


def hypotrochoid_points(
    R: int, r: int, d: float, cx: float, cy: float, scale: float, steps: int
) -> list[tuple[float, float]]:
    """Return (x, y) canvas coordinates for a full hypotrochoid.

    The curve closes after n_turns = r/gcd(R,r) revolutions of the inner
    circle's centre, giving a parameter period of 2π·n_turns.

    Args:
        R: outer (fixed) circle radius (integer, arbitrary units).
        r: inner (rolling) circle radius (integer, same units).
        d: pen distance from inner-circle centre (same units).
        cx, cy: canvas centre in pixels.
        scale: pixels per unit radius.
        steps: total number of parameter steps over the full period.
    """
    g       = gcd(R, r)
    n_turns = r // g
    period  = TWO_PI * n_turns
    Rr      = R - r
    k       = Rr / r
    pts: list[tuple[float, float]] = []
    for i in range(steps + 1):
        t = (i / steps) * period
        x = cx + scale * (Rr * math.cos(t) + d * math.cos(k * t))
        y = cy + scale * (Rr * math.sin(t) - d * math.sin(k * t))
        pts.append((x, y))
    return pts


def generate_svg() -> str:
    """Build and return the thumbnail SVG as a string."""
    d       = DR * r
    g       = gcd(R, r)
    n_turns = r // g
    steps   = n_turns * STEPS_PER_TURN
    max_r   = (R - r) + d
    scale   = (min(WIDTH, HEIGHT) / 2 - 12) / max_r

    pts     = hypotrochoid_points(R, r, d, CX, CY, scale, steps)
    pts_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">\n'
        f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>\n'
        f'  <polyline points="{pts_str}" fill="none" stroke="{FG}" '
        f'stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>\n'
        f'</svg>'
    )


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(generate_svg(), encoding="utf-8")
    print(f"Written {out}")
