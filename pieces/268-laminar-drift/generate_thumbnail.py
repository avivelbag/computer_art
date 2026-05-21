#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 268 — Laminar Drift.

Traces flow-field streamlines using the same sinusoidal noise function as
the browser animation and renders them as SVG polylines — one per streamline,
one stroke color per streamline derived from its starting angle. Using polylines
instead of per-segment <line> elements reduces file size from ~2.7 MB to ~40 KB
while still representing the flow-field structure faithfully.

Uses only the Python standard library. Deterministic via a fixed random seed.
"""
import math
import pathlib
import random

W, H = 400, 400
TAU = math.tau
NOISE_SCALE = 0.003
TIME = 0.3
SPEED = 1.5
STEPS = 80
N_LINES = 60


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


def trace_streamline(x0: float, y0: float) -> list[str]:
    """Follow the flow field from (x0, y0) for up to STEPS steps.

    Returns a list of 'x,y' coordinate strings for the polyline points
    attribute. Stops early if the particle drifts far outside the canvas
    (no torus wrapping here — SVG clips to viewBox). The starting angle
    is also returned for coloring.
    """
    x, y = x0, y0
    pts = [f"{x:.0f},{y:.0f}"]
    for _ in range(STEPS):
        angle = noise(x * NOISE_SCALE, y * NOISE_SCALE, TIME) * TAU
        x += math.cos(angle) * SPEED
        y += math.sin(angle) * SPEED
        if x < -W * 0.5 or x > W * 1.5 or y < -H * 0.5 or y > H * 1.5:
            break
        pts.append(f"{x:.0f},{y:.0f}")
    return pts


def make_svg() -> str:
    """Return the full SVG markup for the flow-field thumbnail."""
    rng = random.Random(42)
    polylines: list[str] = []

    for _ in range(N_LINES):
        x0 = rng.uniform(0, W)
        y0 = rng.uniform(0, H)

        start_angle = noise(x0 * NOISE_SCALE, y0 * NOISE_SCALE, TIME) * TAU
        r, g, b = angle_to_rgb(start_angle)

        pts = trace_streamline(x0, y0)
        if len(pts) < 2:
            continue

        polylines.append(
            f'<polyline points="{" ".join(pts)}" fill="none" '
            f'stroke="rgb({r},{g},{b})" stroke-opacity="0.6" stroke-width="1"/>'
        )

    body = '\n  '.join(polylines)
    return (f'<svg width="400" height="400" viewBox="0 0 400 400"\n'
            f'     xmlns="http://www.w3.org/2000/svg">\n'
            f'  <rect width="400" height="400" fill="#1c1c1e"/>\n'
            f'  {body}\n'
            f'</svg>')


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(make_svg())
    size_kb = out.stat().st_size / 1024
    print(f'Written {out} ({size_kb:.1f} KB)')
