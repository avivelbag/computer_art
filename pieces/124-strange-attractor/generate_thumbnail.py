#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 124 — Strange Attractor.

Iterates the Clifford attractor (a=−1.4, b=1.6, c=1.0, d=0.7), maps the
orbit to a 480×480 SVG viewport, and renders each point as a small circle
whose fill colour is interpolated from violet (low y) through sky-blue (mid y)
to gold (high y).  Uses only the standard library; no external dependencies.
"""
import math
import pathlib

W, H = 480, 480
MARGIN = 20
COORD_MIN = -2.5
COORD_RANGE = 5.0

A, B, C, D = -1.4, 1.6, 1.0, 0.7

BG = "#0d0820"
N_BURN = 500
N_POINTS = 2000
STEP = 5
RADIUS = 1.5


def clifford_step(x: float, y: float) -> tuple[float, float]:
    """One iteration of the Clifford attractor with the canonical parameters.

    Equations:
        x' = sin(a·y) + c·cos(a·x)
        y' = sin(b·x) + d·cos(b·y)
    """
    return (
        math.sin(A * y) + C * math.cos(A * x),
        math.sin(B * x) + D * math.cos(B * y),
    )


def iterate_attractor(n: int, burn: int, step: int) -> list[tuple[float, float]]:
    """Return *n* on-attractor points, discarding the first *burn* iterates.

    Every *step*-th point is collected so the sample is spread across the orbit.
    """
    x, y = 0.1, 0.1
    for _ in range(burn):
        x, y = clifford_step(x, y)
    pts = []
    collected = 0
    ticker = 0
    while collected < n:
        x, y = clifford_step(x, y)
        ticker += 1
        if ticker >= step:
            pts.append((x, y))
            collected += 1
            ticker = 0
    return pts


def to_svg_coords(ax: float, ay: float) -> tuple[float, float]:
    """Map an attractor coordinate to SVG pixel space with a small margin."""
    draw_w = W - 2 * MARGIN
    draw_h = H - 2 * MARGIN
    px = MARGIN + (ax - COORD_MIN) / COORD_RANGE * draw_w
    py = MARGIN + (ay - COORD_MIN) / COORD_RANGE * draw_h
    return px, py


_Y_LOW = -1.5
_Y_HIGH = 1.6


def _colour(ay: float) -> str:
    """Return an HTML hex colour interpolated from violet → sky-blue → gold.

    Normalises against the Clifford attractor's actual y-range (≈[−1.5, 1.6])
    rather than the full coordinate viewport, so the gradient spans the full
    violet→gold spectrum in the rendered thumbnail.

        t=0 → violet  rgb(100, 0, 200)
        t=0.5 → sky   rgb(0, 150, 255)
        t=1 → gold    rgb(255, 210, 0)
    """
    t = max(0.0, min(1.0, (ay - _Y_LOW) / (_Y_HIGH - _Y_LOW)))
    if t < 0.5:
        u = t * 2.0
        r = int(100 - 100 * u)
        g = int(150 * u)
        b = int(200 + 55 * u)
    else:
        u = (t - 0.5) * 2.0
        r = int(255 * u)
        g = int(150 + 60 * u)
        b = int(255 - 255 * u)
    return f"#{r:02X}{g:02X}{b:02X}"


def generate_svg(n_points: int = N_POINTS) -> str:
    """Return a complete SVG string showing *n_points* attractor orbit samples.

    The result is a valid XML document that can be written directly to a file.
    Passing n_points=0 returns a valid SVG with just the background rect.
    """
    pts = iterate_attractor(n_points, N_BURN, STEP) if n_points > 0 else []

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    ]

    for ax, ay in pts:
        sx, sy = to_svg_coords(ax, ay)
        col = _colour(ay)
        lines.append(
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}"'
            f' r="{RADIUS}" fill="{col}" fill-opacity="0.7"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def write_svg(path: str, svg: str) -> None:
    """Write *svg* to *path* as UTF-8 text."""
    pathlib.Path(path).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    write_svg(str(out), generate_svg())
    print(f"Written {out}")
