#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 292 — Ink Bloom.

Produces a static 400x400 SVG that evokes the swirling ink-in-water aesthetic
of the Navier-Stokes fluid simulation: four ink colors on black with radiating
Bezier curves suggesting vortex roll-up.
"""
import math
import pathlib
import random

SEED = 7
W, H = 400, 400
CX, CY = 200, 200

COLORS = [
    ('#3a0066', (0.25, 0.25)),
    ('#1040c0', (0.75, 0.25)),
    ('#c02060', (0.25, 0.75)),
    ('#d08000', (0.75, 0.75)),
]


def spiral_path(ox, oy, start_angle, turns, rng):
    """Return an SVG path string for a loose spiral from (ox, oy).

    Uses cubic Bezier segments to trace an outward spiral that drifts
    toward the canvas center — mimicking dye advection by a vortex.
    """
    pts = []
    cx, cy = ox, oy
    angle = start_angle
    radius = 8
    for _ in range(12):
        angle += 0.55 + rng.uniform(-0.1, 0.1)
        radius += 14 + rng.uniform(-3, 3)
        # drift toward CX, CY
        tx = ox + math.cos(angle) * radius + (CX - ox) * 0.08
        ty = oy + math.sin(angle) * radius + (CY - oy) * 0.08
        # control points with random wobble
        c1x = cx + math.cos(angle - 0.4) * radius * 0.6 + rng.uniform(-10, 10)
        c1y = cy + math.sin(angle - 0.4) * radius * 0.6 + rng.uniform(-10, 10)
        c2x = tx - math.cos(angle) * 20 + rng.uniform(-10, 10)
        c2y = ty - math.sin(angle) * 20 + rng.uniform(-10, 10)
        pts.append(f'C {c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {tx:.1f},{ty:.1f}')
        cx, cy = tx, ty
    return f'M {ox:.1f},{oy:.1f} ' + ' '.join(pts)


def render():
    """Build and return the SVG document string."""
    rng = random.Random(SEED)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'<rect width="{W}" height="{H}" fill="#000000"/>',
    ]

    for color, (fx, fy) in COLORS:
        ox, oy = fx * W, fy * H
        base_angle = math.atan2(CY - oy, CX - ox)
        for i in range(18):
            angle = base_angle + rng.uniform(-math.pi * 0.6, math.pi * 0.6)
            opacity = rng.uniform(0.25, 0.75)
            width = rng.uniform(0.6, 2.2)
            path = spiral_path(ox + rng.uniform(-12, 12), oy + rng.uniform(-12, 12), angle, 2, rng)
            lines.append(
                f'<path d="{path}" fill="none" stroke="{color}" '
                f'stroke-width="{width:.1f}" stroke-opacity="{opacity:.2f}" '
                f'stroke-linecap="round"/>'
            )

    lines.append('</svg>')
    return '\n'.join(lines)


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(render())
    print(f'Written {out}')
