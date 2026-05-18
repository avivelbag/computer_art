#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 244-spirolaterals."""

import math
from pathlib import Path


def gcd(a, b):
    a, b = abs(int(round(a))), abs(int(round(b)))
    while b:
        a, b = b, a % b
    return a or 1


def closure_repeats(n, angle):
    mod = (n * angle) % 360
    if mod == 0:
        return 4
    return min(360 // gcd(mod, 360), 12)


def compute_points(seq, angle_deg, repeats):
    """Return all turtle vertex positions as (x, y) floats."""
    pts = [(0.0, 0.0)]
    x, y, direction = 0.0, 0.0, 0.0
    rad = math.pi / 180
    for _ in range(repeats):
        for length in seq:
            x += length * math.cos(direction * rad)
            y += length * math.sin(direction * rad)
            pts.append((x, y))
            direction = (direction + angle_deg) % 360
    return pts


def fit_points(pts, cx, cy, cell_w, cell_h, margin=0.82):
    """Scale and centre pts so their bounding box fits inside the cell."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    fw = max_x - min_x or 1.0
    fh = max_y - min_y or 1.0
    scale = min(cell_w * margin / fw, cell_h * margin / fh)
    ox = cx - (min_x + fw / 2) * scale
    oy = cy - (min_y + fh / 2) * scale
    return [(p[0] * scale + ox, p[1] * scale + oy) for p in pts]


FIGURES = [
    ([1, 2, 3],       90,  '#7fffd4'),
    ([1, 2],         144,  '#ffb3c1'),
    ([1, 2, 3, 4, 5], 90,  '#ffd700'),
    ([1, 2, 3, 4],   120,  '#c9a7ff'),
    ([1, 1, 2, 3, 5], 90,  '#7fffd4'),
    ([1, 2, 3, 4, 5, 6], 60, '#ffb3c1'),
    ([2, 3, 5],      120,  '#ffd700'),
    ([1, 3, 5],      120,  '#c9a7ff'),
    ([3, 2, 1],       90,  '#7fffd4'),
]

W, H = 400, 400
COLS, ROWS = 3, 3
CELL_W, CELL_H = W // COLS, H // ROWS

path_elements = []
for i, (seq, angle, color) in enumerate(FIGURES):
    if i >= COLS * ROWS:
        break
    col = i % COLS
    row = i // COLS
    cx = col * CELL_W + CELL_W // 2
    cy = row * CELL_H + CELL_H // 2
    repeats = closure_repeats(len(seq), angle)
    raw = compute_points(seq, angle, repeats)
    pts = fit_points(raw, cx, cy, CELL_W, CELL_H)

    d_parts = [f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for x, y in pts[1:]:
        d_parts.append(f"L {x:.1f},{y:.1f}")
    d = " ".join(d_parts)
    path_elements.append(
        f'  <path d="{d}" stroke="{color}" stroke-width="1.4"'
        f' fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    )

svg_lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"'
    f' viewBox="0 0 {W} {H}">',
    f'  <rect width="{W}" height="{H}" fill="#0d1117"/>',
]
svg_lines.extend(path_elements)
svg_lines.append('</svg>')
svg = "\n".join(svg_lines) + "\n"

out = Path(__file__).parent / "thumbnail.svg"
out.write_text(svg)
print(f"Written {out} ({len(svg)} bytes)")
