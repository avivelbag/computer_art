#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 113 — Murmuration: Three Rules and a Sky.

Writes a static 400×250 SVG with 100 boid glyphs at a fixed random seed,
matching the midnight-blue palette of the canvas animation.
"""
import math
import pathlib
import random

SEED = 42
W, H = 400, 250
N = 100


def boid_polygon(x, y, angle, size=5):
    """Return an SVG points string for a triangle boid facing *angle* (radians).

    The tip points in the direction of travel; the two base corners are placed
    at ±135° from the heading at 55% of *size* from the centroid.
    """
    tip = (x + math.cos(angle) * size, y + math.sin(angle) * size)
    lr = size * 0.55
    left = (x + math.cos(angle + math.pi * 0.75) * lr,
            y + math.sin(angle + math.pi * 0.75) * lr)
    right = (x + math.cos(angle - math.pi * 0.75) * lr,
             y + math.sin(angle - math.pi * 0.75) * lr)
    return (f"{tip[0]:.1f},{tip[1]:.1f} "
            f"{left[0]:.1f},{left[1]:.1f} "
            f"{right[0]:.1f},{right[1]:.1f}")


def render():
    """Build and return the SVG document string for the thumbnail."""
    rng = random.Random(SEED)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        '<defs>',
        '  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"'
        ' gradientUnits="objectBoundingBox">',
        '    <stop offset="0" stop-color="#0a0a2e"/>',
        '    <stop offset="1" stop-color="#1a0a28"/>',
        '  </linearGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
    ]
    for _ in range(N):
        x = rng.uniform(8, W - 8)
        y = rng.uniform(8, H - 8)
        angle = rng.uniform(0, math.pi * 2)
        pts = boid_polygon(x, y, angle)
        lines.append(f'  <polygon points="{pts}" fill="rgba(220,230,255,0.85)"/>')
    lines.append('</svg>')
    return '\n'.join(lines)


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(render())
    print(f'Written {out}')
