#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 41 — Clifford strange attractor.

Iterates the Clifford attractor for ITERATIONS steps (after a burn-in warmup),
samples every SAMPLE_STEP-th point, and renders each as a small SVG circle.
Warm amber dots on a near-black background capture the characteristic shape.
"""

import math
import pathlib

A, B, C, D = -1.4, 1.6, 1.0, 0.7
W, H = 400, 400
COORD_MIN = -2.5
COORD_RANGE = 5.0
BG = "#0a0600"
DOT_COLOR = "#FF9030"

BURN_IN = 500
ITERATIONS = 15_000
SAMPLE_STEP = 5


def clifford_step(x: float, y: float) -> tuple[float, float]:
    """One Clifford attractor iteration with module-level parameters A, B, C, D."""
    return (
        math.sin(A * y) + C * math.cos(A * x),
        math.sin(B * x) + D * math.cos(B * y),
    )


def iterate_attractor(
    n_iter: int, burn_in: int, step: int
) -> list[tuple[float, float]]:
    """Return sampled (x, y) pairs from the Clifford attractor.

    Runs burn_in warm-up steps to reach the attractor, then collects one point
    every step-th iteration from n_iter total steps, returning n_iter // step
    points.
    """
    x, y = 0.5, 0.5
    for _ in range(burn_in):
        x, y = clifford_step(x, y)
    pts: list[tuple[float, float]] = []
    for i in range(n_iter):
        x, y = clifford_step(x, y)
        if i % step == 0:
            pts.append((x, y))
    return pts


def to_svg_coords(
    ax: float, ay: float, w: int = W, h: int = H
) -> tuple[float, float]:
    """Map Clifford attractor coordinates to SVG pixel coordinates."""
    return (ax - COORD_MIN) / COORD_RANGE * w, (ay - COORD_MIN) / COORD_RANGE * h


def generate_svg(n_points: int = ITERATIONS // SAMPLE_STEP) -> str:
    """Return an SVG string containing n_points attractor sample dots.

    When n_points is 0, returns a valid SVG with only the background rectangle.
    Each dot is a 1.4-px amber circle at 65% opacity; overlap between dots
    creates visually denser regions that reveal the attractor's shape.
    """
    pts = iterate_attractor(n_points * SAMPLE_STEP, BURN_IN, SAMPLE_STEP)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'  <rect width="{W}" height="{H}" fill="{BG}"/>',
    ]
    for ax, ay in pts:
        px, py = to_svg_coords(ax, ay)
        if 0 <= px < W and 0 <= py < H:
            lines.append(
                f'  <circle cx="{px:.1f}" cy="{py:.1f}"'
                f' r="1.4" fill="{DOT_COLOR}" opacity="0.65"/>'
            )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    svg = generate_svg()
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg)
    dot_count = svg.count("<circle")
    print(f"Wrote {out} ({dot_count} circles, {out.stat().st_size} bytes)")
