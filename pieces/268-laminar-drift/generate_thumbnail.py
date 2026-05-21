#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 268 — Laminar Drift.

Traces flow-field streamlines using the same sinusoidal noise function as
the browser animation and renders them as SVG line segments. Deterministic
via a fixed random seed. Uses only the Python standard library.
"""
import math
import pathlib
import random

W, H = 400, 400
TAU = math.tau
NOISE_SCALE = 0.003
TIME = 0.3
SPEED = 1.5
STEPS = 200
N_LINES = 120


def noise(x: float, y: float, t: float) -> float:
    """Three-octave sinusoidal noise matching the animation's noise function."""
    v, amp, freq = 0.0, 1.0, 1.0
    for i in range(3):
        v += amp * math.sin(freq * x + t) * math.cos(freq * y + t * 0.7 + i)
        amp *= 0.5
        freq *= 2.1
    return v


def angle_to_rgb(angle: float) -> tuple[int, int, int]:
    """Map angle in radians to the 3-stop gradient: deep teal → gold → warm white."""
    t = ((angle % TAU) + TAU) % TAU / TAU
    if t < 0.5:
        s = t * 2
        r = int(13  + s * (212 - 13))
        g = int(115 + s * (168 - 115))
        b = int(119 + s * (67  - 119))
    else:
        s = (t - 0.5) * 2
        r = int(212 + s * (255 - 212))
        g = int(168 + s * (245 - 168))
        b = int(67  + s * (230 - 67))
    return r, g, b


def trace_streamline(x0: float, y0: float) -> list[tuple[float, float, tuple[int, int, int]]]:
    """Follow the flow field from (x0, y0) for STEPS steps.

    Returns a list of (x, y, rgb) tuples where rgb is the color at that point
    derived from the heading angle.
    """
    pts = []
    x, y = x0, y0
    for _ in range(STEPS):
        angle = noise(x * NOISE_SCALE, y * NOISE_SCALE, TIME) * TAU
        pts.append((x, y, angle_to_rgb(angle)))
        x += math.cos(angle) * SPEED
        y += math.sin(angle) * SPEED
        x = x % W
        y = y % H
    return pts


def make_svg() -> str:
    """Return the full SVG markup for the flow-field thumbnail."""
    rng = random.Random(42)
    lines: list[str] = []

    for _ in range(N_LINES):
        x0 = rng.uniform(0, W)
        y0 = rng.uniform(0, H)
        pts = trace_streamline(x0, y0)

        for i in range(len(pts) - 1):
            x1, y1, col = pts[i]
            x2, y2, _ = pts[i + 1]
            if abs(x2 - x1) > W * 0.4 or abs(y2 - y1) > H * 0.4:
                continue
            r, g, b = col
            lines.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="rgb({r},{g},{b})" stroke-opacity="0.6" stroke-width="0.8"/>'
            )

    body = '\n  '.join(lines)
    return f'<svg width="400" height="400" viewBox="0 0 400 400"\n' \
           f'     xmlns="http://www.w3.org/2000/svg">\n' \
           f'  <rect width="400" height="400" fill="#1c1c1e"/>\n' \
           f'  {body}\n' \
           f'</svg>'


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(make_svg())
    print(f'Written {out}')
